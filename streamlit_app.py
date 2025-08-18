import streamlit as st
import os
from datetime import datetime
import base64
import math

# 페이지 기본 설정
st.set_page_config(page_title="반려견 추모관", page_icon="🐾", layout="centered")

# --- 헤더 ---
st.markdown("<h1 style='text-align: center;'>🐾 Pet Memorialization 🐾</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>In Loving Memory</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>소중한 반려견을 추모할 수 있는 공간입니다</p>", unsafe_allow_html=True)

# --- GitHub 추모 이미지 ---
img_url = "https://github.com/hyeongyunkim/teamproject/raw/main/petfuneral.png"
st.markdown(
    f"<div style='text-align: center;'><img src='{img_url}' width='300'></div>",
    unsafe_allow_html=True
)

# --- 부고장 ---
st.markdown("<h2 style='text-align: center;'>📜 부고장</h2>", unsafe_allow_html=True)
pet_name = "초코"
st.markdown(
    f"<p style='text-align: center;'>사랑하는 반려견 <b>{pet_name}</b> 이(가) 무지개다리를 건넜습니다.<br>함께한 시간들을 기억하며 따뜻한 마음으로 추모해주세요.</p>",
    unsafe_allow_html=True
)

# --- 방명록 ---
st.markdown("<h2 style='text-align: center;'>✍️ 방명록</h2>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1,2,1])
with col2:
    name = st.text_input("이름")
    message = st.text_area("메시지")
    if st.button("추모 메시지 남기기"):
        if name and message:
            with open("guestbook.txt", "a", encoding="utf-8") as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {name}: {message}\n")
            st.success("메시지가 등록되었습니다. 고맙습니다.")
        else:
            st.warning("이름과 메시지를 입력해주세요.")

# --- 방명록 읽어오기 ---
st.markdown("<h3 style='text-align: center;'>📖 추모 메시지 모음</h3>", unsafe_allow_html=True)
try:
    with open("guestbook.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            st.markdown(f"<p style='text-align: center;'>{line.strip()}</p>", unsafe_allow_html=True)
except FileNotFoundError:
    st.info("아직 등록된 메시지가 없습니다.")

# --- 온라인 추모관 (갤러리) ---
st.markdown("<h2>🖼️ 온라인 추모관</h2>", unsafe_allow_html=True)

# 업로드 폴더
UPLOAD_FOLDER = "uploaded_images"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --- 사진 업로드 ---
uploaded_file = st.file_uploader("사진 업로드", type=["png", "jpg", "jpeg"])
if uploaded_file is not None:
    save_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"{uploaded_file.name} 업로드 완료!")

# --- 갤러리 표시 (반응형) ---
image_files = os.listdir(UPLOAD_FOLDER)

if image_files:
    # 반응형 열 수 결정 (화면 폭이 넓으면 4열, 좁으면 2~3열)
    num_images = len(image_files)
    cols_count = 3 if num_images >= 3 else max(1, num_images)
    cols = st.columns(cols_count)
    
    for idx, img_file in enumerate(image_files):
        img_path = os.path.join(UPLOAD_FOLDER, img_file)
        with open(img_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        with cols[idx % cols_count]:
            st.markdown(f'<img src="data:image/png;base64,{encoded}" width="200">', unsafe_allow_html=True)
else:
    st.info("아직 업로드된 사진이 없습니다.")
