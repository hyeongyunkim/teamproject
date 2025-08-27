import streamlit as st
import os
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

    /* ===== 상단 고정 브랜드 바 ===== */
    .topbar-fixed {
        position: fixed; top: 0; left: 0; right: 0; height: 60px;
        background-color: #FAE8D9; border-bottom: 1px solid #EED7CA;
        display: flex; align-items: center; padding: 0 24px; z-index: 1000;
    }
    .topbar-fixed .brand {
        display: flex; align-items: center; gap: 10px;
        font-size: 22px; font-weight: 800; color: #4B3832;
        letter-spacing: -0.2px;
    }
    .topbar-fixed .logo { font-size: 26px; }
    /* 본문이 가려지지 않도록 여백 */
    .main-block { margin-top: 74px; }

    /* 공통 버튼 */
    .stButton>button{
        background: var(--accent); color:#fff; border:none; border-radius:12px;
        padding:8px 16px; font-weight:600; transition:.15s;
        box-shadow:0 3px 10px rgba(207,161,141,.25);
    }
    .stButton>button:hover{ filter: brightness(1.03); transform: translateY(-1px); }

    .stTextInput>div>div>input, .stTextArea textarea{
        background:#fff; border:1px solid var(--line); border-radius:12px;
    }

    .page-wrap{ max-width:1180px; margin:0 auto; }

    /* ---------- 히어로 영역 ---------- */
    .hero{
        position:relative;
        background: radial-gradient(1200px 600px at 10% -20%, #FFEDE2 0%, rgba(255, 237, 226, 0) 60%),
                    linear-gradient(180deg, #FFF7F2 0%, #FFEFE6 100%);
        border:1px solid var(--line);
        border-radius:24px;
        box-shadow: var(--shadow);
        padding:28px 32px;
    }
    .hero-grid{ display:grid; grid-template-columns: 1.6fr .9fr; gap:28px; align-items:center; }
    .tagline{ font-size:18px; color:#6C5149; margin-bottom:14px; }
    .badges{ display:flex; gap:10px; flex-wrap:wrap; }
    .badge{
        display:inline-flex; align-items:center; gap:8px;
        padding:6px 10px; border-radius:999px; font-weight:700; font-size:13px;
        background:#fff; border:1px solid var(--line); box-shadow:0 2px 8px rgba(79,56,50,.05);
        color:#5A3E36;
    }
    .badge .dot{ width:8px; height:8px; border-radius:50%; background:var(--accent); }

    .kv{
        width:180px; height:180px; border-radius:50%;
        background:#fff; border:6px solid #F3E2D8; box-shadow: var(--shadow); overflow:hidden;
    }
    .kv img{ width:100%; height:100%; object-fit:cover; }

    /* ---------- 방명록 카드 ---------- */
    .guest-card{
        background: linear-gradient(180deg, #FFF8F1 0%, #FFFFFF 100%);
        border: 1px solid var(--line);
        border-left: 6px solid var(--accent);
        border-radius: 14px; padding: 14px 16px; margin: 10px 0 16px 0;
        box-shadow: 0 4px 10px rgba(79, 56, 50, 0.08);
    }
    .guest-card-header{ display:flex; align-items:center; gap:10px; margin-bottom: 8px; }
    .guest-avatar{ width:34px; height:34px; border-radius:50%; background:#F0D9CF; display:flex; align-items:center; justify-content:center; }
    .guest-name-time{ display:flex; flex-direction:column; line-height:1.2; }

    /* ---------- 갤러리 ---------- */
    .photo-frame{
        background:#fff; border: 6px solid #F3E2D8;
        box-shadow: 0 8px 18px rgba(79,56,50,0.12);
        border-radius:16px; padding:10px; margin-bottom:12px;
    }
    .photo-frame .thumb{
        width:85%; aspect-ratio:1/1; object-fit:cover; display:block; border-radius:10px; margin:0 auto;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------- 상단 고정 브랜드 바 --------------------
st.markdown("""
<div class="topbar-fixed">
  <div class="brand"><span class="logo">🐾</span> Forever Pet</div>
</div>
""", unsafe_allow_html=True)

# 본문 시작
st.markdown('<div class="main-block">', unsafe_allow_html=True)

# -------------------- 유틸 --------------------
UPLOAD_FOLDER = "uploaded_images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
BASE_IMG_URL = "https://github.com/hyeongyunkim/teamproject/raw/main/petfuneral.png"

def list_uploaded_images():
    return sorted([f for f in os.listdir(UPLOAD_FOLDER) if f.lower().endswith((".png",".jpg",".jpeg"))])

def build_image_list():
    return [BASE_IMG_URL] + [os.path.join(UPLOAD_FOLDER, f) for f in list_uploaded_images()]

def file_sha256(data): return hashlib.sha256(data).hexdigest()
def img_file_to_data_uri(path):
    mime,_ = mimetypes.guess_type(path)
    if mime is None: mime="image/jpeg"
    with open(path,"rb") as f: b64=base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}"

# -------------------- 상단 히어로 --------------------
try:
    with open("guestbook.txt","r",encoding="utf-8") as f:
        guest_lines=[ln for ln in f if ln.strip()]
except FileNotFoundError:
    guest_lines=[]
photo_count=len(list_uploaded_images())
message_count=len(guest_lines)

st.markdown(f"""
<div class="page-wrap">
  <div class="hero">
    <div class="hero-grid">
      <div>
        <div class="tagline">소중한 반려견을 추모하는 공간</div>
        <div class="badges">
          <span class="badge"><span class="dot"></span> 사진 {photo_count}장</span>
          <span class="badge"><span class="dot"></span> 방명록 {message_count}개</span>
        </div>
      </div>
      <div class="kv"><img src="{BASE_IMG_URL}" alt="memorial"></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# -------------------- 탭 --------------------
tab1, tab2, tab3 = st.tabs(["📜 추모관", "📺 스트리밍", "💐 기부/꽃바구니"])

# ==================== ① 추모관 ====================
with tab1:
    st.subheader("📜 부고장")
    st.markdown("""<div style="text-align:center; background:#FAE8D9; padding:15px; border-radius:15px;">
    사랑하는 반려견 <b>초코</b> 이(가) 무지개다리를 건넜습니다.<br>🐾 태어난 날: 2015-03-15<br>🌈 무지개다리 건넌 날: 2024-08-10</div>""", unsafe_allow_html=True)

    st.subheader("✍️ 방명록")
    name=st.text_input("이름"); msg=st.text_area("메시지")
    if st.button("추모 메시지 남기기"):
        if name and msg:
            with open("guestbook.txt","a",encoding="utf-8") as f: f.write(f"{datetime.now()}|{name}|{msg}\n")
            st.success("메시지가 등록되었습니다."); st.rerun()
        else: st.warning("이름과 메시지를 입력해주세요.")

    st.subheader("📖 메시지 모음")
    for line in reversed(guest_lines):
        try: time_str,user,msg=line.strip().split("|",2)
        except: continue
        st.markdown(f"""
        <div class="guest-card">
            <div class="guest-card-header"><div class="guest-avatar">🕊️</div>
            <div class="guest-name-time"><b>{html.escape(user)}</b><span>{time_str}</span></div></div>
            <div>{html.escape(msg)}</div>
        </div>
        """, unsafe_allow_html=True)

    st.subheader("🖼️ 온라인 추모관")
    with st.form("gallery_upload",clear_on_submit=True):
        files=st.file_uploader("사진 업로드",type=["png","jpg","jpeg"],accept_multiple_files=True)
        if st.form_submit_button("업로드") and files:
            for f in files:
                data=f.getvalue(); digest=file_sha256(data)[:16]
                if not any(x.startswith(digest+"_") for x in os.listdir(UPLOAD_FOLDER)):
                    with open(os.path.join(UPLOAD_FOLDER,f"{digest}_{f.name}"),"wb") as out: out.write(data)
            st.rerun()
    imgs=list_uploaded_images()
    if imgs:
        cols=st.columns(3)
        for i,f in enumerate(imgs):
            path=os.path.join(UPLOAD_FOLDER,f); data_uri=img_file_to_data_uri(path)
            with cols[i%3]:
                st.markdown(f"<div class='photo-frame'><img class='thumb' src='{data_uri}'></div>",unsafe_allow_html=True)
                if st.button("삭제",key=f"del{i}"): os.remove(path); st.rerun()
    else: st.info("아직 업로드된 사진이 없습니다.")

# ==================== ② 스트리밍 ====================
with tab2:
    url=st.text_input("YouTube 링크","https://www.youtube.com/embed/dQw4w9WgXcQ")
    st.markdown(f"<div style='text-align:center'><iframe width='560' height='315' src='{url}' frameborder='0' allowfullscreen></iframe></div>",unsafe_allow_html=True)

# ==================== ③ 기부 ====================
with tab3:
    link=st.text_input("꽃바구니 주문 링크","https://www.naver.com")
    st.markdown(f"<div style='text-align:center'><a href='{link}' target='_blank'>👉 꽃바구니 주문하기</a></div>",unsafe_allow_html=True)

# -------------------- 플로팅 상담 버튼 --------------------
if "show_fab_menu" not in st.session_state: st.session_state.show_fab_menu=False
st.markdown("""
<style>
.fab-container{position:fixed;bottom:20px;right:20px;z-index:9999;}
.fab-main{width:56px;height:56px;border-radius:50%;background:#CFA18D;color:#fff;font-size:26px;border:none;cursor:pointer;}
.fab-menu{display:flex;flex-direction:column;align-items:flex-end;margin-bottom:8px;}
.fab-menu a{background:#FAE8D9;color:#4B3832;padding:8px 14px;border-radius:20px;margin:4px 0;text-decoration:none;font-weight:600;font-size:14px;border:1px solid #EED7CA;}
</style>
<div class="fab-container">""",unsafe_allow_html=True)
if st.session_state.show_fab_menu:
    st.markdown("""<div class="fab-menu">
        <a href="https://pf.kakao.com/_example" target="_blank">💬 카카오톡 문의</a>
        <a href="tel:010-1234-5678">📞 전화 문의</a>
    </div>""",unsafe_allow_html=True)
if st.button("＋" if not st.session_state.show_fab_menu else "✕",key="fab_main"):
    st.session_state.show_fab_menu=not st.session_state.show_fab_menu
st.markdown("</div>",unsafe_allow_html=True)
