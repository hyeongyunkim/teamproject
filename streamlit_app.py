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
    :root{
        --bg:#FDF6EC; --ink:#4B3832; --accent:#CFA18D; --accent-2:#FAE8D9; --line:#EED7CA;
        --shadow:0 10px 24px rgba(79,56,50,0.12);
    }
    body { background-color: var(--bg); color: var(--ink); }
    h1,h2,h3 { color: var(--ink) !important; }

    /* 공통 버튼 */
    .stButton>button{
        background: var(--accent); color:#fff; border:none; border-radius:12px;
        padding:8px 16px; font-weight:600; transition:.15s; box-shadow:0 3px 10px rgba(207,161,141,.25);
    }
    .stButton>button:hover{ filter: brightness(1.03); transform: translateY(-1px); }

    .stTextInput>div>div>input, .stTextArea textarea{
        background:#fff; border:1px solid var(--line); border-radius:12px;
    }

    /* 최대 폭 고정 컨테이너 느낌 */
    .page-wrap{ max-width:1180px; margin:0 auto; }

    /* ---------- 최상단 고정 브랜드 바 ---------- */
    .topbar-fixed {
        position: fixed; top: 0; left: 0; right: 0;
        height: 60px; z-index: 1000;
        background-color: #FAE8D9;
        border-bottom: 1px solid #EED7CA;
        display: flex; align-items: center;
        padding: 0 24px;
    }
    .topbar-fixed .brand {
        display: flex; align-items: center; gap: 10px;
        font-size: 22px; font-weight: 800; color: #4B3832;
        letter-spacing: -0.2px;
    }
    .topbar-fixed .logo { font-size: 26px; }

    /* 본문이 상단바에 가리지 않도록 여백 */
    .main-block { margin-top: 76px; } /* 60px + 여유 */

    /* ---------- 히어로 영역(상단) ---------- */
    .hero{
        position:relative;
        background: radial-gradient(1200px 600px at 10% -20%, #FFEDE2 0%, rgba(255, 237, 226, 0) 60%),
                    linear-gradient(180deg, #FFF7F2 0%, #FFEFE6 100%);
        border:1px solid var(--line);
        border-radius:24px;
        box-shadow: var(--shadow);
        padding:28px 32px;
        overflow:hidden;
    }
    .hero:before{
        content:"";
        position:absolute; inset:-20px;
        background-image: radial-gradient(1px 1px at 20% 30%, rgba(207,161,141,.28) 0, transparent 60%),
                          radial-gradient(1px 1px at 60% 70%, rgba(207,161,141,.22) 0, transparent 60%),
                          radial-gradient(1px 1px at 80% 20%, rgba(207,161,141,.18) 0, transparent 60%);
        opacity:.6; pointer-events:none;
    }
    .hero-grid{
        display:grid; grid-template-columns: 1.6fr .9fr; gap:28px; align-items:center;
    }
    .brand{
        display:flex; align-items:center; gap:12px; margin-bottom:6px;
    }
    .brand .logo{
        width:44px; height:44px; border-radius:12px; display:flex; align-items:center; justify-content:center;
        background:#FCE9E1; border:1px solid var(--line); box-shadow:0 4px 12px rgba(79,56,50,.08); font-size:22px;
    }
    .brand .name{
        font-size:26px; font-weight:800; letter-spacing:-.2px;
    }
    .tagline{
        font-size:16px; color:#6C5149; margin-bottom:14px;
    }
    .badges{ display:flex; gap:10px; flex-wrap:wrap; }
    .badge{
        display:inline-flex; align-items:center; gap:8px;
        padding:6px 10px; border-radius:999px; font-weight:700; font-size:13px;
        background:#fff; border:1px solid var(--line); box-shadow:0 2px 8px rgba(79,56,50,.05);
        color:#5A3E36;
    }
    .badge .dot{ width:8px; height:8px; border-radius:50%; background:var(--accent); box-shadow:0 0 0 3px rgba(207,161,141,.18) inset; }

    .hero-visual{
        display:flex; align-items:center; justify-content:center;
    }
    .kv{
        width:180px; height:180px; border-radius:50%;
        background:#fff; border:6px solid #F3E2D8; box-shadow: var(--shadow); overflow:hidden;
    }
    .kv img{ width:100%; height:100%; object-fit:cover; display:block; }

    .nav-divider{ height:10px; }

    /* ---------- 방명록 카드 ---------- */
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

    /* ---------- 탭 헤더(센터/균등) ---------- */
    div[data-baseweb="tab-list"]{ justify-content:center !important; gap:12px !important; width:100% !important; }
    button[role="tab"]{
        min-width: 220px; /* 탭 가로폭 일정 */
        text-align:center !important; border-radius
