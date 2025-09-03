import streamlit as st
import os
import hashlib
import base64
import mimetypes
from datetime import datetime
import html
import json

# -------------------- 페이지 기본 설정 --------------------
st.set_page_config(page_title="반려동물 추모관", page_icon="🐾", layout="wide")

# -------------------- 색감/스타일 --------------------
st.markdown("""
    <style>
    :root{
        --bg:#FDF6EC; --ink:#4B3832; --accent:#CFA18D; --accent-2:#FAE8D9; --line:#EED7CA;
        --shadow:0 10px 24px rgba(79,56,50,0.12);
    }
    body { background-color: var(--bg); color: var(--ink); }
    h1,h2,h3 { color: var(--ink) !important; }

    .topbar-fixed {
        position: fixed; top: 0; left: 0; right: 0; height: 60px;
        background-color: #FAE8D9; border-bottom: 1px solid #EED7CA;
        display: flex; align-items: center; justify-content:flex-start;
        padding: 0 24px; z-index: 1000;
    }
    .topbar-fixed .brand {
        display: flex; align-items: center; gap: 10px;
        font-size: 28px; font-weight: 900; color: #4B3832;
    }
    .main-block { margin-top: 74px; }

    .stButton>button{
        background: var(--accent); color:#fff; border:none; border-radius:12px;
        padding:6px 14px; font-weight:600;
        box-shadow:0 3px 10px rgba(207,161,141,.25);
    }
    .stButton>button:hover{ filter: brightness(1.05); }

    .page-wrap{ max-width:1180px; margin:0 auto; }

    .hero{
        border:1px solid var(--line); border-radius:24px;
        box-shadow: var(--shadow); padding:24px 28px;
        background: linear-gradient(180deg, #FFF7F2 0%, #FFEFE6 100%);
    }
    .hero-grid{
        display:grid; grid-template-columns: 1.6fr 1fr; gap:20px; align-items:flex-start;
    }
    .hero-logo{ font-size:26px; font-weight:900; color:#4B3832; margin-bottom:8px; }
    .tagline{ font-size:18px; color:#6C5149; margin-bottom:14px; }
    .badges{ display:flex; gap:10px; flex-wrap:wrap; margin-bottom:10px; }
    .badge{
        display:inline-flex; align-items:center; gap:6px;
        padding:4px 10px; border-radius:999px; font-weight:600; font-size:13px;
        background:#fff; border:1px solid var(--line); color:#5A3E36;
    }
    .badge .dot{ width:8px; height:8px; border-radius:50%; background:var(--accent); }

    .kv{ width:160px; height:160px; border-radius:50%; overflow:hidden; margin:0 auto 12px; border:5px solid #F3E2D8; }
    .kv img{ width:100%; height:100%; object-fit:cover; }

    .guest-card{
        background: #fff; border:1px solid var(--line); border-left:6px solid var(--accent);
        border-radius: 12px; padding: 12px 14px; margin: 8px 0 12px 0;
        box-shadow: 0 2px 6px rgba(79,56,50,0.08);
    }
    .guest-avatar{ width:30px; height:30px; border-radius:50%; background:#F0D9CF;
        display:flex; align-items:center; justify-content:center; font-weight:700; }
    .guest-name{ font-weight:700; }
    .guest-time{ font-size:12px; color:#8B6F66; }
    .photo-frame{
        background:#fff; border: 5px solid #F3E2D8; border-radius:14px;
        padding:6px; margin-bottom:12px; box-shadow:0 4px 10px rgba(79,56,50,0.1);
    }
    .photo-frame .thumb{ width:100%; height:auto; border-radius:10px; }
    </style>
""", unsafe_allow_html=True)

# -------------------- 상단 고정 브랜드 바 --------------------
st.markdown("""
<div class="topbar-fixed">
  <div class="brand">🐾&nbsp; Pet Memorilization &nbsp;🐾</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="main-block">', unsafe_allow_html=True)

# -------------------- 유틸 --------------------
UPLOAD_FOLDER = "uploaded_images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

BASE_IMG_URL = "https://github.com/hyeongyunkim/teamproject/raw/main/petfuneral.png"
INFO_PATH = "memorial_info.json"

def list_uploaded_images():
    return sorted([f for f in os.listdir(UPLOAD_FOLDER) if f.lower().endswith((".png",".jpg",".jpeg"))])

def initials_from_name(name): return "🕊️" if not name.strip() else name.strip()[0].upper()

def file_sha256(b): return hashlib.sha256(b).hexdigest()

def img_file_to_data_uri(path):
    mime,_=mimetypes.guess_type(path)
    if mime is None: mime="image/jpeg"
    with open(path,"rb") as f: b64=base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}"

# -------------------- 부고정보 로드 --------------------
default_name="초코"
default_birth=datetime(2015,3,15).date()
default_pass=datetime(2024,8,10).date()
if os.path.exists(INFO_PATH):
    try:
        with open(INFO_PATH,"r",encoding="utf-8") as f:
            data=json.load(f)
            default_name=data.get("name",default_name)
            if data.get("birth"): default_birth=datetime.strptime(data["birth"],"%Y-%m-%d").date()
            if data.get("pass"): default_pass=datetime.strptime(data["pass"],"%Y-%m-%d").date()
    except: pass

# -------------------- 히어로 영역 --------------------
try:
    with open("guestbook.txt","r",encoding="utf-8") as f:
        guest_lines=[ln for ln in f.readlines() if ln.strip()]
except FileNotFoundError: guest_lines=[]
photo_count=len(list_uploaded_images()); message_count=len(guest_lines)

st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
col1,col2=st.columns([1.6,1])
with col1:
    st.markdown(f"""
    <div class="hero">
      <div class="hero-logo">🐾 Pet Memorialization 🐾</div>
      <div class="tagline">소중한 반려동물을 추모하는 공간</div>
      <div class="badges">
        <span class="badge"><span class="dot"></span> 사진 {photo_count}장</span>
        <span class="badge"><span class="dot"></span> 방명록 {message_count}개</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("<div class='hero'>", unsafe_allow_html=True)
    st.markdown(f"<div class='kv'><img src='{BASE_IMG_URL}'></div>", unsafe_allow_html=True)
    st.markdown("**📜 부고 정보 입력**")
    pet_name=st.text_input("반려동물 이름",value=default_name)
    birth_date=st.date_input("태어난 날",value=default_birth,format="YYYY-MM-DD")
    pass_date=st.date_input("무지개다리 건넌 날",value=default_pass,format="YYYY-MM-DD")
    if st.button("부고 정보 저장"):
        with open(INFO_PATH,"w",encoding="utf-8") as f:
            json.dump({"name":pet_name.strip(),"birth":birth_date.isoformat(),"pass":pass_date.isoformat()},f,ensure_ascii=False,indent=2)
        st.success("저장 완료!"); st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# -------------------- 탭 --------------------
tab1,tab2,tab3=st.tabs(["📜 부고장/방명록/추모관","📺 장례식 스트리밍","💐 기부/꽃바구니"])

with tab1:
    st.subheader("📜 부고장")
    safe_name=html.escape(pet_name or default_name)
    st.markdown(f"""
    <div style="text-align:center;background:#FAE8D9;padding:15px;border-radius:15px;">
      사랑하는 <b>{safe_name}</b> 이(가) 무지개다리를 건넜습니다.<br>
      함께한 시간들을 기억하며 따뜻한 마음으로 추모해주세요.<br><br>
      🐾 <b>태어난 날:</b> {birth_date.isoformat()}<br>
      🌈 <b>무지개다리 건넌 날:</b> {pass_date.isoformat()}
    </div>""",unsafe_allow_html=True)

    st.subheader("✍️ 방명록")
    name=st.text_input("이름")
    msg=st.text_area("메시지")
    if st.button("추모 메시지 남기기"):
        if name and msg:
            with open("guestbook.txt","a",encoding="utf-8") as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|{name}|{msg}\n")
            st.success("메시지 등록됨"); st.rerun()
        else: st.warning("이름과 메시지를 입력해주세요.")

    st.subheader("📖 추모 메시지 모음")
    if not guest_lines: st.info("아직 등록된 메시지가 없습니다.")
    else:
        for idx,line in enumerate(reversed(guest_lines)):
            try: t,u,m=line.strip().split("|",2)
            except: continue
            c1,c2=st.columns([6,1])
            with c1:
                st.markdown(f"""
                <div class="guest-card">
                  <div style="display:flex;gap:10px;align-items:center;">
                    <div class="guest-avatar">{html.escape(initials_from_name(u))}</div>
                    <div><div class="guest-name">🕊️ {html.escape(u)}</div>
                    <div class="guest-time">{html.escape(t)}</div></div>
                  </div>
                  <div class="guest-msg">{html.escape(m)}</div>
                </div>""",unsafe_allow_html=True)
            with c2:
                if st.button("삭제",key=f"delmsg_{idx}"):
                    real_idx=len(guest_lines)-1-idx
                    del guest_lines[real_idx]
                    with open("guestbook.txt","w",encoding="utf-8") as f: f.writelines(guest_lines)
                    st.rerun()

    st.subheader("🖼️ 온라인 추모관")
    with st.form("gallery_upload",clear_on_submit=True):
        files=st.file_uploader("사진 업로드",type=["png","jpg","jpeg"],accept_multiple_files=True)
        submit=st.form_submit_button("업로드")
    if submit and files:
        saved,dup=0,0
        for f in files:
            data=f.getvalue();digest=file_sha256(data)[:16]
            if any(fn.startswith(digest+"_") for fn in os.listdir(UPLOAD_FOLDER)): dup+=1;continue
            fname="".join(c for c in f.name if c not in "\\/:*?\"<>|")
            with open(os.path.join(UPLOAD_FOLDER,f"{digest}_{fname}"),"wb") as out: out.write(data)
            saved+=1
        if saved: st.success(f"{saved}장 업로드 완료!")
        if dup: st.info(f"{dup}장 중복 제외")
        st.rerun()
    imgs=list_uploaded_images()
    if imgs:
        cols=st.columns(3)
        for i,img in enumerate(imgs):
            with cols[i%3]:
                data_uri=img_file_to_data_uri(os.path.join(UPLOAD_FOLDER,img))
                st.markdown(f"<div class='photo-frame'><img class='thumb' src='{data_uri}'></div>",unsafe_allow_html=True)
                if st.button("삭제",key=f"delimg_{i}"):
                    os.remove(os.path.join(UPLOAD_FOLDER,img)); st.rerun()
    else: st.info("아직 업로드된 사진이 없습니다.")

with tab2:
    st.header("📺 장례식 실시간 스트리밍")
    url=st.text_input("YouTube URL","https://www.youtube.com/embed/dQw4w9WgXcQ")
    st.markdown(f"<div style='text-align:center;'><iframe width='560' height='315' src='{url}' frameborder='0' allowfullscreen></iframe></div>",unsafe_allow_html=True)

with tab3:
    st.header("💐 조문객 기부 / 꽃바구니 주문")
    st.markdown("- 💳 기부: 카카오페이 / 토스 / 계좌이체\n- 🌹 꽃바구니 주문: 온라인 꽃집 링크")
    link=st.text_input("꽃바구니 주문 링크","https://www.naver.com")
    st.markdown(f"<div style='text-align:center;'><a href='{link}' target='_blank' style='font-size:18px;color:#CFA18D;font-weight:bold;'>👉 꽃바구니 주문하러 가기</a></div>",unsafe_allow_html=True)
