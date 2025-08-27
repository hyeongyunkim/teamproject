import streamlit as st
import os
import hashlib
import base64
import mimetypes
from datetime import datetime
import html  # 메시지 안전 표시용

# -------------------- 페이지 기본 설정 --------------------
st.set_page_config(page_title="Forever Pet - 반려견 추모관", page_icon="🐾", layout="wide")

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

    /* 버튼 */
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

    /* ---------- 탭 ---------- */
    div[data-baseweb="tab-list"]{ justify-content:center !important; gap:12px !important; width:100% !important; }
    button[role="tab"]{
        min-width: 200px;
        text-align:center !important; border-radius: 999px !important;
        border: 1px solid var(--line) !important; background:#FFF6EE !important;
        color: var(--ink) !important; font-weight:700 !important;
    }
    button[aria-selected="true"][role="tab"]{
        background: var(--accent) !important; color:#fff !important; border-color: var(--accent) !important;
        box-shadow: 0 2px 6px rgba(207,161,141,.35);
    }
    .tab-short { display:none; }
    .tab-long { display:inline; }
    @media (max-width: 768px){
      .tab-short { display:inline; }
      .tab-long { display:none; }
    }

    /* ---------- 방명록 카드 ---------- */
    .guest-card{
        background: linear-gradient(180deg, #FFF8F1 0%, #FFFFFF 100%);
        border: 1px solid var(--line);
        border-left: 6px solid var(--accent);
        border-radius: 14px; padding: 14px 16px; margin: 10px 0 16px 0;
        box-shadow: 0 4px 10px rgba(79, 56, 50, 0.08);
    }
    .guest-card-header{ display:flex; align-items:center; gap:10px; margin-bottom: 8px; }
    .guest-avatar{ width:34px; height:34px; border-radius:50%; background:#F0D9CF; 
        color:#4B3832; display:flex; align-items:center; justify-content:center; font-weight:700; }
    .guest-name-time{ display:flex; flex-direction:column; line-height:1.2; }
    .guest-name{ font-weight:700; }
    .guest-time{ font-size:12px; color:#8B6F66; }
    .guest-msg{ font-size:16px; color:#4B3832; white-space:pre-wrap; margin: 6px 0 0 0; }

    /* ---------- 갤러리 ---------- */
    .photo-frame{
        background:#fff; border: 6px solid #F3E2D8; box-shadow: 0 8px 18px rgba(79,56,50,0.12);
        border-radius:16px; padding:10px; margin-bottom:12px;
    }
    .photo-frame .thumb{
        width:85%; aspect-ratio:1/1; object-fit:cover; display:block; border-radius:10px; margin:0 auto;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------- 상단 브랜드 바 --------------------
st.markdown("""
<div class="topbar-fixed">
  <div class="brand"><span class="logo">🐾</span> Forever Pet</div>
</div>
""", unsafe_allow_html=True)
st.markdown('<div class="main-block">', unsafe_allow_html=True)

# -------------------- 유틸 --------------------
UPLOAD_FOLDER = "uploaded_images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
BASE_IMG_URL = "https://github.com/hyeongyunkim/teamproject/raw/main/petfuneral.png"

def list_uploaded_images():
    return sorted([f for f in os.listdir(UPLOAD_FOLDER) if f.lower().endswith((".png", ".jpg", ".jpeg"))])

def initials_from_name(name: str) -> str:
    return "🕊️" if not name else name[0].upper()

def file_sha256(byte_data: bytes) -> str:
    return hashlib.sha256(byte_data).hexdigest()

def img_file_to_data_uri(path: str) -> str:
    mime, _ = mimetypes.guess_type(path)
    if mime is None: mime = "image/jpeg"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}"

# -------------------- 탭 --------------------
tab1, tab2, tab3 = st.tabs([
    "<span class='tab-long'>📜 부고장/방명록/추모관</span><span class='tab-short'>📜 추모관</span>",
    "<span class='tab-long'>📺 장례식 스트리밍</span><span class='tab-short'>📺 스트리밍</span>",
    "<span class='tab-long'>💐 기부/꽃바구니</span><span class='tab-short'>💐 기부</span>",
])

# ==================== ① 부고장/방명록/추모관 ====================
with tab1:
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>In Loving Memory</h2>", unsafe_allow_html=True)

    # --- 부고장 ---
    st.subheader("📜 부고장")
    st.markdown(
        """
        <div style="text-align:center; background-color:#FAE8D9; padding:15px; border-radius:15px; margin:10px;">
        사랑하는 반려견 <b>초코</b> 이(가) 무지개다리를 건넜습니다.<br>
        함께한 시간들을 기억하며 따뜻한 마음으로 추모해주세요.
        <br><br>
        🐾 <b>태어난 날:</b> 2015-03-15 <br>
        🌈 <b>무지개다리 건넌 날:</b> 2024-08-10
        </div>
        """,
        unsafe_allow_html=True
    )

    # --- 방명록 작성 ---
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

    # --- 방명록 목록 ---
    st.subheader("📖 추모 메시지 모음")
    try:
        with open("guestbook.txt", "r", encoding="utf-8") as f:
            lines = [ln for ln in f.readlines() if ln.strip()]
    except FileNotFoundError:
        lines = []
    for idx, line in enumerate(reversed(lines)):
        try:
            time_str, user, msg = line.strip().split("|", 2)
        except ValueError:
            continue
        st.markdown(
            f"""
            <div class="guest-card">
                <div class="guest-card-header">
                    <div class="guest-avatar">{html.escape(initials_from_name(user))}</div>
                    <div class="guest-name-time">
                        <span class="guest-name">🕊️ {html.escape(user)}</span>
                        <span class="guest-time">{html.escape(time_str)}</span>
                    </div>
                </div>
                <div class="guest-msg">{html.escape(msg)}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # --- 온라인 추모관 ---
    st.subheader("🖼️ 온라인 추모관")
    with st.form("gallery_upload", clear_on_submit=True):
        uploaded_files = st.file_uploader("사진 업로드", type=["png","jpg","jpeg"], accept_multiple_files=True)
        submit = st.form_submit_button("업로드")
    if submit and uploaded_files:
        for uploaded_file in uploaded_files:
            data = uploaded_file.getvalue()
            digest = file_sha256(data)[:16]
            if not any(f.startswith(digest + "_") for f in os.listdir(UPLOAD_FOLDER)):
                safe_name = "".join(c for c in uploaded_file.name if c not in "\\/:*?\"<>|")
                filename = f"{digest}_{safe_name}"
                with open(os.path.join(UPLOAD_FOLDER, filename), "wb") as f:
                    f.write(data)
        st.rerun()

    image_files = list_uploaded_images()
    if image_files:
        cols = st.columns(3)
        for idx, img_file in enumerate(image_files):
            img_path = os.path.join(UPLOAD_FOLDER, img_file)
            with cols[idx % 3]:
                data_uri = img_file_to_data_uri(img_path)
                st.markdown(
                    f"""
                    <div class="photo-frame">
                        <img class="thumb" src="{data_uri}" alt="memorial photo">
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                if st.button("삭제", key=f"delete_img_{idx}"):
                    os.remove(img_path)
                    st.rerun()
    else:
        st.info("아직 업로드된 사진이 없습니다.")
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== ② 장례식 실시간 스트리밍 ====================
with tab2:
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
    st.header("📺 장례식 실시간 스트리밍")
    video_url = st.text_input("YouTube 영상 URL 입력", "https://www.youtube.com/embed/dQw4w9WgXcQ")
    st.markdown(
        f"<div style='text-align:center;'><iframe width='560' height='315' src='{video_url}' frameborder='0' allowfullscreen></iframe></div>",
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== ③ 기부 / 꽃바구니 주문 ====================
with tab3:
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
    st.header("💐 조문객 기부 / 꽃바구니 주문")
    link = st.text_input("꽃바구니 주문 링크", "https://www.naver.com")
    st.markdown(
        f"<div style='text-align:center;'><a href='{link}' target='_blank' style='font-size:18px; color:#CFA18D; font-weight:bold;'>👉 꽃바구니 주문하러 가기</a></div>",
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
