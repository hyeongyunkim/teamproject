import streamlit as st
import os
import hashlib
import base64
import mimetypes
from datetime import datetime
import html  # 메시지 안전 표시용 (특수문자 이스케이프)
import json  # 부고 정보 저장/로드

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

    /* ===== 상단 고정 브랜드 바 ===== */
    .topbar-fixed {
        position: fixed; top: 0; left: 0; right: 0; height: 60px;
        background-color: #FAE8D9; border-bottom: 1px solid #EED7CA;
        display: flex; align-items: center; justify-content:flex-start;
        padding: 0 24px; z-index: 1000;
    }
    .topbar-fixed .brand {
        display: flex; align-items: center; gap: 10px;
        font-size: 28px; font-weight: 900; color: #4B3832;
        letter-spacing: -0.3px;
        line-height:1;
    }
    /* 본문 여백 */
    .main-block { margin-top: 74px; }

    /* 공통 버튼 */
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

    /* ---------- 히어로 영역 ---------- */
    .hero{
        position:relative;
        background: radial-gradient(1200px 600px at 10% -20%, #FFEDE2 0%, rgba(255,237,226,0) 60%),
                    linear-gradient(180deg, #FFF7F2 0%, #FFEFE6 100%);
        border:1px solid var(--line); border-radius:24px;
        box-shadow: var(--shadow); padding:28px 32px;
        overflow:hidden;
    }
    .hero-logo{
        font-size:26px; font-weight:900; color:#4B3832; margin-bottom:8px;
    }
    .tagline{ font-size:18px; color:#6C5149; margin-bottom:14px; }
    .badges{ display:flex; gap:10px; flex-wrap:wrap; }
    .badge{
        display:inline-flex; align-items:center; gap:8px;
        padding:6px 10px; border-radius:999px; font-weight:700; font-size:13px;
        background:#fff; border:1px solid var(--line);
        box-shadow:0 2px 8px rgba(79,56,50,.05); color:#5A3E36;
    }
    .badge .dot{ width:8px; height:8px; border-radius:50%; background: var(--accent);
        box-shadow:0 0 0 3px rgba(207,161,141,.18) inset; }

    .kv{
        width:180px; height:180px; border-radius:50%;
        background:#fff; border:6px solid #F3E2D8; box-shadow: var(--shadow); overflow:hidden;
        margin: 0 auto 10px;
    }
    .kv img{ width:100%; height:100%; object-fit:cover; display:block; }

    /* ---------- 방명록 카드 ---------- */
    .guest-card{
        background: linear-gradient(180deg, #FFF8F1 0%, #FFFFFF 100%);
        border: 1px solid var(--line); border-left: 6px solid var(--accent);
        border-radius: 14px; padding: 14px 16px; margin: 10px 0 16px 0;
        box-shadow: 0 4px 10px rgba(79,56,50,0.08);
    }
    .guest-card-header{ display:flex; align-items:center; gap:10px; margin-bottom: 8px; }
    .guest-avatar{ width:34px; height:34px; min-width:34px; border-radius:50%;
        background:#F0D9CF; color:#4B3832; display:flex; align-items:center; justify-content:center; font-weight:700; }
    .guest-name-time{ display:flex; flex-direction:column; line-height:1.2; }
    .guest-name{ font-weight:700; }
    .guest-time{ font-size:12px; color:#8B6F66; }
    .guest-msg{ font-size:16px; color:#4B3832; white-space:pre-wrap; margin: 6px 0 0 0; }

    /* ---------- 탭 헤더 ---------- */
    div[data-baseweb="tab-list"]{ justify-content:center !important; gap:12px !important; width:100% !important; }
    button[role="tab"]{
        min-width: 220px; border-radius: 999px !important;
        border: 1px solid var(--line) !important; background:#FFF6EE !important;
        color: var(--ink) !important; font-weight:700 !important;
    }
    button[aria-selected="true"][role="tab"]{
        background: var(--accent) !important; color:#fff !important;
        border-color: var(--accent) !important;
        box-shadow: 0 2px 6px rgba(207,161,141,.35);
    }

    /* ---------- 캐러셀/갤러리 ---------- */
    .photo-frame{
        background:#fff; border: 6px solid #F3E2D8; box-shadow: 0 8px 18px rgba(79,56,50,0.12);
        border-radius:16px; padding:10px; margin-bottom:12px;
    }
    .photo-frame .thumb{
        width:70%; height:auto; object-fit:contain;
        display:block; border-radius:10px; margin:0 auto;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------- 상단 고정 브랜드 바 --------------------
st.markdown("""
<div class="topbar-fixed">
  <div class="brand">🐾&nbsp; Pet Memorilization &nbsp;🐾</div>
</div>
""", unsafe_allow_html=True)

# -------------------- 본문 시작 --------------------
st.markdown('<div class="main-block">', unsafe_allow_html=True)

# -------------------- 공용 경로/유틸 --------------------
UPLOAD_FOLDER = "uploaded_images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

BASE_IMG_URL = "https://github.com/hyeongyunkim/teamproject/raw/main/petfuneral.png"
INFO_PATH = "memorial_info.json"

def list_uploaded_images():
    return sorted([
        f for f in os.listdir(UPLOAD_FOLDER)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ])

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

# -------------------- 부고 기본/로드 --------------------
default_name = "초코"
default_birth = datetime(2015, 3, 15).date()
default_pass  = datetime(2024, 8, 10).date()

if os.path.exists(INFO_PATH):
    try:
        with open(INFO_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            default_name = data.get("name", default_name)
            if data.get("birth"): default_birth = datetime.strptime(data["birth"], "%Y-%m-%d").date()
            if data.get("pass"):  default_pass  = datetime.strptime(data["pass"],  "%Y-%m-%d").date()
    except Exception:
        pass

# -------------------- 히어로 영역 (좌: 소개 / 우: 이미지+부고입력) --------------------
try:
    with open("guestbook.txt", "r", encoding="utf-8") as f:
        guest_lines = [ln for ln in f.readlines() if ln.strip()]
except FileNotFoundError:
    guest_lines = []
photo_count = len(list_uploaded_images())
message_count = len(guest_lines)

st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
st.markdown('<div class="hero">', unsafe_allow_html=True)
left, right = st.columns([1.6, 0.9])

with left:
    st.markdown(
        f"""
        <div class="hero-logo">🐾 Pet Memorialization 🐾</div>
        <div class="tagline">소중한 반려동물을 추모하는 공간</div>
        <div class="badges">
            <span class="badge"><span class="dot"></span> 사진 {photo_count}장</span>
            <span class="badge"><span class="dot"></span> 방명록 {message_count}개</span>
        </div>
        """, unsafe_allow_html=True
    )

with right:
    # 둥근 이미지
    st.markdown(f"<div class='kv'><img src='{BASE_IMG_URL}' alt='memorial'></div>", unsafe_allow_html=True)
    # 우측 상단 부고 입력칸
    st.markdown("**📜 부고 정보 입력**")
    pet_name = st.text_input("반려동물 이름", value=default_name, key="pet_name_input_topright")
    birth_date = st.date_input("태어난 날", value=default_birth, format="YYYY-MM-DD", key="birth_date_input_topright")
    pass_date = st.date_input("무지개다리 건넌 날", value=default_pass, format="YYYY-MM-DD", key="pass_date_input_topright")
    if st.button("부고 정보 저장", key="save_obituary_topright"):
        try:
            with open(INFO_PATH, "w", encoding="utf-8") as f:
                json.dump({
                    "name": (pet_name or "").strip() or default_name,
                    "birth": birth_date.isoformat(),
                    "pass":  pass_date.isoformat()
                }, f, ensure_ascii=False, indent=2)
            st.success("부고 정보를 저장했어요.")
            st.rerun()
        except Exception as e:
            st.error(f"저장 중 오류가 발생했어요: {e}")

st.markdown('</div>', unsafe_allow_html=True)  # .hero
st.markdown('</div>', unsafe_allow_html=True)  # .page-wrap
st.markdown('<div class="nav-divider"></div>', unsafe_allow_html=True)

# -------------------- 탭 --------------------
tab1, tab2, tab3 = st.tabs(["📜 부고장/방명록/추모관", "📺 장례식 스트리밍", "💐 기부/꽃바구니"])

# ==================== ① 부고장/방명록/추모관 ====================
with tab1:
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>In Loving Memory</h2>", unsafe_allow_html=True)

    # --- 대표 이미지 캐러셀 (업로드한 사진만) ---
    img_list = [os.path.join(UPLOAD_FOLDER, f) for f in list_uploaded_images()]
    n = len(img_list)
    if "carousel_idx" not in st.session_state:
        st.session_state.carousel_idx = 0

    if n == 0:
        st.info("현재 업로드된 대표 사진이 없습니다. '온라인 추모관'에서 사진을 업로드해 주세요.")
    else:
        st.session_state.carousel_idx %= n
        prev, mid, nextb = st.columns([1,6,1])
        with prev:
            if st.button("◀", key="carousel_prev"):
                st.session_state.carousel_idx = (st.session_state.carousel_idx - 1) % n
        with mid:
            current = img_list[st.session_state.carousel_idx]
            data_uri = img_file_to_data_uri(current)
            st.markdown(
                f"""
                <div class="photo-frame" style="max-width:720px;margin:0 auto 10px;">
                    <img class="thumb" src="{data_uri}" alt="memorial hero">
                </div>
                """, unsafe_allow_html=True
            )
            st.markdown(
                f"<p style='text-align:center; color:#6C5149;'><b>{st.session_state.carousel_idx + 1} / {n}</b></p>",
                unsafe_allow_html=True
            )
        with nextb:
            if st.button("▶", key="carousel_next"):
                st.session_state.carousel_idx = (st.session_state.carousel_idx + 1) % n

    # --- 부고장 표시 (우측 상단 입력값 사용) ---
    st.subheader("📜 부고장")
    safe_name = html.escape((pet_name or "").strip() or default_name)
    st.markdown(
        f"""
        <div style="text-align:center; background-color:#FAE8D9; padding:15px;
                    border-radius:15px; margin:10px;">
        사랑하는 <b>{safe_name}</b> 이(가) 무지개다리를 건넜습니다.<br>
        함께한 시간들을 기억하며 따뜻한 마음으로 추모해주세요.
        <br><br>
        🐾 <b>태어난 날:</b> {birth_date.isoformat()} <br>
        🌈 <b>무지개다리 건넌 날:</b> {pass_date.isoformat()}
        </div>
        """, unsafe_allow_html=True
    )

    # --- 방명록 작성 ---
    st.subheader("✍️ 방명록")
    name = st.text_input("이름")
    message = st.text_area("메시지")
    if st.button("추모 메시지 남기기"):
        if name and message:
            with open("guestbook.txt", "a", encoding="utf-8") as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|{name}|{message}\n")
            st.success("메시지가 등록되었습니다.")
            st.rerun()
        else:
            st.warning("이름과 메시지를 입력해주세요.")

    # --- 방명록 모음 (삭제 기능 포함) ---
    st.subheader("📖 추모 메시지 모음")
    try:
        with open("guestbook.txt", "r", encoding="utf-8") as f:
            lines = [ln for ln in f.readlines() if ln.strip()]
    except FileNotFoundError:
        lines = []

    if not lines:
        st.info("아직 등록된 메시지가 없습니다.")
    else:
        for idx, line in enumerate(reversed(lines)):
            try:
                time_str, user, msg = line.strip().split("|", 2)
            except ValueError:
                continue

            col_msg, col_btn = st.columns([6,1])
            with col_msg:
                st.markdown(
                    f"""
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
                    """, unsafe_allow_html=True
                )
            with col_btn:
                if st.button("삭제", key=f"delete_msg_{idx}"):
                    real_idx = len(lines) - 1 - idx
                    del lines[real_idx]
                    with open("guestbook.txt", "w", encoding="utf-8") as f:
                        f.writelines(lines)
                    st.rerun()

    # --- 온라인 추모관 (사진 업로드/삭제) ---
    st.subheader("🖼️ 온라인 추모관")
    with st.form("gallery_upload", clear_on_submit=True):
        uploaded_files = st.file_uploader("사진 업로드", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
        submit = st.form_submit_button("업로드")

    if submit and uploaded_files:
        saved, dup = 0, 0
        for uploaded_file in uploaded_files:
            data = uploaded_file.getvalue()
            digest = file_sha256(data)[:16]
            # 중복 방지: 동일 파일 해시가 이미 존재하면 스킵
            if any(f.startswith(digest + "_") for f in os.listdir(UPLOAD_FOLDER)):
                dup += 1
                continue
            safe_name_file = "".join(c for c in uploaded_file.name if c not in "\\/:*?\"<>|")
            filename = f"{digest}_{safe_name_file}"
            with open(os.path.join(UPLOAD_FOLDER, filename), "wb") as f:
                f.write(data)
            saved += 1
        if saved: st.success(f"{saved}장 업로드 완료!")
        if dup: st.info(f"중복으로 제외된 사진: {dup}장")
        st.rerun()

    image_files = list_uploaded_images()
    if image_files:
        cols = st.columns(3)
        for idx, img_file in enumerate(image_files):
            img_path = os.path.join(UPLOAD_FOLDER, img_file)
            with cols[idx % 3]:
                data_uri = img_file_to_data_uri(img_path)
                st.markdown(
                    f"""
                    <div class="photo-frame">
                        <img class="thumb" src="{data_uri}" alt="memorial photo">
                    </div>
                    """, unsafe_allow_html=True
                )
                if st.button("삭제", key=f"delete_img_{idx}"):
                    os.remove(img_path)
                    st.rerun()
    else:
        st.info("아직 업로드된 사진이 없습니다.")

    st.markdown('</div>', unsafe_allow_html=True)

# ==================== ② 장례식 스트리밍 ====================
with tab2:
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
    st.header("📺 장례식 실시간 스트리밍")
    video_url = st.text_input("YouTube 영상 URL 입력", "https://www.youtube.com/embed/dQw4w9WgXcQ")
    st.markdown(
        f"<div style='text-align:center;'><iframe width='560' height='315' src='{video_url}' frameborder='0' allowfullscreen></iframe></div>",
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== ③ 기부/꽃바구니 ====================
with tab3:
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
    st.header("💐 조문객 기부 / 꽃바구니 주문")
    st.markdown("- 💳 기부: 카카오페이 / 토스 / 계좌이체 가능\n- 🌹 꽃바구니 주문: 온라인 꽃집 링크 연결")
    link = st.text_input("꽃바구니 주문 링크", "https://www.naver.com")
    st.markdown(
        f"<div style='text-align:center;'><a href='{link}' target='_blank' "
        f"style='font-size:18px; color:#CFA18D; font-weight:bold;'>👉 꽃바구니 주문하러 가기</a></div>",
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------- 본문 종료 --------------------
st.markdown('</div>', unsafe_allow_html=True)
