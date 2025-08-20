import streamlit as st
import os
import uuid
from datetime import datetime

# -------------------- 페이지 기본 설정 --------------------
st.set_page_config(page_title="반려견 추모관", page_icon="🐾", layout="wide")

UPLOAD_FOLDER = "uploaded_images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -------------------- CSS 상단 네비게이션 --------------------
st.markdown(
    """
    <style>
    .navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #fff5f5;
        padding: 12px 30px;
        border-bottom: 2px solid #eee;
    }
    .navbar h2 {
        margin: 0;
        color: #CFA18D;
        font-weight: bold;
    }
    .menu {
        display: flex;
        gap: 20px;
    }
    .menu a {
        text-decoration: none;
        font-size: 18px;
        color: #444;
        padding: 6px 12px;
        border-radius: 8px;
    }
    .menu a.active {
        background-color: #CFA18D;
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------- 네비게이션 상태 --------------------
if "menu" not in st.session_state:
    st.session_state.menu = "부고장"

menu_items = {
    "부고장": "📜 부고장/방명록/추모관",
    "스트리밍": "📺 장례식 스트리밍",
    "기부": "💐 기부/꽃바구니"
}

# -------------------- 상단 바 HTML --------------------
menu_html = '<div class="navbar"><h2>🐾 Pet Memorialization</h2><div class="menu">'
for key, label in menu_items.items():
    active_class = "active" if st.session_state.menu == key else ""
    menu_html += f'<a href="#" class="{active_class}" onclick="window.parent.postMessage({{type: \'menu_select\', menu: \'{key}\'}}, \'*\')">{label}</a>'
menu_html += "</div></div>"
st.markdown(menu_html, unsafe_allow_html=True)

# -------------------- JS 이벤트 핸들러 --------------------
st.markdown(
    """
    <script>
    const streamlitEvents = window.streamlitEvents || {};
    window.streamlitEvents = streamlitEvents;
    window.addEventListener("message", (event) => {
        if (event.data.type === "menu_select") {
            const menu = event.data.menu;
            window.parent.postMessage({ isStreamlitMessage: true, type: "streamlit:setComponentValue", value: menu }, "*");
        }
    });
    </script>
    """,
    unsafe_allow_html=True,
)

selected_menu = st.session_state.menu

# -------------------- 유틸 --------------------
def build_image_list():
    base_img = "https://github.com/hyeongyunkim/teamproject/raw/main/petfuneral.png"
    uploaded = [
        os.path.join(UPLOAD_FOLDER, f)
        for f in os.listdir(UPLOAD_FOLDER)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ]
    return [base_img] + sorted(uploaded)

# -------------------- 페이지 렌더링 --------------------
if selected_menu == "부고장":
    st.markdown("<h2 style='text-align: center;'>In Loving Memory</h2>", unsafe_allow_html=True)
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
    st.info("사랑하는 반려견 초코가 무지개다리를 건넜습니다.\n\n🐾 태어난 날: 2015-03-15\n\n🌈 무지개다리 건넌 날: 2024-08-10")

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

    # 추모관
    st.subheader("🖼️ 온라인 추모관")
    uploaded_file = st.file_uploader("사진 업로드", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        unique_filename = f"{uuid.uuid4()}_{uploaded_file.name}"
        save_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"{uploaded_file.name} 업로드 완료!")
        st.rerun()

    image_files = sorted([f for f in os.listdir(UPLOAD_FOLDER) if f.lower().endswith((".png", ".jpg", ".jpeg"))])
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

elif selected_menu == "스트리밍":
    st.header("📺 장례식 실시간 스트리밍")
    video_url = st.text_input("YouTube 영상 URL 입력", "https://www.youtube.com/embed/dQw4w9WgXcQ")
    st.markdown(f"<div style='text-align:center;'><iframe width='560' height='315' src='{video_url}' frameborder='0' allowfullscreen></iframe></div>", unsafe_allow_html=True)

elif selected_menu == "기부":
    st.header("💐 조문객 기부 / 꽃바구니 주문")
    st.markdown("- 💳 기부: 카카오페이 / 토스 / 계좌이체 연동 가능\n- 🌹 꽃바구니 주문: 온라인 꽃집 링크 연결 가능")
    link = st.text_input("꽃바구니 주문 링크", "https://www.naver.com")
    st.markdown(f"<div style='text-align:center;'><a href='{link}' target='_blank' style='font-size:18px; color:#CFA18D; font-weight:bold;'>👉 꽃바구니 주문하러 가기</a></div>", unsafe_allow_html=True)
