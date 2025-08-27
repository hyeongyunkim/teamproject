import streamlit as st
import os
import hashlib
import base64
import mimetypes
from datetime import datetime
import html

# -------------------- 기본 설정 --------------------
st.set_page_config(page_title="Forever Pet - 반려견 추모관", page_icon="🐾", layout="wide")

# -------------------- 스타일 --------------------
st.markdown("""
    <style>
    :root {
        --bg:#FDF6EC; --ink:#4B3832; --accent:#CFA18D; --line:#EED7CA;
    }
    body { background:var(--bg); color:var(--ink); }

    /* 상단 고정 로고바 */
    .topbar-fixed {
        position:fixed; top:0; left:0; right:0; height:60px;
        background:#FAE8D9; border-bottom:1px solid var(--line);
        display:flex; align-items:center; padding:0 24px; z-index:1000;
    }
    .topbar-fixed .brand { display:flex; align-items:center; gap:8px; font-size:22px; font-weight:800; color:var(--ink);}
    .main-block { margin-top:74px; }

    /* 버튼 */
    .stButton>button {
        background:var(--accent); color:#fff; border:none; border-radius:12px;
        padding:8px 16px; font-weight:600;
    }

    /* 방명록 카드 */
    .guest-card { background:#fff; border:1px solid var(--line); border-left:6px solid var(--accent);
        border-radius:12px; padding:12px; margin:10px 0; }
    .guest-avatar { width:34px; height:34px; border-radius:50%; background:#F0D9CF;
        display:flex; align-items:center; justify-content:center; font-weight:700; color:var(--ink);}
    .guest-msg { margin-top:6px; font-size:15px; }

    /* 갤러리 */
    .photo-frame { background:#fff; border:6px solid #F3E2D8; border-radius:12px; margin-bottom:12px; }
    .photo-frame .thumb { width:85%; aspect-ratio:1/1; object-fit:cover; display:block; margin:0 auto; border-radius:10px;}
    </style>
""", unsafe_allow_html=True)

# -------------------- 상단 로고 --------------------
st.markdown("""
<div class="topbar-fixed">
  <div class="brand"><span class="logo">🐾</span> Forever Pet</div>
</div>
""", unsafe_allow_html=True)
st.markdown('<div class="main-block">', unsafe_allow_html=True)

# -------------------- 유틸 --------------------
UPLOAD_FOLDER = "uploaded_images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
BASE_IMG_URL = "https://github.com/hyeongyunkim/teamproject/raw/main/petfuneral.png"

def list_uploaded_images():
    return sorted([f for f in os.listdir(UPLOAD_FOLDER) if f.lower().endswith((".png",".jpg",".jpeg"))])

def initials_from_name(name:str)->str:
    return "🕊️" if not name else name[0].upper()

def file_sha256(b:bytes)->str:
    return hashlib.sha256(b).hexdigest()

def img_file_to_data_uri(path:str)->str:
    mime,_=mimetypes.guess_type(path)
    if mime is None: mime="image/jpeg"
    with open(path,"rb") as f:
        return f"data:{mime};base64,{base64.b64encode(f.read()).decode()}"

# -------------------- PC=탭 / 모바일=드롭다운 --------------------
# 화면 너비를 JS로 가져올 수 없으니 Streamlit에서는 간단히 선택 UI 제공
menu_options = ["📜 부고장/방명록/추모관","📺 장례식 스트리밍","💐 기부/꽃바구니"]
# PC → tabs / Mobile → selectbox
if st.session_state.get("force_mobile", False):
    choice = st.selectbox("메뉴 선택", menu_options)
else:
    t1,t2,t3 = st.tabs(menu_options)
    choice = st.session_state.get("active_tab","📜 부고장/방명록/추모관")
    if t1: choice="📜 부고장/방명록/추모관"
    if t2: choice="📺 장례식 스트리밍"
    if t3: choice="💐 기부/꽃바구니"

# ==================== ① 추모관 ====================
if choice=="📜 부고장/방명록/추모관":
    st.header("📜 부고장")
    st.markdown("""
    <div style="text-align:center; background:#FAE8D9; padding:15px; border-radius:12px;">
      사랑하는 반려견 <b>초코</b>가 무지개다리를 건넜습니다.<br>
      함께한 시간들을 기억하며 따뜻한 마음으로 추모해주세요.<br><br>
      🐾 태어난 날: 2015-03-15 <br>
      🌈 무지개다리 건넌 날: 2024-08-10
    </div>
    """, unsafe_allow_html=True)

    st.subheader("✍️ 방명록")
    name=st.text_input("이름")
    msg=st.text_area("메시지")
    if st.button("추모 메시지 남기기"):
        if name and msg:
            with open("guestbook.txt","a",encoding="utf-8") as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|{name}|{msg}\n")
            st.success("등록되었습니다."); st.rerun()

    st.subheader("📖 추모 메시지 모음")
    try: lines=open("guestbook.txt","r",encoding="utf-8").read().splitlines()
    except FileNotFoundError: lines=[]
    for line in reversed(lines):
        try: t,u,m=line.split("|",2)
        except: continue
        st.markdown(f"""
        <div class="guest-card">
          <div class="guest-avatar">{initials_from_name(u)}</div>
          <div><b>{u}</b> <small>{t}</small></div>
          <div class="guest-msg">{html.escape(m)}</div>
        </div>
        """, unsafe_allow_html=True)

    st.subheader("🖼️ 온라인 추모관")
    with st.form("gallery", clear_on_submit=True):
        files=st.file_uploader("사진 업로드", type=["png","jpg","jpeg"], accept_multiple_files=True)
        submit=st.form_submit_button("업로드")
    if submit and files:
        for f in files:
            data=f.getvalue(); digest=file_sha256(data)[:16]
            if not any(x.startswith(digest+"_") for x in os.listdir(UPLOAD_FOLDER)):
                safe="".join(c for c in f.name if c not in "\\/:*?\"<>|")
                with open(os.path.join(UPLOAD_FOLDER,f"{digest}_{safe}"),"wb") as out: out.write(data)
        st.rerun()
    imgs=list_uploaded_images()
    if imgs:
        cols=st.columns(3)
        for i,img in enumerate(imgs):
            with cols[i%3]:
                st.markdown(f"""
                <div class="photo-frame">
                  <img class="thumb" src="{img_file_to_data_uri(os.path.join(UPLOAD_FOLDER,img))}">
                </div>""", unsafe_allow_html=True)
                if st.button("삭제",key=f"del{i}"): os.remove(os.path.join(UPLOAD_FOLDER,img)); st.rerun()

# ==================== ② 스트리밍 ====================
elif choice=="📺 장례식 스트리밍":
    st.header("📺 장례식 실시간 스트리밍")
    url=st.text_input("YouTube 영상 URL","https://www.youtube.com/embed/dQw4w9WgXcQ")
    st.markdown(f"<div style='text-align:center'><iframe width='100%' height='315' src='{url}'></iframe></div>", unsafe_allow_html=True)

# ==================== ③ 기부 ====================
elif choice=="💐 기부/꽃바구니":
    st.header("💐 기부/꽃바구니 주문")
    link=st.text_input("꽃바구니 주문 링크","https://www.naver.com")
    st.markdown(f"<a href='{link}' target='_blank' style='font-size:18px;color:#CFA18D;font-weight:bold;'>👉 꽃바구니 주문하기</a>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
