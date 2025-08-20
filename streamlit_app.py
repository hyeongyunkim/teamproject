import streamlit as st
import os
import uuid
from datetime import datetime

# -------------------- 페이지 기본 설정 --------------------
st.set_page_config(page_title="반려견 추모관", page_icon="🐾", layout="wide")

# -------------------- CSS (상단 네비게이션 바) --------------------
st.markdown("""
    <style>
    body {
        background-color: #FDF6EC;
        color: #4B3832;
    }
    h1, h2, h3 { color: #4B3832 !important; }
    .stButton>button {
        background-color: #CFA18D;
        color: white;
        border-radius: 10px;
        padding: 6px 15px;
        border: none;
        font-size: 14px;
    }
    .stButton>button:hover { background-color: #D9A7A0; color: #fff; }
    .stTextInput>div>div>input, .stTextArea textarea {
        background-color: #fff;
        border: 1px solid #CFA18D;
        border-radius: 10px;
    }

    /* 상단 네비게이션 바 */
    .navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #FAE8D9;
        padding: 10px 20px;
        border-radius: 0 0 15px 15px;
    }
    .navbar-left {
        font-size: 20px;
        font-weight: bold;
        color: #4B3832;
    }
    .navbar-right a {
        margin: 0 10px;
        text-decoration: none;
        color: #4B3832;
        font-weight: bold;
        font-size: 16px;
    }
    .navbar-right a:hover {
        color: #CFA18D;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------- 상단 네비게이션 --------------------
st.markdown("""
    <div class="navbar">
        <div class="navbar-left">🐾 Pet Memorialization</div>
        <div class="navbar-right">
            <a href="?page=main">부고장/방명록/추모관</a>
            <a href="?page=streaming">장례식 스트리밍</a>
            <a href="?page=donation">기부/꽃바구니</a>
        </div>
    </div>
""", unsafe_allow_html=True)

# -------------------- 페이지 라우팅 --------------------
query_params = st.query_params
page = query_params.get("page", ["main"])[0]

UPLOAD_FOLDER = "uploaded_images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -------------------- 유틸: 이미지 리스트 --------------------
def build_image_list():
    base_img = "https://github.com/hyeongyunkim/teamproject/raw/main/petfuneral.png"
    uploaded = [
        os.path.join(UPLOAD_FOLDER, f)
        for f in os.listdir(UPLOAD_FOLDER)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ]
    return [base_img] + sorted(uploaded)

# -------------------- 페이지 1: 부고장 + 방명록 + 추모관 --------------------
if page == "main":
    st.markdown("<h1 style='text-align: center;'>In Loving Memory</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>소중한 반려견을 추모할 수 있는 공간입니다</p>", unsafe_allow_html=True)

    # 이미지 캐러셀
    img_list = build_image_list()
    n = len(img_list)
    if "carousel_idx" not in st.session_state:
        st.session_state.carousel_idx = 0
    st.session_state.carousel_idx %= max(n, 1)

    nav_prev, img_col, nav_next = st.columns([1,6,1])
    with nav_prev:
        if st.button("◀", key="carousel_prev"):
            st.session_state.carousel_idx = (st.session_state.carousel_idx - 1) % n
    with img_col:
        st.image(img_list[st.session_state.carousel_idx], use_container_width=True,
                 caption=f"{st.session_state.carousel_idx+1} / {n}")
    with nav_next:
        if st.button("▶", key="carousel_next"):
            st.session_state.carousel_idx = (st.session_state.carousel_idx + 1) % n

    if st.button("🔍 크게 보기", key="carousel_zoom"):
        with st.modal("대표 이미지 크게 보기"):
            st.image(img_list[st.session_state.carousel_idx], use_column_width=True)

    # 부고장
    st.subheader("📜 부고장")
    pet_name = "초코"
    birth_date = "2015-03-15"
    death_date = "2024-08-10"
    st.info(f"사랑하는 반려견 {pet_name} 이(가) 무지개다리를 건넜습니다.\n\n"
            f"🐾 태어난 날: {birth_date}\n\n🌈 무지개다리 건넌 날: {death_date}")

    # 방명록
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
            col1, col2 = st.columns([8,1])
            with col1:
                st.markdown(f"🕊️ **{user}** ({time_str})\n\n> {msg}")
            with col2:
                if st.button("❌", key=f"delete_msg_{idx}"):
                    lines.pop(len(lines) - 1 - idx)
                    with open("guestbook.txt", "w", encoding="utf-8") as f:
                        f.writelines(lines)
                    st.rerun()

    # 추모관 (사진 업로드)
    st.subheader("🖼️ 온라인 추모관")
    uploaded_file = st.file_uploader("사진 업로드", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        unique_filename = f"{uuid.uuid4()}_{uploaded_file.name}"
        save_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"{uploaded_file.name} 업로드 완료!")
        st.rerun()

    image_files = sorted([
        f for f in os.listdir(UPLOAD_FOLDER)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ])
    if image_files:
        cols_count = 3 if len(image_files) >= 3 else max(1, len(image_files))
        cols = st.columns(cols_count)
        for idx, img_file in enumerate(image_files):
            img_path = os.path.join(UPLOAD_FOLDER, img_file)
            with cols[idx % cols_count]:
                st.image(img_path, width=200, caption="🌸 추억의 사진 🌸")
                if st.button("삭제", key=f"delete_img_{idx}"):
                    os.remove(img_path)
                    st.rerun()
    else:
        st.info("아직 업로드된 사진이 없습니다.")

# -------------------- 페이지 2: 장례식 스트리밍 --------------------
elif page == "streaming":
    st.header("📺 장례식 실시간 스트리밍")
    video_url = st.text_input("YouTube 영상 URL 입력", "https://www.youtube.com/embed/dQw4w9WgXcQ")
    st.markdown(f"<div style='text-align:center;'><iframe width='560' height='315' src='{video_url}' frameborder='0' allowfullscreen></iframe></div>", unsafe_allow_html=True)

# -------------------- 페이지 3: 기부 / 꽃바구니 주문 --------------------
elif page == "donation":
    st.header("💐 조문객 기부 / 꽃바구니 주문")
    st.markdown("- 💳 기부: 카카오페이 / 토스 / 계좌이체 연동 가능\n- 🌹 꽃바구니 주문: 온라인 꽃집 링크 연결 가능")
    link = st.text_input("꽃바구니 주문 링크", "https://www.naver.com")
    st.markdown(f"<div style='text-align:center;'><a href='{link}' target='_blank' style='font-size:18px; color:#CFA18D; font-weight:bold;'>👉 꽃바구니 주문하러 가기</a></div>", unsafe_allow_html=True)
