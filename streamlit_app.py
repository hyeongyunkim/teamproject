import streamlit as st
import os
from datetime import datetime
import requests
from PIL import Image
from io import BytesIO

# 페이지 기본 설정
st.set_page_config(page_title="반려견 추모관", page_icon="🐾", layout="centered")

# 헤더
st.title("🐾 반려견 장례식 추모 웹페이지")
st.subheader("In Loving Memory")
st.write("소중한 반려견을 추모할 수 있는 공간입니다.")

# 추모 이미지 (절대 경로 방식)
img_url = "https://github.com/hyeongyunkim/teamproject/raw/main/petfuneral.png"
st.image(img_url, caption="추모 이미지", use_column_width=True)



# 부고장
st.header("📜 부고장")
pet_name = "초코"
st.write(f"사랑하는 반려견 **{pet_name}** 이(가) 무지개다리를 건넜습니다.")
st.write("함께한 시간들을 기억하며 따뜻한 마음으로 추모해주세요.")

# 방명록 (메시지 남기기)
st.header("✍️ 방명록")
name = st.text_input("이름")
message = st.text_area("메시지")
if st.button("추모 메시지 남기기"):
    if name and message:
        with open("guestbook.txt", "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {name}: {message}\n")
        st.success("메시지가 등록되었습니다. 고맙습니다.")
    else:
        st.warning("이름과 메시지를 입력해주세요.")

# 방명록 읽어오기
st.subheader("📖 추모 메시지 모음")
try:
    with open("guestbook.txt", "r", encoding="utf-8") as f:
        for line in f.readlines():
            st.write(line.strip())
except FileNotFoundError:
    st.info("아직 등록된 메시지가 없습니다.")

# 온라인 추모관 (사진 올리기)
st.header("🖼️ 온라인 추모관")
uploaded_file = st.file_uploader("사진 업로드", type=["png", "jpg", "jpeg"])
if uploaded_file is not None:
    st.image(uploaded_file, caption="추모 사진", use_column_width=True)
