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
    body { background-color: #FDF6EC; color: #4B3832; }
    h1, h2, h3 { color: #4B3832 !important; }
    .stButton>button {
        background-color: #CFA18D; color: white; border-radius: 10px;
        padding: 6px 15px; border: none; font-size: 14px; transition: all .15s ease;
    }
    .stButton>button:hover { background-color: #D9A7A0; color: #fff; }
    .stTextInput>div>div>input, .stTextArea textarea {
        background-color: #fff; border: 1px solid #CFA18D; border-radius: 10px;
    }
    .topbar {
        background-color:#FAE8D9; padding:12px 18px; border-radius:0 0 14px 14px;
        border-bottom: 1px solid #EED7CA;
    }
    .nav-divider { height:8px; }

    /* ---------- 방명록 카드 스타일 ---------- */
    .guest-card {
        background: linear-gradient(180deg, #FFF8F1 0%, #FFFFFF 100%);
        border: 1px solid #EED7CA;
        border-left: 6px solid #CFA18D;
        border-radius: 14px;
        padding: 14px 16px;
        margin: 10px 0 16px 0;
        box-shadow: 0 4px 10px rgba(79, 56, 50, 0.08);
    }
    .guest-card-header { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
    .guest-avatar {
        width: 34px; height: 34px; min-width:34px; border-radius: 50%;
        background: #F0D9CF; color:#4B3832; display:flex; align-items:center; justify-content:center; font-weight: 700;
    }
    .guest-name-time { display:flex; flex-direction:column; line-height:1.2; }
    .guest-name { font-weight:700; }
    .guest-time { font-size:12px; color:#8B6F66; }
    .guest-msg { font-size:16px; color:#4B3832; white-space:pre-wrap; margin: 6px 0 0 0; }

    /* ---------- 탭 헤더 균등 정렬 ---------- */
    div[data-baseweb="tab-list"] {
        justify-content: space-between !important;
        gap: 12px !important;
        width: 100% !important;
    }
    button[role="tab"] {
        flex: 1 1 0 !important;
        text-align: center !important;
        border-radius: 999px !important;
        border: 1px solid #EED7CA !important;
        background: #FFF6EE !important;
        color: #4B3832 !important;
        font-weight: 600 !important;
    }
    button[aria-selected="true"][role="tab"] {
        background: #CFA18D !important;
        color: #fff !important;
        border-color: #CFA18D !important;
        box-shadow: 0 2px 6px rgba(207,161,141,.35);
    }

    /* --- 온라인 추모관 액자 스타일 --- */
    .photo-frame {
        background:#fff;
        border: 6px solid #F3E2D8;
        box-shadow: 0 8px 18px rgba(79,56,50,0.12);
        border-radius: 16px;
        padding: 10px;
        margin-bottom: 12px;
    }

    /* --- 정사각형 썸네일 --- */
    .photo-frame .thumb {
        width: 100%;
        aspect-ratio: 1 / 1;   /* 정사각형 */
        object-fit: cover;
        display: block;
        border-radius: 10px;
    }

    /* --- 상단 캐러셀용 액자 --- */
    .photo-frame.hero {
        max-width: 560px;
        margin: 0 auto 8px auto;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------- 상단바 --------------------
with st.container():
    st.markdown('<div class="topbar"></div>', unsafe_allow_html=True)
    left, right = st.columns([1.8, 6.2], gap="large")
    with left:
        st.markdown("### 🐾 Pet Memorialization")
        st.markdown(
            "<p style='font-size:18px; font-weight:500; color:#5A3E36;'>소중한 반려견을 추모하는 공간</p>",
            unsafe_allow_html=True
        )
    with right:
        st.write("")

st.markdown('<div class="nav-divider"></div>', unsafe_allow_html=True)

# -------------------- 공용 경로/유틸 --------------------
UPLOAD_FOLDER = "uploaded_images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def build_image_list():
    base_img = "https://github.com/hyeongyunkim/teamproject/raw/main/petfuneral.png"
    uploaded = [
        os.path.join(UPLOAD_FOLDER, f)
        for f in sorted(os.listdir(UPLOAD_FOLDER))
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ]
    return [base_img] + uploaded

def initials_from_name(name: str) -> str:
    name = name.strip()
    if not name:
        return "🕊️"
    return name[0].upper()

def file_sha256(byte_data: bytes) -> str:
    return hashlib.sha256(byte_data).hexdigest()

def img_file_to_data_uri(path: str) -> str:
    mime, _ = mimetypes.guess_type(path)
    if mime is None:
        mime = "image/jpeg"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}"

# -------------------- 탭 --------------------
tab1, tab2, tab3 = st.tabs(["📜 부고장/방명록/추모관", "📺 장례식 스트리밍", "💐 기부/꽃바구니"])

# ==================== ① 부고장/방명록/추모관 ====================
with tab1:
    st.markdown("<h2 style='text-align:center;'>In Loving Memory</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>소중한 반려견을 추모할 수 있는 공간입니다</p>", unsafe_allow_html=True)

    # --- 대표 이미지 캐러셀 ---
    img_list = build_image_list()
    n = len(img_list)
    total_photos = max(0, n - 1)  # 업로드된 사진 개수 (대표 제외)

    if "carousel_idx" not in st.session_state:
        st.session_state.carousel_idx = 0
    st.session_state.carousel_idx %= max(n, 1)

    prev, mid, nextb = st.columns([1,6,1])
    with prev:
        if st.button("◀", key="carousel_prev"):
            st.session_state.carousel_idx = (st.session_state.carousel_idx - 1) % n

    with mid:
        current = img_list[st.session_state.carousel_idx]
        if current.startswith("http"):
            st.markdown(
                f"""
                <div class="photo-frame hero">
                    <img src="{current}" alt="memorial hero">
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            data_uri = img_file_to_data_uri(current)
            st.markdown(
                f"""
                <div class="photo-frame hero">
                    <img class="thumb" src="{data_uri}" alt="memorial hero">
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown(
            f"<p style='text-align:center; color:#6C5149;'>"
            f"<b>{st.session_state.carousel_idx + 1} / {n}</b> • "
            f"현재 업로드된 사진: <b>{total_photos}장</b>"
            f"</p>", unsafe_allow_html=True
        )

    with nextb:
        if st.button("▶", key="carousel_next"):
            st.session_state.carousel_idx = (st.session_state.carousel_idx + 1) % n

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
            st.success("메시지가 등록되었습니다. 고맙습니다.")
            st.rerun()
        else:
            st.warning("이름과 메시지를 입력해주세요.")

    # --- 방명록 모음 ---
    st.subheader("📖 추모 메시지 모음")
    try:
        with open("guestbook.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []
    if not lines:
        st.info("아직 등록된 메시지가 없습니다.")
    else:
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
        uploaded_files = st.file_uploader("사진 업로드", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
        submit = st.form_submit_button("업로드")

    if submit and uploaded_files:
        for uploaded_file in uploaded_files:
            data = uploaded_file.getvalue()
            digest = file_sha256(data)[:16]
            if any(f.startswith(digest + "_") for f in os.listdir(UPLOAD_FOLDER)):
                continue
            safe_name = "".join(c for c in uploaded_file.name if c not in "\\/:*?\"<>|")
            filename = f"{digest}_{safe_name}"
            with open(os.path.join(UPLOAD_FOLDER, filename), "wb") as f:
                f.write(data)
        st.success("사진 업로드 완료!")
        st.rerun()

    image_files = sorted([
        f for f in os.listdir(UPLOAD_FOLDER)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ])
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

# ==================== ② 장례식 스트리밍 ====================
with tab2:
    st.header("📺 장례식 실시간 스트리밍")
    video_url = st.text_input("YouTube 영상 URL", "https://www.youtube.com/embed/dQw4w9WgXcQ")
    st.markdown(f"<div style='text-align:center;'><iframe width='560' height='315' src='{video_url}' frameborder='0' allowfullscreen></iframe></div>", unsafe_allow_html=True)

# ==================== ③ 기부 / 꽃바구니 ====================
with tab3:
    st.header("💐 조문객 기부 / 꽃바구니 주문")
    link = st.text_input("꽃바구니 주문 링크", "https://www.naver.com")
    st.markdown(f"<div style='text-align:center;'><a href='{link}' target='_blank' style='font-size:18px; color:#CFA18D; font-weight:bold;'>👉 꽃바구니 주문하러 가기</a></div>", unsafe_allow_html=True)
