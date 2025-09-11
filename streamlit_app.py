import streamlit as st
import os
import hashlib
import base64
import mimetypes
from datetime import datetime
import html
import json
import tempfile

from PIL import Image
from io import BytesIO

# -------------------- 기본 설정 --------------------
st.set_page_config(page_title="반려동물 추모관", page_icon="🐾", layout="wide")

UPLOAD_FOLDER = "uploaded_images"
CONVERTED_FOLDER = "converted_images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

BASE_IMG_URL = "https://github.com/hyeongyunkim/teamproject/raw/main/petfuneral.png"
INFO_PATH = "memorial_info.json"

# -------------------- OpenAI 설정 --------------------
def load_api_key() -> str:
    key = None
    try:
        key = st.secrets.get("OPENAI_API_KEY")
    except Exception:
        pass
    if not key:
        key = os.getenv("OPENAI_API_KEY", "")
    return (key or "").strip()

OPENAI_API_KEY = load_api_key()
client = None
openai_import_error = None
if OPENAI_API_KEY:
    try:
        from openai import OpenAI  # pip install openai>=1.0.0
        client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        openai_import_error = e

# -------------------- 유틸 --------------------
def list_uploaded_only():
    if not os.path.exists(UPLOAD_FOLDER):
        return []
    return sorted([
        f for f in os.listdir(UPLOAD_FOLDER)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ])

def list_converted_only():
    if not os.path.exists(CONVERTED_FOLDER):
        return []
    return sorted([
        os.path.join(CONVERTED_FOLDER, f)
        for f in os.listdir(CONVERTED_FOLDER)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ])

def img_file_to_data_uri(path: str) -> str:
    mime, _ = mimetypes.guess_type(path)
    if mime is None:
        mime = "image/jpeg"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}"

# -------------------- 강한 만화책 리드로잉 프롬프트 --------------------
COMIC_PROMPT = (
    "FULL RE-ILLUSTRATION of the pet photo in EXTREME COMIC/MANGA style. "
    "Use the original only as pose/silhouette reference. Completely redraw as if hand-drawn. "
    "Strong bold black ink lines, thick clean outlines; high-contrast cel shading (2-3 tones only). "
    "Flat, high-saturation colors. Halftone screen tones for shadows/background. "
    "Cartoon exaggeration of features (cute but bold). Stylized simple background (white/flat/halftone). "
    "No gradients, no blur, no photo textures, no realism. "
    "Looks like a printed Japanese manga page. "
    "Style inspiration: 1990s Japanese manga such as Dragon Ball or Sailor Moon."
)

# -------------------- 전처리 + 임시 PNG 마스크로 안정적 edit --------------------
def ai_redraw_comic_style(img_path: str, out_path: str):
    """
    - 입력 이미지를 흑백 + 축소(최대 768)로 전처리 → 사진 질감 영향 최소화
    - 정사각 768 캔버스 중앙 정렬 (비율 보정)
    - 전영역 편집용 완전 투명 마스크 생성
    - 마스크/이미지를 임시 PNG 파일로 저장해서 client.images.edit 호출 (안정성↑)
    """
    if client is None:
        if not OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY가 설정되어 있지 않습니다.")
        if openai_import_error:
            raise RuntimeError(f"openai 라이브러리 문제: {openai_import_error}")
        raise RuntimeError("OpenAI 클라이언트 초기화 실패")

    # 1) 입력 전처리: 흑백 + 축소(최대 768), 정사각 캔버스에 중앙 배치
    with Image.open(img_path) as im:
        im = im.convert("L")  # grayscale
        im.thumbnail((768, 768), Image.LANCZOS)
        canvas = Image.new("L", (768, 768), 255)
        x = (768 - im.width) // 2
        y = (768 - im.height) // 2
        canvas.paste(im, (x, y))
        preprocessed = canvas.convert("RGBA")

    # 2) 전영역 편집용 완전 투명 마스크 (768x768)
    mask_img = Image.new("RGBA", (768, 768), (0, 0, 0, 0))

    tmp_img_path = None
    tmp_mask_path = None
    try:
        # 임시 파일(PNG)로 저장
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as t_img:
            preprocessed.save(t_img.name, "PNG")
            tmp_img_path = t_img.name

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as t_mask:
            mask_img.save(t_mask.name, "PNG")
            tmp_mask_path = t_mask.name

        # 3) OpenAI image edit
        with open(tmp_img_path, "rb") as f_img, open(tmp_mask_path, "rb") as f_mask:
            resp = client.images.edit(
                model="gpt-image-1",
                image=f_img,
                mask=f_mask,
                prompt=COMIC_PROMPT,
                size="1024x1024",
            )

        b64_img = resp.data[0].b64_json
        img_bytes = base64.b64decode(b64_img)
        with open(out_path, "wb") as out:
            out.write(img_bytes)

    finally:
        for p in (tmp_img_path, tmp_mask_path):
            try:
                if p and os.path.exists(p):
                    os.remove(p)
            except Exception:
                pass

# -------------------- 스타일(CSS) --------------------
st.markdown("""
<style>
:root{
  --bg:#FDF6EC; --ink:#4B3832; --accent:#CFA18D; --accent-2:#FAE8D9; --line:#EED7CA;
  --shadow:0 10px 24px rgba(79,56,50,0.12);
}
body { background-color: var(--bg); color: var(--ink); }
.page-wrap{ max-width:1180px; margin:0 auto; }
.topbar-fixed { position:fixed; top:0; left:0; right:0; height:60px;
  background:#FAE8D9; border-bottom:1px solid var(--line);
  display:flex; align-items:center; padding:0 24px; z-index:1000; }
.topbar-fixed .brand { font-size:28px; font-weight:900; color:#4B3832; }
.main-block { margin-top:74px; }
.hero{ background:linear-gradient(180deg,#FFF7F2 0%,#FFEFE6 100%);
  border:1px solid var(--line); border-radius:24px; box-shadow:var(--shadow); padding:17px 32px; }
.hero-grid{ display:grid; grid-template-columns:1.6fr .9fr; gap:28px; align-items:center; }
.hero-logo{ font-size:26px; font-weight:900; color:#4B3832; }
.tagline{ font-size:18px; color:#6C5149; margin-bottom:14px; }
.badges{ display:flex; gap:10px; flex-wrap:wrap; }
.badge{ padding:6px 10px; border-radius:999px; font-weight:700; font-size:13px;
  background:#fff; border:1px solid var(--line); box-shadow:0 2px 8px rgba(79,56,50,.05); color:#5A3E36; }
.badge .dot{ width:8px; height:8px; border-radius:50%; background: var(--accent); }
.hero-visual .kv img{ width:50%; display:block; }
.photo-frame{ background:#fff; border:6px solid #F3E2D8; box-shadow:0 8px 18px rgba(79,56,50,0.12);
  border-radius:16px; padding:10px; margin-bottom:12px; }
.photo-frame .thumb{ width:70%; display:block; border-radius:10px; margin:0 auto; }
.guest-card{ background:linear-gradient(180deg,#FFF8F1 0%,#FFFFFF 100%);
  border:1px solid var(--line); border-left:6px solid var(--accent); border-radius:14px;
  padding:14px 16px; margin:10px 0 16px; box-shadow:0 4px 10px rgba(79,56,50,0.08); }
.stTabs [role="tablist"]{ justify-content:center !important; gap:12px !important; }
.frame-card{ background:#fff; border:6px solid #F3E2D8; border-radius:16px;
  box-shadow:0 8px 18px rgba(79,56,50,0.12); padding:10px; margin-bottom:16px; }
.frame-edge{ background:#FFFFFF; border:1px solid var(--line); border-radius:12px; padding:8px; }
.square-thumb{ width:100%; aspect-ratio:1/1; object-fit:cover; display:block; border-radius:10px; }
.frame-meta{ color:#6C5149; font-size:12px; margin-top:8px; text-align:center; opacity:.9; }
</style>
""", unsafe_allow_html=True)

# -------------------- 상단 바 --------------------
st.markdown("""<div class="topbar-fixed"><div class="brand">🐾 Pet Memorialization 🐾</div></div>""", unsafe_allow_html=True)
st.markdown('<div class="main-block">', unsafe_allow_html=True)

# -------------------- 부고 정보 --------------------
default_name = "초코"
default_birth = datetime(2015, 3, 15).date()
default_pass  = datetime(2024, 8, 10).date()

if os.path.exists(INFO_PATH):
    try:
        with open(INFO_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            default_name = data.get("name", default_name)
            if data.get("birth"): default_birth = datetime.strptime(data["birth"], "%Y-%m-%d").date()
            if data.get("pass"):  default_pass  = datetime.strptime(data["pass"], "%Y-%m-%d").date()
    except Exception:
        pass

st.sidebar.title("📜 부고 정보 입력")
pet_name = st.sidebar.text_input("반려동물 이름", value=default_name)
birth_date = st.sidebar.date_input("태어난 날", value=default_birth)
pass_date = st.sidebar.date_input("무지개다리 건넌 날", value=default_pass)

if st.sidebar.button("저장하기"):
    with open(INFO_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "name": (pet_name or "").strip() or default_name,
            "birth": birth_date.isoformat(),
            "pass":  pass_date.isoformat()
        }, f, ensure_ascii=False, indent=2)
    st.sidebar.success("저장 완료!")
    st.rerun()

with st.sidebar.expander("🔎 상태"):
    st.write("OpenAI 클라이언트:", "OK" if client else ("오류" if openai_import_error else "없음"))
    if OPENAI_API_KEY:
        masked = OPENAI_API_KEY[:7] + "..." + OPENAI_API_KEY[-4:]
        st.caption(f"키 지문: {masked}")
    else:
        st.caption("OPENAI_API_KEY 미설정")

# -------------------- 히어로 --------------------
try:
    with open("guestbook.txt", "r", encoding="utf-8") as f:
        guest_lines = [ln for ln in f.readlines() if ln.strip()]
except FileNotFoundError:
    guest_lines = []

def list_for_badge():
    return len(list_converted_only()), len(guest_lines)

photo_count, message_count = list_for_badge()

st.markdown(f"""
<div class="hero">
  <div class="hero-grid">
    <div>
      <div class="hero-logo">🐾 Pet Memorialization 🐾</div>
      <div class="tagline">소중한 반려동물을 추모하는 공간</div>
      <div class="badges">
        <span class="badge"><span class="dot"></span> 변환 사진 {photo_count}장</span>
        <span class="badge"><span class="dot"></span> 방명록 {message_count}개</span>
      </div>
    </div>
    <div class="hero-visual">
      <div class="kv">
        <img src="{BASE_IMG_URL}" alt="memorial">
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# -------------------- 탭 --------------------
tab1, tab2 = st.tabs(["📜 부고장/방명록/추모관", "📺 장례식 스트리밍"])

# ====== 탭1 ======
with tab1:
    # 캐러셀 (변환본만)
    st.markdown("<h2 style='text-align:center;'>In Loving Memory</h2>", unsafe_allow_html=True)
    converted_list = list_converted_only()
    n = len(converted_list)

    if "carousel_idx" not in st.session_state:
        st.session_state.carousel_idx = 0

    if n > 0:
        st.session_state.carousel_idx %= n
        prev, mid, nxt = st.columns([1, 6, 1])
        with prev:
            if st.button("◀", key="carousel_prev"):
                st.session_state.carousel_idx = (st.session_state.carousel_idx - 1) % n
        with mid:
            current = converted_list[st.session_state.carousel_idx]
            data_uri = img_file_to_data_uri(current)
            st.markdown(f"""
            <div class="photo-frame" style="max-width:720px;margin:0 auto 10px;">
                <img class="thumb" src="{data_uri}">
            </div>
            """, unsafe_allow_html=True)
            st.markdown(
                f"<p style='text-align:center;'><b>{st.session_state.carousel_idx+1}/{n}</b></p>",
                unsafe_allow_html=True
            )
        with nxt:
            if st.button("▶", key="carousel_next"):
                st.session_state.carousel_idx = (st.session_state.carousel_idx + 1) % n
    else:
        st.info("아직 변환된 사진이 없습니다. 아래 '온라인 추모관'에서 업로드 후 ‘모두 AI 변환’을 눌러주세요.")

    # 부고장
    st.subheader("📜 부고장")
    safe_name = html.escape((pet_name or "").strip() or default_name)
    st.markdown(f"""
    <div style="text-align:center; background-color:#FAE8D9; padding:15px; border-radius:15px; margin:10px;">
      사랑하는 <b>{safe_name}</b> 이(가) 무지개다리를 건넜습니다.<br>
      함께한 시간들을 기억하며 따뜻한 마음으로 추모해주세요.<br><br>
      🐾 <b>태어난 날:</b> {default_birth.isoformat()} <br>
      🌈 <b>무지개다리 건넌 날:</b> {default_pass.isoformat()}
    </div>
    """, unsafe_allow_html=True)

    # 방명록 작성
    st.subheader("✍️ 방명록")
    name = st.text_input("이름")
    message = st.text_area("메시지")
    if st.button("추모 메시지 남기기"):
        if name and message:
            with open("guestbook.txt", "a", encoding="utf-8") as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|{name}|{message}\n")
            st.success("메시지가 등록되었습니다.")
            st.rerun()
        else:
            st.warning("이름과 메시지를 입력해주세요.")

    # 방명록 모음
    st.subheader("📖 추모 메시지 모음")
    try:
        with open("guestbook.txt", "r", encoding="utf-8") as f:
            guest_lines = [ln for ln in f.readlines() if ln.strip()]
    except FileNotFoundError:
        guest_lines = []

    if guest_lines:
        for idx, line in enumerate(reversed(guest_lines)):
            try:
                time_str, user, msg = line.strip().split("|", 2)
            except Exception:
                continue
            col_msg, col_btn = st.columns([6, 1])
            with col_msg:
                safe_user = html.escape(user)
                safe_time = html.escape(time_str)
                safe_msg = html.escape(msg).replace("\n", "<br>")
                st.markdown(f"""
                <div class="guest-card">
                    <div class="guest-card-header" style="display:flex; gap:12px; align-items:center; margin-bottom:6px;">
                        <div class="guest-avatar" style="width:36px;height:36px;border-radius:50%;
                             display:flex;align-items:center;justify-content:center;background:#FAE8D9;
                             color:#6C5149;font-weight:700;box-shadow:0 2px 6px rgba(79,56,50,0.05);">🕊️</div>
                        <div class="guest-name-time">
                            <span class="guest-name" style="color:#4B3832;font-weight:700;">{safe_user}</span>
                            <span class="guest-time" style="color:#9B8F88; font-size:12px; margin-left:6px;">· {safe_time}</span>
                        </div>
                    </div>
                    <div class="guest-msg" style="margin-top:6px;padding:10px 12px;background:#FFF4ED;
                         border:1px dashed #F0E0D7;border-radius:12px;color:#5A3E36;line-height:1.6;">
                        {safe_msg}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col_btn:
                if st.button("삭제", key=f"del_msg_{idx}"):
                    real_idx = len(guest_lines) - 1 - idx
                    del guest_lines[real_idx]
                    with open("guestbook.txt", "w", encoding="utf-8") as f:
                        f.writelines(guest_lines)
                    st.rerun()
    else:
        st.info("아직 등록된 메시지가 없습니다.")

    # -------------------- 온라인 추모관: 업로드만 --------------------
    st.subheader("🖼️ 온라인 추모관")
    with st.form("gallery_upload_only", clear_on_submit=True):
        uploaded_files = st.file_uploader("사진 업로드", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
        submit_upload = st.form_submit_button("업로드")  # ✅ 업로드 전용 버튼

    if submit_upload and uploaded_files:
        saved, dup = 0, 0
        for uploaded_file in uploaded_files:
            data = uploaded_file.getvalue()
            digest = hashlib.sha256(data).hexdigest()[:16]
            if any(f.startswith(digest + "_") for f in os.listdir(UPLOAD_FOLDER)):
                dup += 1
                continue
            safe_name_file = "".join(c for c in uploaded_file.name if c not in "\\/:*?\"<>|")
            filename = f"{digest}_{safe_name_file}"
            in_path = os.path.join(UPLOAD_FOLDER, filename)
            with open(in_path, "wb") as f:
                f.write(data)
            saved += 1

        if saved: st.success(f"{saved}장 업로드 완료! 아래 ‘모두 AI 변환’을 눌러 만화풍으로 변환하세요.")
        if dup: st.info(f"중복으로 제외된 사진: {dup}장")
        st.rerun()

    st.caption("💡 업로드만 먼저 하고, 아래 ‘모두 AI 변환’ 버튼으로 일괄 변환할 수 있어요.")

    # -------------------- 모두 AI 변환 (미변환 원본만) --------------------
    st.caption("💡 '모두 AI 변환'을 누르면 미변환 원본만 **만화책 리드로잉**으로 일괄 변환합니다. (OpenAI 전용)")
    if st.button("모두 AI 변환"):
        if client is None:
            st.error("❌ OpenAI가 준비되지 않았습니다. (Secrets/환경변수의 OPENAI_API_KEY와 조직 인증을 확인하세요.)")
        else:
            originals_for_bulk = list_uploaded_only()
            if not originals_for_bulk:
                st.info("업로드된 원본 사진이 없습니다.")
            else:
                converted_names = set(os.listdir(CONVERTED_FOLDER)) if os.path.exists(CONVERTED_FOLDER) else set()
                to_convert = []
                for img_file in originals_for_bulk:
                    out_name = f"converted_{img_file}"
                    if out_name not in converted_names:
                        to_convert.append(img_file)

                if not to_convert:
                    st.info("변환할 원본이 없습니다. (모두 이미 변환됨)")
                else:
                    progress = st.progress(0)
                    status = st.empty()
                    done, failed = 0, 0
                    total = len(to_convert)

                    for i, img_file in enumerate(to_convert, start=1):
                        in_path  = os.path.join(UPLOAD_FOLDER, img_file)
                        out_name = f"converted_{img_file}"
                        out_path = os.path.join(CONVERTED_FOLDER, out_name)
                        try:
                            status.write(f"변환 중 {i}/{total} : {html.escape(img_file)}")
                            ai_redraw_comic_style(in_path, out_path)
                            done += 1
                        except Exception as e:
                            failed += 1
                            st.error(f"⚠️ {img_file} 변환 실패: {e}")
                        finally:
                            progress.progress(i / total)

                    if done:
                        st.success(f"변환 완료: {done}장" + (f" · 실패 {failed}장" if failed else ""))
                    else:
                        st.error("변환에 실패했습니다. (오류 메시지를 확인해 주세요)")

                    st.rerun()

# ====== 탭2: 스트리밍 ======
with tab2:
    st.header("📺 장례식 실시간 스트리밍")
    video_url = st.text_input("YouTube 영상 URL 입력", "https://www.youtube.com/embed/dQw4w9WgXcQ")
    st.markdown(
        f"<div style='text-align:center;'><iframe width='560' height='315' src='{video_url}' frameborder='0' allowfullscreen></iframe></div>",
        unsafe_allow_html=True
    )
