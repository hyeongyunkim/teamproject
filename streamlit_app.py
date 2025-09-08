import streamlit as st
import os
import hashlib
import base64
import mimetypes
from datetime import datetime
import html
import json
from openai import OpenAI

# -------------------- 기본 설정 --------------------
st.set_page_config(page_title="반려동물 추모관", page_icon="🐾", layout="wide")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------------------- 경로 --------------------
UPLOAD_FOLDER = "uploaded_images"
CONVERTED_FOLDER = "converted_images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

BASE_IMG_URL = "https://github.com/hyeongyunkim/teamproject/raw/main/petfuneral.png"
INFO_PATH = "memorial_info.json"

# -------------------- 유틸 함수 --------------------
def list_uploaded_images():
    files = []
    for folder in [UPLOAD_FOLDER, CONVERTED_FOLDER]:
        if os.path.exists(folder):
            files += [
                os.path.join(folder, f)
                for f in os.listdir(folder)
                if f.lower().endswith((".png", ".jpg", ".jpeg"))
            ]
    return sorted(files)

def initials_from_name(name: str) -> str:
    name = name.strip()
    return "🕊️" if not name else name[0].upper()

def file_sha256(byte_data: bytes) -> str:
    return hashlib.sha256(byte_data).hexdigest()

def img_file_to_data_uri(path: str) -> str:
    mime, _ = mimetypes.guess_type(path)
    if mime is None:
        mime = "image/jpeg"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}"

# -------------------- CSS --------------------
st.markdown("""
<style>
:root{
    --bg:#FDF6EC; --ink:#4B3832; --accent:#CFA18D;
    --accent-2:#FAE8D9; --line:#EED7CA;
    --shadow:0 10px 24px rgba(79,56,50,0.12);
}
body { background-color: var(--bg); color: var(--ink); }
h1,h2,h3 { color: var(--ink) !important; }

/* ===== 상단 고정 바 ===== */
.topbar-fixed {
    position: fixed; top: 0; left: 0; right: 0; height: 60px;
    background-color: #FAE8D9; border-bottom: 1px solid #EED7CA;
    display: flex; align-items: center; padding: 0 24px; z-index: 1000;
}
.topbar-fixed .brand {
    font-size: 28px; font-weight: 900; color: #4B3832;
}

/* 본문 */
.main-block { margin-top: 74px; }

/* 버튼 */
.stButton>button{
    background: var(--accent); color:#fff; border:none; border-radius:12px;
    padding:8px 16px; font-weight:600; transition:.15s;
    box-shadow:0 3px 10px rgba(207,161,141,.25);
}
.stButton>button:hover{ filter: brightness(1.05); transform: translateY(-1px); }

.stTextInput>div>div>input, .stTextArea textarea{
    background:#fff; border:1px solid var(--line); border-radius:12px;
}

.page-wrap{ max-width:1180px; margin:0 auto; }

/* 히어로 */
.hero{
    background: linear-gradient(180deg, #FFF7F2 0%, #FFEFE6 100%);
    border:1px solid var(--line); border-radius:24px;
    box-shadow: var(--shadow); padding:28px 32px;
}
.hero-grid{
    display:grid; grid-template-columns: 1.6fr .9fr; gap:28px; align-items:center;
}
.hero-logo{ font-size:26px; font-weight:900; color:#4B3832; }
.tagline{ font-size:18px; color:#6C5149; margin-bottom:14px; }
.badges{ display:flex; gap:10px; flex-wrap:wrap; }
.badge{
    padding:6px 10px; border-radius:999px; font-weight:700; font-size:13px;
    background:#fff; border:1px solid var(--line);
    box-shadow:0 2px 8px rgba(79,56,50,.05); color:#5A3E36;
}
.badge .dot{ width:8px; height:8px; border-radius:50%; background: var(--accent); }

/* 방명록 카드 */
.guest-card{
    background: linear-gradient(180deg, #FFF8F1 0%, #FFFFFF 100%);
    border: 1px solid var(--line); border-left: 6px solid var(--accent);
    border-radius: 14px; padding: 14px 16px; margin: 10px 0 16px 0;
    box-shadow: 0 4px 10px rgba(79,56,50,0.08);
}
.guest-avatar{ width:34px; height:34px; border-radius:50%; background:#F0D9CF;
    color:#4B3832; display:flex; align-items:center; justify-content:center; font-weight:700; }

/* 갤러리 */
.photo-frame{
    background:#fff; border: 6px solid #F3E2D8;
    box-shadow: 0 8px 18px rgba(79,56,50,0.12);
    border-radius:16px; padding:10px; margin-bottom:12px;
}
.photo-frame .thumb{
    width:70%; display:block; border-radius:10px; margin:0 auto;
}
</style>
""", unsafe_allow_html=True)

# -------------------- 상단 고정 브랜드 바 --------------------
st.markdown("""
<div class="topbar-fixed">
  <div class="brand">🐾 Pet Memorilization 🐾</div>
</div>
""", unsafe_allow_html=True)

# -------------------- 본문 시작 --------------------
st.markdown('<div class="main-block">', unsafe_allow_html=True)

# -------------------- 부고 정보 --------------------
default_name = "초코"
default_birth = datetime(2015, 3, 15).date()
default_pass  = datetime(2024, 8, 10).date()

if os.path.exists(INFO_PATH):
    try:
        with open(INFO_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            default_name = data.get("name", default_name)
            if data.get("birth"):
                default_birth = datetime.strptime(data["birth"], "%Y-%m-%d").date()
            if data.get("pass"):
                default_pass  = datetime.strptime(data["pass"], "%Y-%m-%d").date()
    except Exception:
        pass

st.sidebar.title("📜 부고 정보 입력")
pet_name = st.sidebar.text_input("반려동물 이름", value=default_name)
birth_date = st.sidebar.date_input("태어난 날", value=default_birth)
pass_date = st.sidebar.date_input("무지개다리 건넌 날", value=default_pass)

if st.sidebar.button("저장하기"):
    with open(INFO_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "name": (pet_name or "").strip() or default_name,
            "birth": birth_date.isoformat(),
            "pass":  pass_date.isoformat()
        }, f, ensure_ascii=False, indent=2)
    st.sidebar.success("저장 완료!")
    st.rerun()

# -------------------- 히어로 영역 --------------------
try:
    with open("guestbook.txt", "r", encoding="utf-8") as f:
        guest_lines = [ln for ln in f.readlines() if ln.strip()]
except FileNotFoundError:
    guest_lines = []

photo_count = len(list_uploaded_images())
message_count = len(guest_lines)

st.markdown(f"""
<div class="hero">
  <div class="hero-grid">
    <div>
      <div class="hero-logo">🐾 Pet Memorialization 🐾</div>
      <div class="tagline">소중한 반려동물을 추모하는 공간</div>
      <div class="badges">
        <span class="badge"><span class="dot"></span> 사진 {photo_count}장</span>
        <span class="badge"><span class="dot"></span> 방명록 {message_count}개</span>
      </div>
    </div>
    <div class="hero-visual">
      <div class="kv">
        <img src="{BASE_IMG_URL}" alt="memorial">
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# -------------------- 탭 --------------------
tab1, tab2, tab3 = st.tabs(["📜 부고장/방명록/추모관", "📺 스트리밍", "💐 기부/꽃바구니"])

# ==================== ① 부고장/방명록/추모관 ====================
with tab1:
    st.markdown("<h2 style='text-align:center;'>In Loving Memory</h2>", unsafe_allow_html=True)

    # --- 대표 이미지 캐러셀 ---
    img_list = list_uploaded_images()
    n = len(img_list)
    if "carousel_idx" not in st.session_state: st.session_state.carousel_idx = 0
    if n > 0:
        st.session_state.carousel_idx %= n
        prev, mid, nxt = st.columns([1,6,1])
        with prev:
            if st.button("◀"): st.session_state.carousel_idx = (st.session_state.carousel_idx - 1) % n
        with mid:
            current = img_list[st.session_state.carousel_idx]
            data_uri = img_file_to_data_uri(current)
            st.markdown(f"""
                <div class="photo-frame" style="max-width:720px;margin:0 auto 10px;">
                    <img class="thumb" src="{data_uri}">
                </div>
            """, unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;'><b>{st.session_state.carousel_idx+1}/{n}</b></p>", unsafe_allow_html=True)
        with nxt:
            if st.button("▶"): st.session_state.carousel_idx = (st.session_state.carousel_idx + 1) % n
    else:
        st.info("대표 사진이 없습니다. 온라인 추모관에서 사진을 업로드하세요.")

    # --- 부고장 ---
    st.subheader("📜 부고장")
    safe_name = html.escape((pet_name or "").strip() or default_name)
    st.markdown(f"""
    <div style="text-align:center; background-color:#FAE8D9; padding:15px; border-radius:15px; margin:10px;">
    사랑하는 <b>{safe_name}</b> 이(가) 무지개다리를 건넜습니다.<br>
    함께한 시간들을 기억하며 따뜻한 마음으로 추모해주세요.
    <br><br>
    🐾 <b>태어난 날:</b> {birth_date.isoformat()} <br>
    🌈 <b>무지개다리 건넌 날:</b> {pass_date.isoformat()}
    </div>
    """, unsafe_allow_html=True)

    # --- 방명록 ---
    st.subheader("✍️ 방명록")
    name = st.text_input("이름")
    message = st.text_area("메시지")
    if st.button("추모 메시지 남기기"):
        if name and message:
            with open("guestbook.txt", "a", encoding="utf-8") as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|{name}|{message}\n")
            st.success("메시지가 등록되었습니다.")
            st.rerun()

    st.subheader("📖 추모 메시지 모음")
    if guest_lines:
        for idx, line in enumerate(reversed(guest_lines)):
            try: time_str, user, msg = line.strip().split("|", 2)
            except: continue
            col_msg, col_btn = st.columns([6,1])
            with col_msg:
                st.markdown(f"""
                <div class="guest-card">
                  <div class="guest-card-header">
                    <div class="guest-avatar">{html.escape(initials_from_name(user))}</div>
                    <div class="guest-name-time">
                      <span class="guest-name">🕊️ {html.escape(user)}</span>
                      <span class="guest-time">{html.escape(time_str)}</span>
                    </div>
                  </div>
                  <div class="guest-msg">{html.escape(msg)}</div>
                </div>
                """, unsafe_allow_html=True)
            with col_btn:
                if st.button("삭제", key=f"delmsg{idx}"):
                    real_idx = len(guest_lines)-1-idx
                    del guest_lines[real_idx]
                    with open("guestbook.txt","w",encoding="utf-8") as f: f.writelines(guest_lines)
                    st.rerun()
    else:
        st.info("아직 메시지가 없습니다.")

    # --- 온라인 추모관 ---
    st.subheader("🖼️ 온라인 추모관")
    with st.form("gallery_upload", clear_on_submit=True):
        uploaded_files = st.file_uploader("사진 업로드", type=["png","jpg","jpeg"], accept_multiple_files=True)
        submit = st.form_submit_button("업로드")
    if submit and uploaded_files:
        for uploaded_file in uploaded_files:
            data = uploaded_file.getvalue()
            digest = file_sha256(data)[:16]
            safe_name_file = "".join(c for c in uploaded_file.name if c not in "\\/:*?\"<>|")
            filename = f"{digest}_{safe_name_file}"
            with open(os.path.join(UPLOAD_FOLDER, filename), "wb") as f: f.write(data)
        st.rerun()

    image_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.lower().endswith((".png",".jpg",".jpeg"))]
    for idx, img_file in enumerate(image_files):
        img_path = os.path.join(UPLOAD_FOLDER, img_file)
        cols = st.columns([2,1])
        with cols[0]: st.image(img_path, caption="원본 사진", use_container_width=True)
        with cols[1]:
            if st.button("AI 변환", key=f"convert{idx}"):
                try:
                    with open(img_path,"rb") as f:
                        response = client.images.edit(
                            model="gpt-image-1",
                            image=f,
                            prompt="귀여운 그림 느낌의 반려동물 추모 사진. 따뜻하고 밝은 색감.",
                            size="512x512"
                        )
                    b64_img = response.data[0].b64_json
                    img_bytes = base64.b64decode(b64_img)
                    new_filename = f"converted_{img_file}"
                    save_path = os.path.join(CONVERTED_FOLDER, new_filename)
                    with open(save_path,"wb") as out: out.write(img_bytes)
                    st.success("변환 완료! 캐러셀에서도 볼 수 있습니다.")
                    st.rerun()
                except Exception as e:
                    st.error(f"변환 실패: {e}")

# ==================== ② 스트리밍 ====================
with tab2:
    st.header("📺 장례식 스트리밍")
    video_url = st.text_input("YouTube URL", "https://www.youtube.com/embed/dQw4w9WgXcQ")
    st.markdown(f"<div style='text-align:center;'><iframe width='560' height='315' src='{video_url}' frameborder='0' allowfullscreen></iframe></div>", unsafe_allow_html=True)

# ==================== ③ 기부/꽃바구니 ====================
with tab3:
    st.header("💐 조문객 기부 / 꽃바구니 주문")
    st.markdown("- 💳 기부: 카카오페이 / 토스 / 계좌이체\n- 🌹 꽃바구니 주문: 온라인 꽃집 링크 연결")
    link = st.text_input("꽃바구니 주문 링크", "https://www.naver.com")
    st.markdown(f"<div style='text-align:center;'><a href='{link}' target='_blank' style='font-size:18px; color:#CFA18D; font-weight:bold;'>👉 꽃바구니 주문하기</a></div>", unsafe_allow_html=True)
