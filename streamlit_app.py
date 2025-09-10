import streamlit as st
import os
import hashlib
import base64
import mimetypes
from datetime import datetime
import html
import json

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

# -------------------- 강한 만화책 리드로잉 프롬프트 --------------------
COMIC_PROMPT = (
    "FULL RE-ILLUSTRATION of the pet photo in EXTREME COMIC/MANGA style. "
    "Use the original only as pose/silhouette reference. Completely redraw as if hand-drawn. "
    "Strong bold black ink lines, thick outlines, high-contrast cel shading (2-3 tones only). "
    "Flat, high-saturation colors. Halftone screen tones for shadows and backgrounds. "
    "Cartoon exaggeration of features (cute but bold). "
    "No gradients, no blur, no photo textures, no realism. "
    "Looks like a printed Japanese manga page. "
    "Style inspiration: 1990s Japanese manga such as Dragon Ball or Sailor Moon."
)

# -------------------- 전체 투명 마스크 생성 --------------------
def make_full_transparent_mask_bytes(w: int, h: int) -> bytes:
    mask = Image.new("RGBA", (w, h), (0, 0, 0, 0))  # 완전 투명
    buf = BytesIO()
    mask.save(buf, format="PNG")
    return buf.getvalue()

# -------------------- OpenAI: 리드로잉 --------------------
def ai_redraw_comic_style(img_path: str, out_path: str):
    if client is None:
        if not OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY가 설정되어 있지 않습니다.")
        if openai_import_error:
            raise RuntimeError(f"openai 라이브러리 문제: {openai_import_error}")
        raise RuntimeError("OpenAI 클라이언트 초기화 실패")

    with Image.open(img_path) as im:
        w, h = im.size
    mask_bytes = make_full_transparent_mask_bytes(w, h)

    with open(img_path, "rb") as f_img, BytesIO(mask_bytes) as f_mask:
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
</style>
""", unsafe_allow_html=True)

# -------------------- 상단 고정 바 --------------------
st.markdown("""<div class="topbar-fixed"><div class="brand">🐾 Pet Memorialization 🐾</div></div>""", unsafe_allow_html=True)
st.markdown('<div class="main-block">', unsafe_allow_html=True)

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
tab1, tab2, tab3 = st.tabs(["📜 부고장/방명록/추모관", "📺 장례식 스트리밍", "💐 기부/꽃바구니"])

# ====== 탭1 ======
with tab1:
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
        st.info("아직 변환된 사진이 없습니다. 추모관에서 사진 업로드 후 자동 변환됩니다.")

    # 온라인 추모관 업로드 → 즉시 변환
    st.subheader("🖼️ 온라인 추모관")
    with st.form("gallery_upload", clear_on_submit=True):
        uploaded_files = st.file_uploader("사진 업로드", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
        submit = st.form_submit_button("업로드 및 자동 변환")
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
            in_path = os.path.join(UPLOAD_FOLDER, filename)
            with open(in_path, "wb") as f:
                f.write(data)
            saved += 1

            # ✅ 업로드 후 자동 변환
            if client is not None:
                out_path = os.path.join(CONVERTED_FOLDER, f"converted_{filename}")
                try:
                    ai_redraw_comic_style(in_path, out_path)
                except Exception as e:
                    st.error(f"AI 변환 실패: {e}")

        if saved: st.success(f"{saved}장 업로드 및 AI 변환 완료! 캐러셀에서 확인하세요.")
        if dup: st.info(f"중복으로 제외된 사진: {dup}장")
        st.rerun()
