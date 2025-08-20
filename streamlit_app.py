import streamlit as st
import os
from datetime import datetime
import base64

# 페이지 기본 설정 (모바일 친화 레이아웃)
st.set_page_config(page_title="반려견 추모관", page_icon="🐾", layout="wide")

# --- CSS for Mobile Optimization ---
st.markdown("""
<style>
    /* 모바일 화면에서 글씨 크기 조정 */
    h1, h2, h3 { text-align: center; }
    p { font-size: 16px; }
    /* 카드 스타일 */
    .message-card {
        background-color:#f9f9f9;
        padding:12px;
        margin:8px 0;
        border-radius:12px;
        box-shadow: 1px 1px 4px rgba(0,0,0,0.1);
    }
    .message-user { font-size: 14px; font-weight: bold; color:#333; }
    .message-text { font-size: 15px; color:#444; margin:6px 0; }
    .message-time { font-size: 11px; color:gray; text-align:right; }
    /* 이미지 반응형 */
    .gallery-img { width: 100%; max-width: 200px; border-radius:10px; margin:5px 0; }
</style>
""", unsafe_allow_html=True)

# --- 사이드바 메뉴 ---
menu = st.sidebar.selectbox(
    "메뉴 선택",
    ["부고장 + 방명록 + 추모관", "장례식 실시간 스트리밍", "기부 / 꽃바구니 주문"]
)

# --- 1페이지 ---
if menu == "부고장 + 방명록 + 추모관":
    st.markdown("<h1>🐾 Pet Memorialization 🐾</h1>", unsafe_allow_html=True)
    st.markdown("<h3>In Loving Memory</h3>", unsafe_allow_html=True)
    st.markdown("<p>소중한 반려견을 추모할 수 있는 공간입니다</p>", unsafe_allow_html=True)

    # 추모 이미지
    img_url = "https://github.com/hyeongyunkim/teamproject/raw/main/petfuneral.png"
    st.image(img_url, width=250)

    # 부고장
    pet_name, birth_date, death_date = "초코", "2015-03-15", "2024-08-10"
    st.markdown(f"""
        <h2>📜 부고장</h2>
        <p>
        사랑하는 반려견 <b>{pet_name}</b> 이(가) 무지개다리를 건넜습니다.<br>
        함께한 시간들을 기억하며 따뜻한 마음으로 추모해주세요.
        </p>
        <p>
        🐾 <b>태어난 날:</b> {birth_date}<br>
        🌈 <b>무지개다리 건넌 날:</b> {death_date}
        </p>
        """, unsafe_allow_html=True)

    # 방명록
    st.markdown("<h2>✍️ 방명록</h2>", unsafe_allow_html=True)
    name = st.text_input("이름", placeholder="이름을 입력해주세요", key="guest_name")
    message = st.text_area("메시지", placeholder="추모 메시지를 남겨주세요", key="guest_msg")
    if st.button("추모 메시지 남기기", use_container_width=True):
        if name and message:
            with open("guestbook.txt", "a", encoding="utf-8") as f:
                f.write(f"{datetime.now(
