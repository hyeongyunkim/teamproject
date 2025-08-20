import streamlit as st
import os
import uuid
from datetime import datetime

st.set_page_config(page_title="반려견 추모관", page_icon="🐾", layout="wide")

# -------------------- 상단 네비게이션 --------------------
st.markdown("""
    <style>
    .navbar {
        display: flex;
        justify-content: center;
        background-color: #FAE8D9;
        padding: 10px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    .nav-item {
        margin: 0 20px;
        font-size: 18px;
        font-weight: bold;
        color: #4B3832;
        text-decoration: none;
    }
    .nav-item:hover {
        color: #CFA18D;
        cursor: pointer;
    }
    </style>
""", unsafe_allow_html=True)

# 상단 메뉴 버튼
nav_options = ["부고장 + 방명록 + 추모관", "장례식 실시간 스트리밍", "기부 / 꽃바구니 주문"]
if "active_page" not in st.session_state:
    st.session_state["active_page"] = nav_options[0]

cols = st.columns(len(nav_options))
for i, option in enumerate(nav_options):
    if cols[i].button(option):
        st.session_state["active_page"] = option

menu = st.session_state["active_page"]

# -------------------- 삭제 확인 상태 --------------------
if "confirm_delete" not in st.session_state:
    st.session_state["confirm_delete"] = False
    st.session_state["delete_target"] = None

# -------------------- 1페이지 --------------------
if menu == "부고장 + 방명록 + 추모관":
    st.title("🐾 Pet Memorialization 🐾")
    st.subheader("In Loving Memory")
    st.caption("소중한 반려견을 추모할 수 있는 공간입니다")

    # 부고장
    st.header("📜 부고장")
    pet_name = "초코"
    birth_date = "2015-03-15"
    death_date = "2024-08-10"
    st.info(f"사랑하는 반려견 {pet_name} 이(가) 무지개다리를 건넜습니다.")
    st.markdown(f"🐾 **태어난 날:** {birth_date}  \n🌈 **무지개다리 건넌 날:** {death_date}")

    # 방명록
    st.header("✍️ 방명록")
    name = st.text_input("이름")
    message = st.text_area("메시지")
    if st.button("추모 메시지 남기기"):
        if name and message:
            with open("guestbook.txt", "a", encoding="utf-8") as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|{name}|{message}\n")
            st.rerun()
        else:
            st.warning("이름과 메시지를 입력해주세요.")

    try:
        with open("guestbook.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []

    for idx, line in enumerate(reversed(lines)):
        try:
            time_str, user, msg = line.strip().split("|", 2)
        except ValueError:
            continue
        st.markdown(f"🕊️ **{user}**: {msg}  \n<span style='color:gray;font-size:12px'>{time_str}</span>", unsafe_allow_html=True)
        if st.button("❌ 삭제", key=f"delete_msg_{idx}"):
            st.session_state["confirm_delete"] = True
            st.session_state["delete_target"] = ("guestbook", idx)

    # 추모관
    st.header("🖼️ 온라인 추모관")
    UPLOAD_FOLDER = "uploaded_images"
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    uploaded_file = st.file_uploader("사진 업로드", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        unique_filename = f"{uuid.uuid4()}_{uploaded_file.name}"
        with open(os.path.join(UPLOAD_FOLDER, unique_filename), "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.rerun()

    image_files = os.listdir(UPLOAD_FOLDER)
    cols = st.columns(3)
    for idx, img_file in enumerate(image_files):
        img_path = os.path.join(UPLOAD_FOLDER, img_file)
        with cols[idx % 3]:
            st.image(img_path, width=200)
            if st.button("삭제", key=f"delete_img_{idx}"):
                st.session_state["confirm_delete"] = True
                st.session_state["delete_target"] = ("image", img_path)

# -------------------- 삭제 확인창 --------------------
if st.session_state["confirm_delete"]:
    st.warning("정말 삭제하시겠습니까?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ 네, 삭제합니다."):
            target_type, target_value = st.session_state["delete_target"]
            if target_type == "guestbook":
                with open("guestbook.txt", "r", encoding="utf-8") as f:
                    lines = f.readlines()
                lines.pop(len(lines)-1-target_value)
                with open("guestbook.txt", "w", encoding="utf-8") as f:
                    f.writelines(lines)
            elif target_type == "image":
                if os.path.exists(target_value):
                    os.remove(target_value)
            st.session_state["confirm_delete"] = False
            st.rerun()
    with col2:
        if st.button("❌ 취소"):
            st.session_state["confirm_delete"] = False
            st.rerun()

# -------------------- 2페이지 --------------------
elif menu == "장례식 실시간 스트리밍":
    st.header("📺 장례식 실시간 스트리밍")
    video_url = st.text_input("YouTube URL", "https://www.youtube.com/embed/dQw4w9WgXcQ")
    st.markdown(f"<iframe width='560' height='315' src='{video_url}' frameborder='0' allowfullscreen></iframe>", unsafe_allow_html=True)

# -------------------- 3페이지 --------------------
elif menu == "기부 / 꽃바구니 주문":
    st.header("💐 기부 / 꽃바구니 주문")
    st.markdown("💳 기부: 카카오페이, 토스, 계좌이체 가능")
    link = st.text_input("꽃바구니 주문 링크", "https://www.naver.com")
    st.markdown(f"[👉 꽃바구니 주문하러 가기]({link})", unsafe_allow_html=True)
