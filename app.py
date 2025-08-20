import streamlit as st

# -------------------- 페이지 기본 설정 --------------------
st.set_page_config(page_title="반려견 추모관", page_icon="🐾", layout="centered")

st.sidebar.title("🐾 반려견 추모관")
st.sidebar.info("왼쪽 메뉴에서 원하는 페이지를 선택해주세요.")

st.markdown("<h1 style='text-align:center;'>🐾 반려견 추모관</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>사이드바 메뉴에서 페이지를 선택할 수 있습니다.</p>", unsafe_allow_html=True)
