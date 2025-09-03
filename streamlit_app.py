import streamlit as st
import os
import hashlib
import base64
import mimetypes
from datetime import datetime
import html

# -------------------- 페이지 기본 설정 --------------------
st.set_page_config(page_title="반려견 추모관", page_icon="🐾", layout="wide")

# -------------------- CSS 스타일 --------------------
st.markdown("""
    <style>
    :root{
        --bg:#FDF6EC; --ink:#4B3832; --accent:#CFA18D; --accent-2:#FAE8D9; --line:#EED7CA;
        --shadow:0 10px 24px rgba(79,56,50,0.12);
    }
    body { background-color: var(--bg); color: var(--ink); }
    h1,h2,h3 { color: var(--ink) !important; }

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

    .stButton>button{
        background: var(--accent); color:#fff; border:none; border-radius:12px;
        padding:8px 16px; font-weight:600; transition:.15s;
        box-shadow:0 3px 10px rgba(207,161,141,.25);
    }
    .stButton>button:hover{ filter: brightness(1.03); transform: translateY(-1px); }

    .page-wrap{ max-width:1180px; margin:0 auto; }

    .hero{ border-radius:24px; box-shadow: var(--shadow);
           background: radial-gradient(1200px 600px at 10% -20%, #FFEDE2 0%, rgba(255, 237, 226, 0) 60%),
                       linear-gradient(180deg, #FFF7F2 0%, #FFEFE6 100%);
           padding:28px 32px; }
    .hero-grid{ display:grid; grid-template-columns: 1.6fr .9fr; gap:28px; align-items:center; }
    .tagline{ font-size:18px; color:#6C5149; margin-bottom:14px; }
    .badges{ display:flex; gap:10px; flex-wrap:wrap; }
    .badge{ padding:6px 10px; border-radius:999px; background:#fff;
            border:1px solid var(--line); font-weight:700; font-size:13px; }

    .kv{ width:180px; height:180px; border-radius:50%; overflow:hidden;
         border:6px solid #F3E2D8; box-shadow: var(--shadow); }
    .kv img{ width:100%; height:100%; object-fit:cover; }

    .guest-card{ background: linear-gradient(180deg, #FFF8F1 0%, #FFFFFF 100%);
                 border-left: 6px solid var(--accent); border-radius: 14px;
                 padding: 14px 16px; margin: 10px 0; }
    .guest-avatar{ width:34px; height:34px; border-radius:50%; background:#F0D9CF;
                   display:flex; align-items:center; justify-content:center; }
    .guest-name{ font-weight:700; }
    .guest-time{ font-size:12px; color:#8B6F66; }
    .guest-msg{ font-size:16px; margin-top:6px; }

    .photo-frame.hero-frame .thumb{ width:60%; margin:0 auto; border-radius:10px; }
    .photo-frame.gallery-frame .thumb{ width:50%; margin:0 auto; border-radius:10px; }
    </style>
""", unsafe_allow_html=True)

# -------------------- 상단 바 --------------------
st.markdown("""
<div class="topbar-fixed">
  <div class="brand"><span class="logo">🐾</span> Forever Pet</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="main-block">', unsafe_allow_html=True)

# -------------------- 파일 경로 --------------------
UPLOAD_FOLDER = "uploaded_images"
OBITUARY_FILE = "obituary.txt"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

BASE_IMG_URL = "https://github.com/hyeongyunkim/teamproject/raw/main/petfuneral.png"

# -------------------- 유틸 --------------------
def list_uploaded_images():
    return sorted([f for f in os.listdir(UPLOAD_FOLDER) if f.lower().endswith((".png", ".jpg", ".jpeg"))])

def build_image_list():
    return [BASE_IMG_URL] + [os.path.join(UPLOAD_FOLDER, f) for f in list_uploaded_images()]

def file_sha256(byte_data: bytes) -> str:
    return hashlib.sha256(byte_data).hexdigest()

def img_file_to_data_uri(path: str) -> str:
    mime, _ = mimetypes.guess_type(path)
    if mime is None: mime = "image/jpeg"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}"

# obituary 저장/불러오기
def load_obituary():
    if os.path.exists(OBITUARY_FILE):
        with open(OBITUARY_FILE, "r", encoding="utf-8") as f:
            data = f.read().strip().split("|")
        if len(data) == 3:
            return data
    return ["초코", "2015-03-15", "2024-08-10"]

def save_obituary(name, birth, rainbow):
    with open(OBITUARY_FILE, "w", encoding="utf-8") as f:
        f.write(f"{name}|{birth}|{rainbow}")

# -------------------- Hero 영역 --------------------
try:
    with open("guestbook.txt", "r", encoding="utf-8") as f:
        guest_lines = [ln for ln in f if ln.strip()]
except FileNotFoundError:
    guest_lines = []

photo_count = len(list_uploaded_images())
message_count = len(guest_lines)
saved_name, saved_birth, saved_rainbow = load_obituary()

st.markdown(
    f"""
    <div class="hero">
      <div class="hero-grid">
        <div>
          <div style="font-size:26px; font-weight:900;">🐾 Pet Memorialization</div>
          <div class="tagline">소중한 반려견을 추모하는 공간</div>
          <div class="badges">
            <span class="badge">사진 {photo_count}장</span>
            <span class="badge">방명록 {message_count}개</span>
          </div>
        </div>
        <div class="hero-visual"><div class="kv"><img src="{BASE_IMG_URL}"></div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# -------------------- Tabs --------------------
tab1, tab2, tab3 = st.tabs(["📜 부고장/방명록/추모관", "📺 장례식 스트리밍", "💐 기부/꽃바구니"])

# --------- Tab1 : 부고장/방명록/추모관 ---------
with tab1:
    st.subheader("📜 부고장")

    # 관리자 모드
    admin_mode = st.checkbox("관리자 모드")
    admin_pw = st.text_input("비밀번호", type="password") if admin_mode else ""
    if admin_mode and admin_pw == "1234":
        with st.form("obituary_form"):
            pet_name = st.text_input("반려동물 이름", saved_name)
            birth_date = st.date_input("태어난 날", datetime.strptime(saved_birth, "%Y-%m-%d"))
            rainbow_date = st.date_input("무지개다리 건넌 날", datetime.strptime(saved_rainbow, "%Y-%m-%d"))
            if st.form_submit_button("저장"):
                save_obituary(pet_name, birth_date.strftime("%Y-%m-%d"), rainbow_date.strftime("%Y-%m-%d"))
                st.success("부고장이 저장되었습니다.")
                st.rerun()

    st.markdown(
        f"""
        <div style="text-align:center; background:#FAE8D9; padding:15px; border-radius:15px; margin:10px;">
        사랑하는 반려견 <b>{saved_name}</b> 이(가) 무지개다리를 건넜습니다.<br>
        🐾 태어난 날: {saved_birth} <br>
        🌈 무지개다리 건넌 날: {saved_rainbow}
        </div>
        """, unsafe_allow_html=True
    )

    # 방명록
    st.subheader("✍️ 방명록")
    name = st.text_input("이름")
    message = st.text_area("메시지")
    if st.button("추모 메시지 남기기"):
        if name and message:
            with open("guestbook.txt", "a", encoding="utf-8") as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|{name}|{message}\n")
            st.success("메시지가 등록되었습니다.")
            st.rerun()

    if guest_lines:
        for line in reversed(guest_lines):
            try:
                t, user, msg = line.strip().split("|", 2)
            except:
                continue
            st.markdown(
                f"""<div class="guest-card">
                        <div><b>🕊️ {html.escape(user)}</b> <span class="guest-time">{t}</span></div>
                        <div class="guest-msg">{html.escape(msg)}</div>
                    </div>""", unsafe_allow_html=True
            )
    else:
        st.info("아직 등록된 메시지가 없습니다.")

    # 갤러리
    st.subheader("🖼️ 온라인 추모관")
    with st.form("gallery_upload", clear_on_submit=True):
        files = st.file_uploader("사진 업로드", type=["png","jpg","jpeg"], accept_multiple_files=True)
        if st.form_submit_button("업로드") and files:
            for f in files:
                digest = file_sha256(f.getvalue())[:16]
                filename = f"{digest}_{f.name}"
                with open(os.path.join(UPLOAD_FOLDER, filename), "wb") as out:
                    out.write(f.getvalue())
            st.rerun()

    for img_file in list_uploaded_images():
        data_uri = img_file_to_data_uri(os.path.join(UPLOAD_FOLDER, img_file))
        st.markdown(f"<div class='photo-frame gallery-frame'><img class='thumb' src='{data_uri}'></div>", unsafe_allow_html=True)

# --------- Tab2 : 스트리밍 ---------
with tab2:
    st.header("📺 장례식 실시간 스트리밍")
    video_url = st.text_input("YouTube 링크", "https://www.youtube.com/embed/dQw4w9WgXcQ")
    st.markdown(f"<iframe width='560' height='315' src='{video_url}' frameborder='0' allowfullscreen></iframe>", unsafe_allow_html=True)

# --------- Tab3 : 기부/꽃바구니 ---------
with tab3:
    st.header("💐 기부 / 꽃바구니")
    link = st.text_input("꽃바구니 주문 링크", "https://www.naver.com")
    st.markdown(f"<a href='{link}' target='_blank'>👉 꽃바구니 주문하기</a>", unsafe_allow_html=True)
