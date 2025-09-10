import streamlit as st
import os
import hashlib
import base64
import mimetypes
from datetime import datetime
import html
import json

# --- 로컬 지브리 변환용 ---
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance, ImageOps, ImageChops

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
        from openai import OpenAI  # pip install openai
        client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        openai_import_error = e

# -------------------- 유틸 --------------------
def list_all_images_for_carousel():
    files = []
    for folder in [UPLOAD_FOLDER, CONVERTED_FOLDER]:
        if os.path.exists(folder):
            files += [
                os.path.join(folder, f)
                for f in os.listdir(folder)
                if f.lower().endswith((".png", ".jpg", ".jpeg"))
            ]
    return sorted(files)

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

def safe_remove(path: str) -> bool:
    try:
        if os.path.exists(path):
            os.remove(path)
            return True
        return False
    except Exception:
        return False

# 대용량 이미지 자동 리사이즈 (변환 전)
def maybe_resize(path: str, max_side=1600):
    try:
        img = Image.open(path).convert("RGB")
        w, h = img.size
        if max(w, h) > max_side:
            scale = max_side / max(w, h)
            img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
            img.save(path)  # 덮어쓰기
    except Exception:
        pass

# -------------------- 빠른 지브리풍 로컬 변환 --------------------
def local_ghibli_filter(in_path: str, out_path: str,
                        *, posterize_bits=4, edge_blur=1, glow=1.3):
    """
    빠른 지브리풍:
    - 포스터라이즈(색 단계 축소)
    - FIND_EDGES 기반 윤곽선 추출 후 농도 보정
    - 파스텔/따뜻한 톤 + 소프트 글로우
    - 순수 Pillow 연산(루프 없음)이라 속도 빠름
    """
    img = Image.open(in_path).convert("RGB")
    w, h = img.size

    # 1) 부드럽게 + 채도/밝기 소폭 업
    base = img.filter(ImageFilter.MedianFilter(3))
    base = ImageEnhance.Color(base).enhance(1.15)
    base = ImageEnhance.Brightness(base).enhance(1.05)

    # 2) 포스터라이즈(만화 느낌)
    base = ImageOps.posterize(base, bits=posterize_bits)

    # 3) 윤곽선 (빠른 방식)
    edge = img.convert("L").filter(ImageFilter.FIND_EDGES)
    if edge_blur > 0:
        edge = edge.filter(ImageFilter.GaussianBlur(edge_blur))
    # 선을 더 진하게: 밝기/대비 조절
    edge = ImageEnhance.Contrast(edge).enhance(2.0)
    edge = ImageEnhance.Brightness(edge).enhance(0.5)  # 어둡게 → 검은 선
    edge_rgb = ImageOps.invert(edge).convert("RGB")     # 흑선

    # 4) 윤곽선 Multiply 합성
    merged = ImageChops.multiply(base, edge_rgb)

    # 5) 파스텔/따뜻한 톤 + 글로우
    merged = ImageEnhance.Color(merged).enhance(1.08)
    warm = Image.new("RGB", merged.size, (255, 230, 205))
    merged = Image.blend(merged, warm, alpha=0.06)
    if glow > 0:
        blur = merged.filter(ImageFilter.GaussianBlur(radius=glow))
        merged = Image.blend(merged, blur, alpha=0.10)

    # 6) 엽서 느낌 테두리
    border = 8
    framed = Image.new("RGB", (w + border*2, h + border*2), (243, 226, 216))
    framed.paste(merged, (border, border))
    framed.save(out_path, format="PNG")

# -------------------- AI 지브리 변환 (OpenAI 시도→403/키없음 시 로컬 폴백) --------------------
def ai_convert_cute_memorial(img_path: str, out_path: str):
    """
    고정 지브리풍:
      - OpenAI(gpt-image-1) 편집 지브리 프롬프트 시도
      - 403/권한 문제 또는 키 미설정/클라이언트 실패면 로컬 지브리 폴백
    """
    # 키/클라이언트 없으면 바로 로컬
    if client is None:
        local_ghibli_filter(img_path, out_path)
        return

    prompt = (
        "Studio Ghibli style, hand-painted watercolor background, soft cel-shading, "
        "warm pastel palette, gentle bloom, subtle film grain, clean black outlines, "
        "storybook illustration look. Keep subject cute and serene."
    )
    try:
        with open(img_path, "rb") as f:
            resp = client.images.edit(
                model="gpt-image-1",
                image=f,
                prompt=prompt,
                size="1024x1024",
            )
        b64_img = resp.data[0].b64_json
        img_bytes = base64.b64decode(b64_img)
        with open(out_path, "wb") as out:
            out.write(img_bytes)
    except Exception as e:
        msg = str(e)
        # 조직 인증/권한 문제 등은 자동 폴백
        if ("403" in msg) or ("must be verified" in msg) or ("access" in msg.lower()):
            local_ghibli_filter(img_path, out_path)
        else:
            raise

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

# -------------------- 상단 고정 바 --------------------
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

# (임시) 진단 패널 - 필요 없으면 제거해도 됩니다
with st.sidebar.expander("🔎 진단(임시)"):
    st.write("OpenAI 클라이언트:", "OK" if client else "없음(로컬 지브리 사용)")
    st.write("원본/변환 이미지 수:", len(list_uploaded_only()), len(list_converted_only()))
    if OPENAI_API_KEY:
        masked = OPENAI_API_KEY[:7] + "..." + OPENAI_API_KEY[-4:]
        st.caption(f"키 지문: {masked}")
    else:
        st.caption("OpenAI 키 없음")

# -------------------- 히어로 --------------------
try:
    with open("guestbook.txt", "r", encoding="utf-8") as f:
        guest_lines = [ln for ln in f.readlines() if ln.strip()]
except FileNotFoundError:
    guest_lines = []

photo_count = len(list_all_images_for_carousel())
message_count = len(guest_lines)

st.markdown(f"""
<div class="hero">
  <div class="hero-grid">
    <div>
      <div class="hero-logo">🐾 Pet Memorialization 🐾</div>
      <div class="tagline">소중한 반려동물을 추모하는 공간</div>
      <div class="badges">
        <span class="badge"><span class="dot"></span> 사진 {photo_count}장</span>
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
tab1, tab2, tab3 = st.tabs(["📜 부고장/방명록/추모관", "📺 장례식 스트리밍", "💐 기부/꽃바구니"])

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
        prev, mid, nxt = st.columns([1,6,1])
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
        st.info("아직 변환된 사진이 없습니다. 아래 ‘온라인 추모관’에서 업로드 후 ‘AI 변환’ 또는 ‘모두 AI 변환’을 눌러 주세요.")

    # 부고장
    st.subheader("📜 부고장")
    safe_name = html.escape((pet_name or "").strip() or default_name)
    st.markdown(f"""
    <div style="text-align:center; background-color:#FAE8D9; padding:15px; border-radius:15px; margin:10px;">
      사랑하는 <b>{safe_name}</b> 이(가) 무지개다리를 건넜습니다.<br>
      함께한 시간들을 기억하며 따뜻한 마음으로 추모해주세요.<br><br>
      🐾 <b>태어난 날:</b> {birth_date.isoformat()} <br>
      🌈 <b>무지개다리 건넌 날:</b> {pass_date.isoformat()}
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
            col_msg, col_btn = st.columns([6,1])
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
                            <span class="guest-time" style="color:#9B8F88;font-size:12px;margin-left:6px;">· {safe_time}</span>
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
                        st.write
                        f.writelines(guest_lines)
                    st.rerun()
    else:
        st.info("아직 등록된 메시지가 없습니다.")

    # 온라인 추모관 — 업로드
    st.subheader("🖼️ 온라인 추모관")
    with st.form("gallery_upload", clear_on_submit=True):
        uploaded_files = st.file_uploader("사진 업로드", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
        submit = st.form_submit_button("업로드")
    if submit and uploaded_files:
        saved, dup = 0, 0
        for uploaded_file in uploaded_files:
            data = uploaded_file.getvalue()
            digest = hashlib.sha256(data).hexdigest()[:16]
            if any(f.startswith(digest + "_") for f in os.listdir(UPLOAD_FOLDER)):
                dup += 1
                continue
            safe_name_file = "".join(c for c in uploaded_file.name if c not in "\\/:*?\"<>|")
            filename = f"{digest}_{safe_name_file}"
            with open(os.path.join(UPLOAD_FOLDER, filename), "wb") as f:
                f.write(data)
            saved += 1
        if saved: st.success(f"{saved}장 업로드 완료!")
        if dup: st.info(f"중복으로 제외된 사진: {dup}장")
        st.rerun()

    # 모두 AI 변환 (지브리 고정 / OpenAI→403 시 로컬 지브리 폴백)
    st.caption("💡 ‘모두 AI 변환’을 누르면 미변환 원본만 지브리풍으로 일괄 변환합니다.")
    if st.button("모두 AI 변환"):
        try:
            originals_for_bulk = list_uploaded_only()
            converted_names = set(os.listdir(CONVERTED_FOLDER)) if os.path.exists(CONVERTED_FOLDER) else set()
            done, skipped = 0, 0
            for img_file in originals_for_bulk:
                out_name = f"converted_{img_file}"
                if out_name in converted_names:
                    skipped += 1
                    continue
                in_path = os.path.join(UPLOAD_FOLDER, img_file)
                out_path = os.path.join(CONVERTED_FOLDER, out_name)
                maybe_resize(in_path, max_side=1600)
                ai_convert_cute_memorial(in_path, out_path)
                done += 1
            st.success(f"변환 완료: {done}장 (이미 변환되어 건너뜀: {skipped}장)")
            st.rerun()
        except Exception as e:
            st.error(f"일괄 변환 실패: {e}")

    # 온라인 추모관 — 목록(3열 액자 그리드, 삭제/AI 변환)
    originals = list_uploaded_only()
    if originals:
        for row_start in range(0, len(originals), 3):
            row_files = originals[row_start:row_start+3]
            cols = st.columns(3, gap="medium")
            for j, img_file in enumerate(row_files):
                idx = row_start + j
                img_path = os.path.join(UPLOAD_FOLDER, img_file)
                with cols[j]:
                    data_uri = img_file_to_data_uri(img_path)
                    st.markdown(
                        f"""
                        <div class="frame-card">
                          <div class="frame-edge">
                            <img class="square-thumb" src="{data_uri}" alt="{html.escape(img_file)}"/>
                          </div>
                          <div class="frame-meta">{html.escape(img_file)}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    b1, b2 = st.columns(2)
                    with b1:
                        if st.button("AI 변환", key=f"convert_{idx}"):
                            try:
                                out_path = os.path.join(CONVERTED_FOLDER, f"converted_{img_file}")
                                maybe_resize(img_path, max_side=1600)
                                ai_convert_cute_memorial(img_path, out_path)
                                st.success("변환 완료! 위 캐러셀에서도 볼 수 있어요.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"변환 실패: {e}")
                    with b2:
                        if st.button("삭제", key=f"delete_{idx}"):
                            ok1 = safe_remove(img_path)
                            conv_candidate = os.path.join(CONVERTED_FOLDER, f"converted_{img_file}")
                            ok2 = safe_remove(conv_candidate)
                            st.success("사진이 삭제되었습니다." if (ok1 or ok2) else "삭제할 파일을 찾지 못했어요.")
                            st.rerun()
    else:
        st.info("아직 업로드된 사진이 없습니다.")

# ====== 탭2: 스트리밍 ======
with tab2:
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
    st.header("📺 장례식 실시간 스트리밍")
    video_url = st.text_input("YouTube 영상 URL 입력", "https://www.youtube.com/embed/dQw4w9WgXcQ")
    st.markdown(
        f"<div style='text-align:center;'><iframe width='560' height='315' src='{video_url}' frameborder='0' allowfullscreen></iframe></div>",
        unsafe_allow_html=True
    )

# ====== 탭3: 기부/꽃바구니 ======
with tab3:
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
    st.header("💐 조문객 기부 / 꽃바구니 주문")
    st.markdown("- 💳 기부: 카카오페이 / 토스 / 계좌이체 가능\n- 🌹 꽃바구니 주문: 온라인 꽃집 링크 연결")
    link = st.text_input("꽃바구니 주문 링크", "https://www.naver.com")
    st.markdown(
        f"<div style='text-align:center;'><a href='{link}' target='_blank' "
        f"style='font-size:18px; color:#CFA18D; font-weight:bold;'>👉 꽃바구니 주문하러 가기</a></div>",
        unsafe_allow_html=True
    )
