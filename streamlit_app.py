import streamlit as st
import os
import uuid
import hashlib
import base64
import mimetypes
from datetime import datetime
import html  # 메시지 안전 표시용 (특수문자 이스케이프)

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
        letter-spacing: -0.2px;
    }
    .topbar-fixed .logo { font-size: 26px; }
    /* 본문이 가려지지 않도록 여백 */
    .main-block { margin-top: 74px; }  /* 상단바 높이 + 여유 */

    /* 공통 버튼 */
    .stButton>button{
        background: var(--accent); color:#fff; border:none; border-radius:12px;
        padding:8px 16px; font-weight:600; transition:.15s;
        box-shadow:0 3px 10px rgba(207,161,141,.25);
    }
    .stButton>button:hover{ filter: brightness(1.03); transform: translateY(-1px); }

    .stTextInput>div>div>input, .stTextArea textarea{
        background:#fff; border:1px solid var(--line); border-radius:12px;
    }

    .page-wrap{ max-width:1180px; margin:0 auto; }

    /* ---------- 히어로 영역(상단) ---------- */
    .hero{
        position:relative;
        background: radial-gradient(1200px 600px at 10% -20%, #FFEDE2 0%, rgba(255, 237, 226, 0) 60%),
                    linear-gradient(180deg, #FFF7F2 0%, #FFEFE6 100%);
        border:1px solid var(--line);
        border-radius:24px;
        box-shadow: var(--shadow);
        padding:28px 32px;
        overflow:hidden;
    }
    .hero:before{
        content:"";
        position:absolute; inset:-20px;
        background-image: radial-gradient(1px 1px at 20% 30%, rgba(207,161,141,.28) 0, transparent 60%),
                          radial-gradient(1px 1px at 60% 70%, rgba(207,161,141,.22) 0, transparent 60%),
                          radial-gradient(1px 1px at 80% 20%, rgba(207,161,141,.18) 0, transparent 60%);
        opacity:.6; pointer-events:none;
    }
    .hero-grid{
        display:grid; grid-template-columns: 1.6fr .9fr; gap:28px; align-items:center;
    }
    .tagline{
        font-size:18px; color:#6C5149; margin-bottom:14px;
    }
    .badges{ display:flex; gap:10px; flex-wrap:wrap; }
    .badge{
        display:inline-flex; align-items:center; gap:8px;
        padding:6px 10px; border-radius:999px; font-weight:700; font-size:13px;
        background:#fff; border:1px solid var(--line); box-shadow:0 2px 8px rgba(79,56,50,.05);
        color:#5A3E36;
    }
    .badge .dot{ width:8px; height:8px; border-radius:50%; background:var(--accent);
        box-shadow:0 0 0 3px rgba(207,161,141,.18) inset; }

    .hero-visual{ display:flex; align-items:center; justify-content:center; }
    .kv{
        width:180px; height:180px; border-radius:50%;
        background:#fff; border:6px solid #F3E2D8; box-shadow: var(--shadow); overflow:hidden;
    }
    .kv img{ width:100%; height:100%; object-fit:cover; display:block; }

    .nav-divider{ height:10px; }

    /* ---------- 방명록 카드 ---------- */
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

    /* ---------- 탭 헤더(센터/균등) ---------- */
    div[data-baseweb="tab-list"]{ justify-content:center !important; gap:12px !important; width:100% !important; }
    button[role="tab"]{
        min-width: 220px; /* 탭 가로폭 일정 */
        text-align:center !important; border-radius: 999px !important;
        border: 1px solid var(--line) !important; background:#FFF6EE !important;
        color: var(--ink) !important; font-weight:700 !important;
    }
    button[aria-selected="true"][role="tab"]{
        background: var(--accent) !important; color:#fff !important; border-color: var(--accent) !important;
        box-shadow: 0 2px 6px rgba(207,161,141,.35);
    }

    /* ---------- 갤러리(액자+정사각썸네일) ---------- */
    .photo-frame{
        background:#fff; border: 6px solid #F3E2D8; box-shadow: 0 8px 18px rgba(79,56,50,0.12);
        border-radius:16px; padding:10px; margin-bottom:12px;
    }
    .photo-frame .thumb{
        width:85%; aspect-ratio:1/1; object-fit:cover; display:block; border-radius:10px; margin:0 auto;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------- 상단 고정 브랜드 바 --------------------
st.markdown("""
<div class="topbar-fixed">
  <div class="brand"><span class="logo">🐾</span> Forever Pet</div>
</div>
""", unsafe_allow_html=True)

# 본문 시작(상단 고정바와 겹치지 않도록 오프셋)
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
    """대표 이미지(URL) + 업로드 이미지 경로 리스트"""
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

# -------------------- 상단 히어로 (전문 UI) --------------------
# 통계 계산(사진 수 / 방명록 수)
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
st.markdown('</div>', unsafe_allow_html=True)  # /page-wrap
st.markdown('<div class="nav-divider"></div>', unsafe_allow_html=True)

# -------------------- 탭 --------------------
tab1, tab2, tab3 = st.tabs(["📜 부고장/방명록/추모관", "📺 장례식 스트리밍", "💐 기부/꽃바구니"])

# ==================== ① 부고장/방명록/추모관 ====================
with tab1:
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)

    st.markdown("<h2 style='text-align:center;'>In Loving Memory</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#6C5149'>따뜻한 마음으로 그리움을 나눌 수 있는 공간입니다.</p>", unsafe_allow_html=True)

    # --- 대표 이미지 캐러셀 (액자 + 지표) ---
    img_list = build_image_list()
    n = len(img_list)
    total_photos = max(0, n - 1)  # 업로드 개수(대표 제외)

    if "carousel_idx" not in st.session_state:
        st.session
