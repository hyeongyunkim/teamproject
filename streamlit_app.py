import streamlit as st
import os
import hashlib
import base64
import mimetypes
from datetime import datetime
import html
import json
import tempfile

from PIL import Image, ImageDraw

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

def load_org_id() -> str:
    org = None
    try:
        org = st.secrets.get("OPENAI_ORG_ID")
    except Exception:
        pass
    if not org:
        org = os.getenv("OPENAI_ORG_ID", "")
    return (org or "").strip()

OPENAI_API_KEY = load_api_key()
OPENAI_ORG_ID = load_org_id()
client = None
openai_import_error = None
if OPENAI_API_KEY:
    try:
        from openai import OpenAI  # pip install openai>=1.0.0
        if OPENAI_ORG_ID:
            client = OpenAI(api_key=OPENAI_API_KEY, organization=OPENAI_ORG_ID)
        else:
            client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        openai_import_error = e

# -------------------- 파일 유틸 --------------------
def list_uploaded_only():
    if not os.path.exists(UPLOAD_FOLDER):
        return []
    return sorted([f for f in os.listdir(UPLOAD_FOLDER)
                   if f.lower().endswith((".png", ".jpg", ".jpeg"))])

def list_converted_only():
    """변환본: PNG/JPG 모두, 최신순 정렬"""
    if not os.path.exists(CONVERTED_FOLDER):
        return []
    files = []
    for f in os.listdir(CONVERTED_FOLDER):
        if f.lower().endswith((".png", ".jpg", ".jpeg")):
            files.append(os.path.join(CONVERTED_FOLDER, f))
    files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return files

def img_file_to_data_uri(path: str) -> str:
    mime, _ = mimetypes.guess_type(path)
    if mime is None:
        mime = "image/png"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}"

def converted_stem(src_filename: str) -> str:
    base, _ = os.path.splitext(src_filename)
    return f"{base}__converted"

def converted_png_name(src_filename: str) -> str:
    return converted_stem(src_filename) + ".png"

# -------------------- 이미지 변환 (애니풍 / variations 우선 + edit 폴백) --------------------
def _save_temp_square_png(src_path: str, max_side: int = 1024) -> str:
    """원본 비율 유지 + 흰 배경 정사각 캔버스(1024)에 합성하여 PNG 임시 저장."""
    with Image.open(src_path) as im:
        im = im.convert("RGBA")
        scale = min(max_side / im.width, max_side / im.height, 1.0)
        new_w = int(im.width * scale)
        new_h = int(im.height * scale)
        im = im.resize((new_w, new_h), Image.LANCZOS)

        canvas = Image.new("RGBA", (max_side, max_side), (255, 255, 255, 255))
        x = (max_side - new_w) // 2
        y = (max_side - new_h) // 2
        canvas.paste(im, (x, y))

    t = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    canvas.save(t.name, "PNG")
    return t.name

def _make_frame_mask_rgba(size: int = 1024, border: int = 24):
    """images.edit 폴백용: 테두리(보존=불투명), 내부(편집=투명) 마스크"""
    m = Image.new("L", (size, size), 0)  # 0=편집
    d = ImageDraw.Draw(m)
    d.rectangle([0, 0, size-1, border-1], fill=255)                         # top
    d.rectangle([0, size-border, size-1, size-1], fill=255)                 # bottom
    d.rectangle([0, border, border-1, size-border-1], fill=255)             # left
    d.rectangle([size-border, border, size-1, size-border-1], fill=255)     # right
    return m.convert("RGBA")

# 일본 TV 애니 감성 프롬프트
_ANIME_PROMPT = (
    "High-quality Japanese TV anime illustration. Keep the SAME pose and composition as the input photo. "
    "Clean cel shading with 2–3 tones per color, hard shadows with clear shapes, flat high-saturation palette. "
    "Bold, clean black lineart with slight variable line weight (0.5–2.5px). "
    "Cute expressive eyes (species-appropriate), small/simple nose & mouth, subtle fur tufts and inner line details. "
    "Anime highlights on eyes/fur, crisp edges. "
    "Simple background without gradients: plain color, halftone dots, or speed lines. "
    "No photo textures, no blur, no noise, no text, no watermark, not photorealistic."
)

def ai_redraw_comic_style(img_path: str, out_path: str):
    """
    기본: images.variations로 원본 포즈/구도 보존하며 '일본 TV 애니' 스타일 변형.
    폴백: images.edit(+프레임 마스크)로 같은 스타일 재그리기.
    출력: .png로 저장.
    """
    if client is None:
        raise RuntimeError("OpenAI 클라이언트가 준비되지 않았습니다. (OPENAI_API_KEY/조직 인증 확인)")

    if not out_path.lower().endswith(".png"):
        out_path = os.path.splitext(out_path)[0] + ".png"

    tmp_img = None
    tmp_mask = None
    try:
        tmp_img = _save_temp_square_png(img_path, max_side=1024)

        # 1) variations 우선 시도 (원본 구도/실루엣 보존에 유리)
        try:
            with open(tmp_img, "rb") as f_img:
                try:
                    resp = client.images.variations(
                        model="gpt-image-1",
                        image=f_img,
                        n=1,
                        size="1024x1024",
                        prompt=_ANIME_PROMPT,
                    )
                except Exception:
                    # 일부 환경에서 variations가 prompt 인자를 거부 → 프롬프트 없이 변형
                    f_img.seek(0)
                    resp = client.images.variations(
                        model="gpt-image-1",
                        image=f_img,
                        n=1,
                        size="1024x1024",
                    )
        except Exception:
            # 2) 폴백: edit + 프레임 마스크(프레이밍 유지)
            mask = _make_frame_mask_rgba(size=1024, border=24)
            tmask = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            mask.save(tmask.name, "PNG")
            tmp_mask = tmask.name

            with open(tmp_img, "rb") as f_img, open(tmp_mask, "rb") as f_mask:
                resp = client.images.edit(
                    model="gpt-image-1",
                    image=f_img,
                    mask=f_mask,
                    size="1024x1024",
                    prompt=_ANIME_PROMPT,
                )

        # 결과 저장
        b64_img = resp.data[0].b64_json
        img_bytes = base64.b64decode(b64_img)
        with open(out_path, "wb") as out:
            out.write(img_bytes)

    finally:
        for p in (tmp_img, tmp_mask):
            try:
                if p and os.path.exists(p):
                    os.remove(p)
            except Exception:
                pass

# -------------------- 스타일(CSS) --------------------
st.markdown("""
<style>
:root{ --bg:#FDF6EC; --ink:#4B3832; --accent:#CFA18D; --accent-2:#FAE8D9; --line:#EED7CA;
--shadow:0 10px 24px rgba(79,56,50,0.12);}
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
  background:#fff; border:1px solid var(--line); box-shadow:0 2px 6px rgba(79,56,50,.05); color:#5A3E36; }
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
    st.caption(f"조직 ID: {OPENAI_ORG_ID or '(미지정)'}")

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
    # === 상단 일괄 변환 버튼 ===
    st.markdown("### 🚀 상단 일괄 AI 변환")
    if st.button("모든 미변환 원본을 '일본 TV 애니' 스타일로 변환하기"):
        if client is None:
            st.error("❌ OpenAI 준비가 안 되었습니다. (OPENAI_API_KEY/조직 인증 확인)")
        else:
            originals = list_uploaded_only()
            if not originals:
                st.info("업로드된 원본 사진이 없습니다.")
            else:
                existing_stems = {os.path.splitext(f)[0] for f in os.listdir(CONVERTED_FOLDER)}
                to_convert = [fn for fn in originals if converted_stem(fn) not in existing_stems]

                if not to_convert:
                    st.info("변환할 원본이 없습니다. (모두 이미 변환됨)")
                else:
                    progress = st.progress(0)
                    status = st.empty()
                    success = 0
                    failures = []
                    total = len(to_convert)

                    for i, fname in enumerate(to_convert, start=1):
                        in_path = os.path.join(UPLOAD_FOLDER, fname)
                        out_path = os.path.join(CONVERTED_FOLDER, converted_png_name(fname))
                        try:
                            status.write(f"변환 중 {i}/{total} : {html.escape(fname)}")
                            ai_redraw_comic_style(in_path, out_path)
                            success += 1
                        except Exception as e:
                            msg = str(e)
                            if "must be verified" in msg or "403" in msg:
                                msg = ("이미지 모델 접근 권한(조직 Verify/결제)이 필요합니다. "
                                       "https://platform.openai.com/settings/organization/general 에서 인증 후 재시도하세요.")
                            failures.append((fname, msg))
                        finally:
                            progress.progress(i / total)

                    if success:
                        st.success(f"✅ 변환 완료: {success}장")
                    if failures:
                        with st.expander(f"⚠️ 실패 {len(failures)}장 (자세히 보기)", expanded=True):
                            for fn, msg in failures:
                                st.error(f"{fn} → {msg}")
                        st.info("실패가 있어 자동 새로고침을 하지 않았습니다. 오류 확인 후 다시 시도해 주세요.")
                    else:
                        st.session_state.carousel_idx = 0
                        st.rerun()

    # 캐러셀 (변환본만)
    st.markdown("<h2 style='text-align:center;'>In Loving Memory</h2>", unsafe_allow_html=True)
    converted_list = list_converted_only()
    n = len(converted_list)

    if "carousel_idx" not in st.session_state:
        st.session_state.carousel_idx = 0

    if n == 0:
        st.info("현재 표시할 변환 이미지가 없습니다. 상단의 '일괄 AI 변환'을 사용하거나 변환본을 추가해 주세요.")
    else:
        st.session_state.carousel_idx = max(0, min(st.session_state.carousel_idx, n - 1))
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

    # -------------------- 온라인 추모관: 업로드만 + 원본 미리보기 --------------------
    st.subheader("🖼️ 온라인 추모관")

    with st.form("gallery_upload_only", clear_on_submit=True):
        uploaded_files = st.file_uploader(
            "사진 업로드 (PNG/JPG)", type=["png", "jpg", "jpeg"], accept_multiple_files=True
        )
        submit_upload = st.form_submit_button("업로드")

    if submit_upload:
        if not uploaded_files:
            st.warning("업로드할 파일을 선택해 주세요.")
        else:
            saved, dup, errs = 0, 0, 0
            existing = set(os.listdir(UPLOAD_FOLDER))
            for uf in uploaded_files:
                try:
                    data = uf.getvalue()
                    if not data:
                        errs += 1
                        continue
                    digest = hashlib.sha256(data).hexdigest()[:16]
                    safe_name = "".join(c for c in uf.name if c not in "\\/:*?\"<>|")
                    filename = f"{digest}_{safe_name}"
                    if any(name.startswith(digest + "_") for name in existing):
                        dup += 1
                        continue
                    with open(os.path.join(UPLOAD_FOLDER, filename), "wb") as f:
                        f.write(data)
                    saved += 1
                    existing.add(filename)
                except Exception as e:
                    errs += 1
                    st.error(f"업로드 실패({uf.name}): {e}")

            if saved: st.success(f"✅ {saved}장 업로드 완료!")
            if dup:   st.info(f"ℹ️ 중복으로 제외된 사진: {dup}장")
            if errs:  st.warning(f"⚠️ 저장 중 오류: {errs}장")
            st.rerun()

    # 업로드된 원본 미리보기 (3열 그리드)
    originals = list_uploaded_only()
    if originals:
        st.caption(f"📂 업로드된 원본: {len(originals)}장")
        for i in range(0, len(originals), 3):
            cols = st.columns(3, gap="medium")
            for j, fname in enumerate(originals[i:i+3]):
                path = os.path.join(UPLOAD_FOLDER, fname)
                with cols[j]:
                    try:
                        data_uri = img_file_to_data_uri(path)
                        st.markdown(f"""
                        <div class="frame-card">
                          <div class="frame-edge">
                            <img class="square-thumb" src="{data_uri}" alt="{html.escape(fname)}"/>
                          </div>
                          <div class="frame-meta">{html.escape(fname)}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button("삭제", key=f"del_origin_{i+j}"):
                            try:
                                os.remove(path)
                                # 변환본도 스템 기준으로 함께 제거
                                stem = converted_stem(fname)
                                for cf in list(os.listdir(CONVERTED_FOLDER)):
                                    if os.path.splitext(cf)[0] == stem:
                                        os.remove(os.path.join(CONVERTED_FOLDER, cf))
                                st.success("삭제되었습니다.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"삭제 실패: {e}")
                    except Exception as e:
                        st.error(f"미리보기 실패({fname}): {e}")
    else:
        st.info("아직 업로드된 사진이 없습니다. 위에서 파일을 업로드하세요.")

# ====== 탭2: 스트리밍 ======
with tab2:
    st.header("📺 장례식 실시간 스트리밍")
    video_url = st.text_input("YouTube 영상 URL 입력", "https://www.youtube.com/embed/dQw4w9WgXcQ")
    st.markdown(
        f"<div style='text-align:center;'><iframe width='560' height='315' src='{video_url}' frameborder='0' allowfullscreen></iframe></div>",
        unsafe_allow_html=True
    )
