import streamlit as st
import os
import uuid
from datetime import datetime

# -------------------- 페이지 기본 설정 --------------------
st.set_page_config(page_title="반려견 추모관", page_icon="🐾", layout="centered")

# -------------------- CSS 스타일 --------------------
st.markdown("""
    <style>
    body {
        background-color: #FDF6EC;
        color: #4B3832;
    }
    h1, h2, h3 {
        color: #4B3832 !important;
    }
    .stButton>button {
        background-color: #CFA18D;
        color: white;
        border-radius: 10px;
        padding: 6px 15px;
        border: none;
        font-size: 14px;
    }
    .stButton>button:hover {
        background-color: #D9A7A0;
        color: #fff;
    }
    .stTextInput>div>div>input, .stTextArea textarea {
        background-color: #fff;
        border: 1px solid #CFA18D;
        border-radius: 10px;
    }
    .stSidebar {
        background-color: #FAE8D9;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------- 네비게이션 메뉴 --------------------
menu = st.sidebar.selectbox(
    "메뉴 선택",
    ["부고장 + 방명록 + 추모관", "장례식 실시간 스트리밍", "기부 / 꽃바구니 주문"]
)

# -------------------- 1페이지: 부고장 + 방명록 + 추모관 --------------------
if menu == "부고장 + 방명록 + 추모관":
    st.markdown("<h1 style='text-align: center;'>🐾 Pet Memorialization 🐾</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>In Loving Memory</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>소중한 반려견을 추모할 수 있는 공간입니다</p>", unsafe_allow_html=True)

    # -------------------- 대표 이미지 (슬라이드쇼 + 클릭 확대) --------------------
    from streamlit_carousel import carousel

    img_list = [
        "https://github.com/hyeongyunkim/teamproject/raw/main/petfuneral.png",
        # 추후 추가 가능
        # "https://path/to/second_image.jpg",
    ]
    carousel_items = [{"img": url, "title": "추억의 순간"} for url in img_list]

    selected = carousel(items=carousel_items, height=400)
    if selected:
        with st.expander("🔍 크게 보기", expanded=False):
            st.image(selected["img"], use_column_width=True)

    # -------------------- 부고장 --------------------
    st.markdown("<h2 style='text-align: center;'>📜 부고장</h2>", unsafe_allow_html=True)
    pet_name = "초코"
    birth_date = "2015-03-15"
    death_date = "2024-08-10"
    st.markdown(
        f"""
        <div style="text-align: center; background-color:#FAE8D9; padding:15px; border-radius:15px; margin:10px;">
        사랑하는 반려견 <b>{pet_name}</b> 이(가) 무지개다리를 건넜습니다.<br>
        함께한 시간들을 기억하며 따뜻한 마음으로 추모해주세요.
        <br><br>
        🐾 <b>태어난 날:</b> {birth_date} <br>
        🌈 <b>무지개다리 건넌 날:</b> {death_date}
        </div>
        """,
        unsafe_allow_html=True
    )

    # -------------------- 방명록 --------------------
    st.markdown("<h2 style='text-align: center;'>✍️ 방명록</h2>", unsafe_allow_html=True)
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

    st.markdown("<h3 style='text-align: center;'>📖 추모 메시지 모음</h3>", unsafe_allow_html=True)

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
                st.markdown(
                    f"""
                    <div style="
                        background-color:#fff;
                        padding:15px;
                        margin:10px 0;
                        border-radius:10px;
                        border: 1px solid #CFA18D;">
                        <p style="color:#4B3832; font-size:14px; margin:0;">🕊️ <b>{user}</b></p>
                        <p style="color:#4B3832; font-size:16px; margin:5px 0;">{msg}</p>
                        <p style="color:gray; font-size:12px; text-align:right; margin:0;">{time_str}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with col2:
                if st.button("❌", key=f"delete_msg_{idx}"):
                    lines.pop(len(lines)-1-idx)
                    with open("guestbook.txt", "w", encoding="utf-8") as f:
                        f.writelines(lines)
                    st.rerun()

    # -------------------- 온라인 추모관 --------------------
    st.markdown("<h2>🖼️ 온라인 추모관</h2>", unsafe_allow_html=True)
    UPLOAD_FOLDER = "uploaded_images"
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    uploaded_file = st.file_uploader("사진 업로드", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        unique_filename = f"{uuid.uuid4()}_{uploaded_file.name}"
        save_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"{uploaded_file.name} 업로드 완료!")
        st.rerun()

    image_files = os.listdir(UPLOAD_FOLDER)
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

# -------------------- 2페이지: 장례식 실시간 스트리밍 --------------------
elif menu == "장례식 실시간 스트리밍":
    st.header("📺 장례식 실시간 스트리밍 (원격 조문 지원)")
    st.markdown("아래에 YouTube 링크를 입력하면 스트리밍 영상이 표시됩니다.")
    video_url = st.text_input("YouTube 영상 URL 입력", "https://www.youtube.com/embed/dQw4w9WgXcQ")
    st.markdown(
        f"<div style='text-align:center;'><iframe width='560' height='315' src='{video_url}' frameborder='0' allowfullscreen></iframe></div>",
        unsafe_allow_html=True
    )

# -------------------- 3페이지: 기부 / 꽃바구니 주문 --------------------
elif menu == "기부 / 꽃바구니 주문":
    st.header("💐 조문객 기부 / 꽃바구니 주문")
    st.markdown("이 페이지에서 조문객이 온라인으로 기부하거나 꽃바구니를 주문할 수 있습니다.")
    st.markdown("- 💳 기부: 카카오페이 / 토스 / 계좌이체 연동 가능")
    st.markdown("- 🌹 꽃바구니 주문: 온라인 꽃집 링크 연결 가능")
    link = st.text_input("꽃바구니 주문 링크", "https://www.naver.com")
    st.markdown(f"<div style='text-align:center;'><a href='{link}' target='_blank' style='font-size:18px; color:#CFA18D; font-weight:bold;'>👉 꽃바구니 주문하러 가기</a></div>", unsafe_allow_html=True)
