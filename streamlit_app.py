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
    try:
        return (st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY", "")).strip()
    except Exception:
        return os.getenv("OPENAI_API_KEY", "").strip()

def load_org_id() -> str:
    try:
        return (st.secrets.get("OPENAI_ORG_ID") or os.getenv("OPENAI_ORG_ID", "")).strip()
    except Exception:
        return os.getenv("OPENAI_ORG_ID", "").strip()

OPENAI_API_KEY = load_api_key()
OPENAI_ORG_ID = load_org_id()
client = None
openai_import_error = None
if OPENAI_API_KEY:
    try:
        from openai import OpenAI
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
    return sorted([f for f in os.listdir(UPLOAD_FOLDER) if f.lower().endswith((".png", ".jpg", ".jpeg"))])

def list_converted_only():
    if not os.path.exists(CONVERTED_FOLDER):
        return []
    files = [os.path.join(CONVERTED_FOLDER, f) for f in os.listdir(CONVERTED_FOLDER) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return files

def img_file_to_data_uri(path: str) -> str:
    mime, _ = mimetypes.guess_type(path)
    if mime is None: mime = "image/png"
    with open(path, "rb") as f: b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}"

def converted_stem(src_filename: str) -> str:
    return os.path.splitext(src_filename)[0] + "__converted"

def converted_png_name(src_filename: str) -> str:
    return converted_stem(src_filename) + ".png"

# -------------------- 이미지 변환 --------------------
def _save_temp_square_png(src_path: str, max_side: int = 1024) -> str:
    with Image.open(src_path) as im:
        im = im.convert("RGBA")
        scale = min(max_side / im.width, max_side / im.height, 1.0)
        new_w, new_h = int(im.width * scale), int(im.height * scale)
        im = im.resize((new_w, new_h), Image.LANCZOS)
        canvas = Image.new("RGBA", (max_side, max_side), (255, 255, 255, 255))
        canvas.paste(im, ((max_side - new_w) // 2, (max_side - new_h) // 2))
    t = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    canvas.save(t.name, "PNG")
    return t.name

def _make_frame_mask_rgba(size: int = 1024, border: int = 24):
    m = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(m)
    d.rectangle([0, 0, size-1, border-1], fill=255)
    d.rectangle([0, size-border, size-1, size-1], fill=255)
    d.rectangle([0, border, border-1, size-border-1], fill=255)
    d.rectangle([size-border, border, size-1, size-border-1], fill=255)
    return m.convert("RGBA")

_ANIME_PROMPT = (
    "High-quality Japanese TV anime illustration. Keep the SAME pose and composition. "
    "Clean cel shading with 2–3 tones, bold black lineart, expressive eyes, "
    "simple background (plain/halftone/speed lines). No photo textures or realism."
)

def ai_redraw_comic_style(img_path: str, out_path: str):
    if client is None:
        raise RuntimeError("OpenAI 클라이언트가 준비되지 않았습니다.")
    if not out_path.lower().endswith(".png"):
        out_path = os.path.splitext(out_path)[0] + ".png"
    tmp_img, tmp_mask = None, None
    try:
        tmp_img = _save_temp_square_png(img_path)
        try:
            with open(tmp_img, "rb") as f_img:
                try:
                    resp = client.images.variations(model="gpt-image-1", image=f_img, n=1, size="1024x1024", prompt=_ANIME_PROMPT)
                except Exception:
                    f_img.seek(0)
                    resp = client.images.variations(model="gpt-image-1", image=f_img, n=1, size="1024x1024")
        except Exception:
            mask = _make_frame_mask_rgba()
            tmask = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            mask.save(tmask.name, "PNG"); tmp_mask = tmask.name
            with open(tmp_img, "rb") as f_img, open(tmp_mask, "rb") as f_mask:
                resp = client.images.edit(model="gpt-image-1", image=f_img, mask=f_mask, size="1024x1024", prompt=_ANIME_PROMPT)
        b64_img = resp.data[0].b64_json
        with open(out_path, "wb") as out: out.write(base64.b64decode(b64_img))
    finally:
        for p in (tmp_img, tmp_mask):
            try:
                if p and os.path.exists(p): os.remove(p)
            except: pass

# -------------------- CSS --------------------
st.markdown("""
<style>
/* 버튼 스타일 */
div[data-testid="stButton"][key="btn_convert"] button {
    background-color: #d7ecfb; color: #2a4d69; border: 1px solid #bcdff7;
    border-radius: 8px; padding: 0.4em 1em; min-width: 80px;
    font-weight: 600; font-size: 15px; white-space: nowrap;
}
div[data-testid="stButton"][key="btn_convert"] button:hover {
    background-color: #c2e0fa; border-color: #a6d1f5;
}
div[data-testid="stButton"][key="btn_original"] button {
    background-color: #d9f5e3; color: #2e5d4e; border: 1px solid #b8e6cf;
    border-radius: 8px; padding: 0.4em 1em; min-width: 80px;
    font-weight: 600; font-size: 15px; white-space: nowrap;
}
div[data-testid="stButton"][key="btn_original"] button:hover {
    background-color: #c5edd7; border-color: #a5dec4;
}
</style>
""", unsafe_allow_html=True)

# -------------------- 상단 바 --------------------
st.markdown("""<div class="topbar-fixed"><div class="brand">🐾 Pet Memorialization 🐾</div></div>""", unsafe_allow_html=True)
st.markdown('<div class="main-block">', unsafe_allow_html=True)

# -------------------- 모드 상태 --------------------
if "show_converted" not in st.session_state:
    st.session_state.show_converted = True

# -------------------- 탭 --------------------
tab1, tab2 = st.tabs(["📜 추모관", "📺 스트리밍"])

with tab1:
    # 버튼 행
    col_left, col_mid, col_spacer, col_right = st.columns([1,6,8,1])
    with col_left:
        if st.button("🎨 그림", key="btn_convert"):
            st.session_state.show_converted = True
            st.session_state.carousel_idx = 0
            st.rerun()
    with col_right:
        if st.button("🖼️ 원본", key="btn_original"):
            st.session_state.show_converted = False
            st.session_state.carousel_idx = 0
            st.rerun()

    # 캐러셀
    st.markdown("<h2 style='text-align:center;'>In Loving Memory</h2>", unsafe_allow_html=True)
    images = list_converted_only() if st.session_state.show_converted else [os.path.join(UPLOAD_FOLDER,f) for f in list_uploaded_only()]
    n = len(images)
    if "carousel_idx" not in st.session_state: st.session_state.carousel_idx = 0
    if n == 0:
        st.info("표시할 이미지가 없습니다. 사진을 업로드하세요.")
    else:
        prev, mid, nxt = st.columns([1,6,1])
        with prev:
            if st.button("◀", key="prev"): st.session_state.carousel_idx = (st.session_state.carousel_idx - 1) % n
        with mid:
            img = images[st.session_state.carousel_idx]
            data_uri = img_file_to_data_uri(img)
            st.markdown(f"<div style='text-align:center;'><img src='{data_uri}' style='max-width:80%;border-radius:12px;'></div>", unsafe_allow_html=True)
            st.caption(f"{st.session_state.carousel_idx+1}/{n}")
        with nxt:
            if st.button("▶", key="next"): st.session_state.carousel_idx = (st.session_state.carousel_idx + 1) % n

with tab2:
    st.header("📺 장례식 실시간 스트리밍")
    video_url = st.text_input("YouTube 영상 URL", "https://www.youtube.com/embed/dQw4w9WgXcQ")
    st.markdown(f"<div style='text-align:center;'><iframe width='560' height='315' src='{video_url}' frameborder='0' allowfullscreen></iframe></div>", unsafe_allow_html=True)
