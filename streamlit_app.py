import streamlit as st
import os
import hashlib
import base64
import mimetypes
from datetime import datetime
import html  # 메시지 안전 표시용

# -------------------- 페이지 기본 설정 --------------------
st.set_page_config(page_title="반려견 추모관", page_icon="🐾", layout="wide")

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

    /* 공통 버튼 */
    .stButton>button{
        background: var(--accent); color:#fff; border:none; border-radius:12px;
        padding:8px 16px; font-weight:600; transition:.15s;
        box-shadow:0 3px 10px rgba(207,161,141,.25);
    }
    .stButton>button:hover{ filter: brightness(1.03); transform: translateY(-1px); }

    /* 방명록 카드 */
    .guest-card{
        background: linear-gradient(180deg, #FFF8F1 0%, #FFFFFF 100%);
        border: 1px solid var(--line);
        border-left: 6px solid var(--accent);
        border-radius: 14px; padding: 14px 16px; margin: 10px 0 16px 0;
        box-shadow: 0 4px 10px rgba(79, 56, 50, 0.08);
    }
    .guest-card-header{ display:flex; align-items:center; gap:10px; margin-bottom: 8px; }
    .guest-avatar{ width:34px; height:34px; min-width:34px; border-radius:50%;
        background:#F0D9CF; color:#4B3832; display:flex; align-items:center; justify-content:center; font-weight:700; }
    .guest-name-time{ display:flex; flex-direction:column; line-height:1.2; }
    .guest-name{ font-weight:700; }
    .guest-time{ font-size:12px; color:#8B6F66; }
    .guest-msg{ font-size:16px; color:#4B3832; white-space:pre-wrap; margin: 6px 0 0 0; }

    /* 갤러리(정사각형 썸네일) */
    .photo-frame{
        background:#fff; border: 6px solid #F3E2D8; box-shadow: 0 8px 18px rgba(79,56,50,0.12);
        border-radius:16px; padding:10px; margin-bottom:12px;
    }
    .photo-frame .thumb{
        width:85%; aspect-ratio:1/1; object-fit:cover; display:block; border-radius:10px; margin:0 auto;
    }

    /* ===== 플로팅 버튼 ===== */
    .floating-btn {
        position: fixed; bottom: 24px; right: 24px;
        width: 60px; height: 60px; border-radius: 50%;
        background-color: #CFA18D; color: #fff; font-size: 28px; font-weight: bold;
        display:flex; align-items:center; justify-content:center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2); cursor: pointer; z-index: 999;
        transition: transform 0.2s;
    }
    .floating-btn:hover { transform: scale(1.05); }

    .floating-menu {
        position: fixed; bottom: 90px; right: 24px;
        display: none; flex-direction: column; gap: 10px; z-index: 998;
    }
    .floating-menu.show { display: flex; }
    .floating-menu a {
        background: #fff; color: #4B3832; text-decoration: none;
        padding: 8px 12px; border-radius: 8px; font-size: 14px;
        border: 1px solid #EED7CA; box-shadow: 0 3px 6px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# -------------------- 상단 고정 브랜드 바 --------------------
st.markdown("""
<div class="topbar-fixed">
  <div class="brand"><span class="logo">🐾</span> Forever Pet</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="main-block">', unsafe_allow_html=True)

# -------------------- 플로팅 버튼 --------------------
st.markdown("""
<div class="floating-btn" onclick="document.querySelector('.floating-menu').classList.toggle('show')">+</div>
<div class="floating-menu">
  <a href="https://pf.kakao.com/" target="_blank">카카오톡 문의</a>
  <a href="mailto:contact@foreverpet.com">이메일 문의</a>
</div>
""", unsafe_allow_html=True)

# -------------------- 예시 컨텐츠 --------------------
st.title("🐾 Pet Memorialization")
st.write("이곳은 반려견을 추모할 수 있는 공간입니다.")
st.info("왼쪽 아래 쓸데없는 버튼은 제거했고, 오른쪽 하단 `+` 플로팅 버튼만 남겼습니다.")

# ---------- 본문 종료 ----------
st.markdown('</div>', unsafe_allow_html=True)
