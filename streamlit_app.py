import streamlit as st
import os
import hashlib
import base64
import mimetypes
from datetime import datetime
import html  # 메시지 안전 표시용

# -------------------- 페이지 기본 설정 --------------------
st.set_page_config(page_title="반려견 추모관", page_icon="🐾", layout="wide")

# -------------------- 색감/스타일 --------------------
st.markdown("""
    <style>
    :root{
        --bg:#FDF6EC; --ink:#4B3832; --accent:#CFA18D; --accent-2:#FAE8D9; --line:#EED7CA;
        --shadow:0 10px 24px rgba(79,56,50,0.12);
    }
    body { background-color: var(--bg); color: var(--ink); }
    h1,h2,h3 { color: var(--ink) !important; }

    /* ===== 상단 고정 브랜드 바 ===== */
    .topbar-fixed {
        position: fixed; top: 0; left: 0; right: 0; height: 60px;
        background-color: #FAE8D9; border-bottom: 1px solid #EED7CA;
        display: flex; align-items: center; padding: 0 24px; z-index: 1000;
    }
    .topbar-fixed .brand {
        display: flex; align-items: center; gap: 10px;
        font-size: 22px; font-weight: 800; color: #4B3832;
    }
    .topbar-fixed .logo { font-size: 26px; }
    .main-block { margin-top: 74px; }

    /* 공통 버튼 */
    .stButton>button{
        background: var(--accent); color:#fff; border:none; border-radius:12px;
        padding:8px 16px; font-weight:600; transition:.15s;
        box-shadow:0 3px 10px rgba(207,161,141,.25);
    }
    .stButton>button:hover{ filter: brightness(1.03); transform: translateY(-1px); }

    /* 방명록 카드 */
    .guest-card{
        background: linear-gradient(180deg, #FFF8F1 0%, #FFFFFF 100%);
        border: 1px solid var(--line);
        border-left: 6px solid var(--accent);
        border-radius: 14px; padding: 14px 16px; margin: 10px 0 16px 0;
        box-shadow: 0 4px 10px rgba(79, 56, 50, 0.08);
    }
    .guest-card-header{ display:flex; align-items:center; gap:10px; margin-bottom: 8px; }
    .guest-avatar{ width:34px; height:34px; min-width:34px; border-radius:50%;
        background:#F0D9CF; color:#4B3832; display:flex; align-items:center; justify-content:center; font-weight:700; }
    .guest-name-time{ display:flex; flex-direction:column; line-height:1.2; }
    .guest-name{ font-weight:700; }
    .guest-time{ font-size:12px; color:#8B6F66; }
    .guest-msg{ font-size:16px; color:#4B3832; white-space:pre-wrap; margin: 6px 0 0 0; }

    /* 갤러리(정사각형 썸네일 / 더 작게) */
    .photo-frame{
        background:#fff; border: 4px solid #F3E2D8; box-shadow: 0 6px 14px rgba(79,56,50,0.12);
        border-radius:12px; padding:6px; margin-bottom:10px;
    }
    .photo-frame .thumb{
        width:70%; aspect-ratio:1/1; object-fit:cover; display:block; border-radius:8px; margin:0 auto;
    }

    /* ===== 플로팅 버튼 ===== */
    .floating-btn {
        position: fixed; bottom: 24px; right: 24px;
        width: 60px; height: 60px; border-radius: 50%;
        background-color: #CFA18D; color: #fff; font-size: 28px; font-weight: bold;
        display:flex; align-items:center; justify-content:center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2); cursor: pointer; z-index: 999;
        transition: transform 0.2s;
    }
    .floating-btn:hover { transform: scale(1.05); }

    .floating-menu {
        position: fixed; bottom: 90px; right: 24px;
        display: none; flex-direction: column; gap: 10px; z-index: 998;
    }
    .floating-menu.show { display: flex; }
    .floating-menu a {
        background: #fff; color: #4B3832; text-decoration: none;
        padding: 8px 12px; border-radius: 8px; font-size: 14px;
        border: 1px solid #EED7CA; box-shadow: 0 3px 6px rgba(0,0,0,0.1);
    }
    </style>

    <script>
    function toggleFloatingMenu(){
        var menu = document.querySelector('.floating-menu');
        if(menu.classList.contains('show')){
            menu.classList.remove('show');
        } else {
            menu.classList.add('show');
        }
    }
    </script>
""", unsafe_allow_html=True)

# -------------------- 상단 고정 브랜드 바 --------------------
st.markdown("""
<div class="topbar-fixed">
  <div class="brand"><span class="logo">🐾</span> Forever Pet</div>
</div>
""", unsafe_allow_html=True)

# -------------------- 플로팅 버튼 --------------------
st.markdown("""
<div class="floating-btn" onclick="toggleFloatingMenu()">+</div>
<div class="floating-menu">
  <a href="https://pf.kakao.com/" target="_blank">카카오톡 문의</a>
  <a href="mailto:contact@foreverpet.com">이메일 문의</a>
</div>
""", unsafe_allow_html=True)

# -------------------- 본문 시작 --------------------
st.markdown('<div class="main-block">', unsafe_allow_html=True)

# -------------------- 공용 경로/유틸 --------------------
UPLOAD_FOLDER = "uploaded_images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

BASE_IMG_URL = "https://github.com/hyeongyunkim/teamproject/raw/main/petfuneral.png"

def list_uploaded_images():
    return sorted([
        f for f in os.listdir(UPLOAD_FOLDER)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ])

def build_image_list():
    uploaded = [os.path.join(UPLOAD_FOLDER, f) for f in list_uploaded_images()]
    return [BASE_IMG_URL] + uploaded

def initials_from_name(name: str) -> str:
    name = name.strip()
    return "🕊️" if not name else name[0].upper()

def file_sha256(byte_data: bytes) -> str:
    return hashlib.sha256(byte_data).hexdigest()

def img_file_to_data_uri(path: str) -> str:
    mime, _ = mimetypes.guess_type(path)
    if mime is None:
        mime = "image/jpeg"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}"

# -------------------- 히어로 영역 --------------------
try:
    with open("guestbook.txt", "r", encoding="utf-8") as f:
        guest_lines = [ln for ln in f.readlines() if ln.strip()]
except FileNotFoundError:
    guest_lines = []
photo_count = len(list_uploaded_images())
message_count = len(guest_lines)

st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
st.markdown(
    f"""
    <div class="hero">
      <div class="hero-grid">
        <div>
          <div class="tagline">소중한 반려견을 추모하는 공간</div>
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
    """,
    unsafe_allow_html=True
)
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div class="nav-divider"></div>', unsafe_allow_html=True)

# -------------------- 탭 --------------------
tab1, tab2, tab3 = st.tabs(["📜 부고장/방명록/추모관", "📺 스트리밍", "💐 기부/꽃바구니"])

# --- 이하 기존 기능(부고장/방명록/추모관, 스트리밍, 기부) 그대로 ---
# (위에서 제공한 코드와 동일하게 넣으시면 됩니다)
