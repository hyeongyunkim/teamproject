import streamlit as st
import os
import hashlib
import base64
import mimetypes
from datetime import datetime
import html  # 메시지 안전 표시용 (특수문자 이스케이프)

# -------------------- 페이지 기본 설정 --------------------
st.set_page_config(page_title="Forever Pet - 반려견 추모관", page_icon="🐾", layout="wide")

# -------------------- 색감/스타일 --------------------
st.markdown("""
    <style>
    :root{
        --bg:#FDF6EC; --ink:#4B3832; --accent:#CFA18D; --accent-2:#FAE8D9; --line:#EED7CA;
        --shadow:0 10px 24px rgba(79,56,50,0.12); --muted:#6C5149;
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
        font-size: 22px; font-weight: 800; color: #4B3832; letter-spacing: -0.2px;
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
    .stTextInput>div>div>input, .stTextArea textarea{
        background:#fff; border:1px solid var(--line); border-radius:12px;
    }

    .page-wrap{ max-width:1180px; margin:0 auto; }
    .section { margin: 28px 0; }

    /* ---------- 히어로 영역 ---------- */
    .hero{
        position:relative;
        background: radial-gradient(1200px 600px at 10% -20%, #FFEDE2 0%, rgba(255, 237, 226, 0) 60%),
                    linear-gradient(180deg, #FFF7F2 0%, #FFEFE6 100%);
        border:1px solid var(--line); border-radius:24px; box-shadow: var(--shadow);
        padding:28px 32px; overflow:hidden;
    }
    .hero:before{
        content:""; position:absolute; inset:-20px;
        background-image: radial-gradient(1px 1px at 20% 30%, rgba(207,161,141,.28) 0, transparent 60%),
                          radial-gradient(1px 1px at 60% 70%, rgba(207,161,141,.22) 0, transparent 60%),
                          radial-gradient(1px 1px at 80% 20%, rgba(207,161,141,.18) 0, transparent 60%);
        opacity:.6; pointer-events:none;
    }
    .hero-grid{ display:grid; grid-template-columns: 1.6fr .9fr; gap:28px; align-items:center; }
    .tagline{ font-size:18px; color:var(--muted); margin-bottom:14px; }
    .badges{ display:flex; gap:10px; flex-wrap:wrap; }
    .badge{
        display:inline-flex; align-items:center; gap:8px; padding:6px 10px; border-radius:999px;
        font-weight:700; font-size:13px; background:#fff; border:1px solid var(--line);
        box-shadow:0 2px 8px rgba(79,56,50,.05); color:#5A3E36;
    }
    .badge .dot{ width:8px; height:8px; border-radius:50%; background:var(--accent);
        box-shadow:0 0 0 3px rgba(207,161,141,.18) inset; }
    .hero-visual{ display:flex; align-items:center; justify-content:center; }
    .kv{ width:180px; height:180px; border-radius:50%; background:#fff; border:6px solid #F3E2D8;
        box-shadow: var(--shadow); overflow:hidden; }
    .kv img{ width:100%; height:100%; object-fit:cover; display:block; }

    /* ---------- 서비스 핵심 카드 ---------- */
    .features{ display:grid; grid-template-columns:repeat(4,1fr); gap:14px; }
    .feature-card{
        background:#fff; border:1px solid var(--line); border-radius:16px; padding:16px;
        box-shadow:0 4px 14px rgba(79,56,50,.06); text-align:center;
    }
    .feature-ico{ font-size:26px; }
    .feature-title{ font-weight:800; margin-top:6px; }
    .feature-desc{ color:var(--muted); font-size:14px; margin-top:4px; line-height:1.4; }

    /* ---------- 절차 타임라인 ---------- */
    .timeline{ display:grid; grid-template-columns:repeat(6,1fr); gap:10px; }
    .step{
        background:#fff; border:1px dashed var(--line); border-radius:14px; padding:12px; text-align:center;
    }
    .step .n{ font-weight:800; color:var(--accent); }
    .step .t{ font-weight:700; margin-top:4px; }
    .step .d{ color:var(--muted); font-size:13px; margin-top:4px; }

    /* ---------- 요금 카드 ---------- */
    .plans{ display:grid; grid-template-columns:repeat(3,1fr); gap:14px; }
    .plan{
        background:#fff; border:1px solid var(--line); border-radius:18px; padding:18px;
        box-shadow:0 6px 16px rgba(79,56,50,.08);
    }
    .plan.pop{ border:2px solid var(--accent); box-shadow:0 8px 20px rgba(207,161,141,.18); }
    .plan h4{ margin:0; }
    .price{ font-size:22px; font-weight:900; margin:8px 0; }
    .ul{ margin:8px 0 12px 16px; color:var(--muted); }
    .ul li{ margin:4px 0; }

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

    /* ---------- 탭 헤더 ---------- */
    div[data-baseweb="tab-list"]{ justify-content:center !important; gap:12px !important; width:100% !important; }
    button[role="tab"]{
        min-width: 220px; text-align:center !important; border-radius: 999px !important;
        border: 1px solid var(--line) !important; background:#FFF6EE !important;
        color: var(--ink) !important; font-weight:700 !important;
    }
    button[aria-selected="true"][role="tab"]{
        background: var(--accent) !important; color:#fff !important; border-color: var(--accent) !important;
        box-shadow: 0 2px 6px rgba(207,161,141,.35);
    }

    /* ---------- 갤러리(액자+정사각썸네일) ---------- */
    .photo-frame{ background:#fff; border: 6px solid #F3E2D8; box-shadow: 0 8px 18px rgba(79,56,50,0.12);
        border-radius:16px; padding:10px; margin-bottom:12px; }
    .photo-frame .thumb{ width:85%; aspect-ratio:1/1; object-fit:cover; display:block; border-radius:10px; margin:0 auto; }

    /* ---------- 우하단 플로팅 상담 버튼 ---------- */
    .fab-wrap{
        position: fixed; right: 18px; bottom: 18px; display:flex; flex-direction:column; gap:10px; z-index:9999;
    }
    .fab{
        background:var(--accent); color:#fff; border-radius:999px; padding:10px 14px;
        box-shadow:0 6px 16px rgba(207,161,141,.35); border:1px solid #b88370; text-decoration:none;
        font-weight:800;
    }
    .fab:hover{ filter:brightness(1.05); }
    .fab.secondary{ background:#fff; color:#4B3832; border-color:var(--line); }
    </style>
""", unsafe_allow_html=True)

# -------------------- 상단 고정 브랜드 바 --------------------
st.markdown("""
<div class="topbar-fixed">
  <div class="brand"><span class="logo">🐾</span> Forever Pet</div>
</div>
""", unsafe_allow_html=True)

# 본문 시작(상단 고정바와 겹치지 않도록 오프셋)
st.markdown('<div class="main-block">', unsafe_allow_html=True)

# -------------------- 공용 경로/유틸 --------------------
UPLOAD_FOLDER = "uploaded_images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
BASE_IMG_URL = "https://github.com/hyeongyunkim/teamproject/raw/main/petfuneral.png"

def list_uploaded_images():
    return sorted([f for f in os.listdir(UPLOAD_FOLDER) if f.lower().endswith((".png",".jpg",".jpeg"))])

def build_image_list():
    uploaded = [os.path.join(UPLOAD_FOLDER, f) for f in list_uploaded_images()]
    return [BASE_IMG_URL] + uploaded

def initials_from_name(name: str) -> str:
    name = name.strip()
    return "🕊️" if not name else name[0].upper()

def file_sha256(byte_data: bytes) -> str:
    return hashlib.sha256(byte_data).hexdigest()

def img_file_to_data_uri(path: str) -> str:
    mime, _ = mimetypes.guess_type(path)
    if mime is None: mime = "image/jpeg"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}"

# -------------------- 상단 히어로 --------------------
try:
    with open("guestbook.txt","r",encoding="utf-8") as f:
        guest_lines = [ln for ln in f.readlines() if ln.strip()]
except FileNotFoundError:
    guest_lines = []
photo_count = len(list_uploaded_images())
message_count = len(guest_lines)

st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
st.markdown(
    f"""
    <div class="hero">
      <div class="hero-grid">
        <div>
          <div class="tagline">소중한 반려견을 추모하는 공간</div>
          <div class="badges">
            <span class="badge"><span class="dot"></span> 사진 {photo_count}장</span>
            <span class="badge"><span class="dot"></span> 방명록 {message_count}개</span>
            <span class="badge"><span class="dot"></span> 24시간 상담</span>
          </div>
        </div>
        <div class="hero-visual">
          <div class="kv">
            <img src="{BASE_IMG_URL}" alt="memorial">
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True
)

# --- 서비스 핵심 카드 (4개) ---
st.markdown('<div class="section page-wrap">', unsafe_allow_html=True)
st.markdown("""
<div class="features">
  <div class="feature-card">
    <div class="feature-ico">📞</div>
    <div class="feature-title">24시간 전문 상담</div>
    <div class="feature-desc">언제든 연락 주세요. 따뜻하게 안내해 드립니다.</div>
  </div>
  <div class="feature-card">
    <div class="feature-ico">📺</div>
    <div class="feature-title">실시간 스트리밍</div>
    <div class="feature-desc">멀리 있는 가족/지인도 참여할 수 있도록.</div>
  </div>
  <div class="feature-card">
    <div class="feature-ico">🌐</div>
    <div class="feature-title">원격 조문</div>
    <div class="feature-desc">방명록/헌화 메시지로 함께 추모합니다.</div>
  </div>
  <div class="feature-card">
    <div class="feature-ico">💐</div>
    <div class="feature-title">기부/추모꽃 연동</div>
    <div class="feature-desc">의미 있는 마음을 전달할 수 있게.</div>
  </div>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 절차 타임라인 ---
st.markdown('<div class="section page-wrap">', unsafe_allow_html=True)
st.markdown("""
### 장례 절차 안내
<div class="timeline">
  <div class="step"><div class="n">1</div><div class="t">상담</div><div class="d">24시간 전화/문의</div></div>
  <div class="step"><div class="n">2</div><div class="t">접수</div><div class="d">기본 안내/일정 확정</div></div>
  <div class="step"><div class="n">3</div><div class="t">안치</div><div class="d">고요한 공간에 모심</div></div>
  <div class="step"><div class="n">4</div><div class="t">추모식</div><div class="d">헌화/추모영상</div></div>
  <div class="step"><div class="n">5</div><div class="t">화장</div><div class="d">엄숙히 진행</div></div>
  <div class="step"><div class="n">6</div><div class="t">수습</div><div class="d">유골함/위패 안내</div></div>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 요금/패키지 카드 ---
st.markdown('<div class="section page-wrap">', unsafe_allow_html=True)
st.markdown("""
### 서비스 패키지
<div class="plans">
  <div class="plan">
    <h4>Basic</h4>
    <div class="price">₩180,000~</div>
    <ul class="ul">
      <li>기본 장례 절차</li>
      <li>헌화/방명록</li>
      <li>기본 유골함</li>
    </ul>
  </div>
  <div class="plan pop">
    <h4>Standard</h4>
    <div class="price">₩280,000~</div>
    <ul class="ul">
      <li>실시간 스트리밍</li>
      <li>맞춤 추모영상</li>
      <li>선택형 유골함</li>
    </ul>
  </div>
  <div class="plan">
    <h4>Premium</h4>
    <div class="price">₩390,000~</div>
    <ul class="ul">
      <li>프라이빗 추모식</li>
      <li>맞춤 추모공간 페이지</li>
      <li>추모꽃 바구니 포함</li>
    </ul>
  </div>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- FAQ (Streamlit expander 활용) ---
st.markdown('<div class="section page-wrap">', unsafe_allow_html=True)
st.markdown("### 자주 묻는 질문")
with st.expander("문의는 24시간 가능한가요?"):
    st.write("네, 언제든지 연락 주시면 빠르게 안내해 드립니다.")
with st.expander("실시간 스트리밍은 어떻게 보나요?"):
    st.write("‘장례식 스트리밍’ 탭에서 YouTube 임베드 링크를 입력해 가족/지인과 공유하실 수 있습니다.")
with st.expander("원격 조문은 어떻게 하나요?"):
    st.write("‘부고장/방명록/추모관’ 탭에서 방명록(추모 메시지)를 남기고, 기부/꽃바구니 탭에서 마음을 전하실 수 있어요.")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="nav-divider"></div>', unsafe_allow_html=True)

# -------------------- 탭: 본 기능들 --------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📜 부고장/방명록/추모관", "📺 장례식 스트리밍", "💐 기부/꽃바구니", "📞 상담/위치"
])

# ==================== ① 부고장/방명록/추모관 ====================
with tab1:
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>In Loving Memory</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#6C5149'>따뜻한 마음으로 그리움을 나눌 수 있는 공간입니다.</p>", unsafe_allow_html=True)

    # --- 대표 이미지 캐러셀 (액자 + 지표) ---
    img_list = build_image_list()
    n = len(img_list)
    total_photos = max(0, n - 1)  # 업로드 개수(대표 제외)

    if "carousel_idx" not in st.session_state:
        st.session_state.carousel_idx = 0
    if n == 0:
        img_list = [BASE_IMG_URL]; n = 1
    st.session_state.carousel_idx %= n

    prev, mid, nextb = st.columns([1,6,1])
    with prev:
        if st.button("◀", key="carousel_prev"):
            st.session_state.carousel_idx = (st.session_state.carousel_idx - 1) % n
    with mid:
        current = img_list[st.session_state.carousel_idx]
        if current.startswith("http"):
            st.markdown(
                f"""
                <div class="photo-frame" style="max-width:560px;margin:0 auto 10px;">
                    <img class="thumb" src="{current}" alt="memorial hero">
                </div>
                """, unsafe_allow_html=True
            )
        else:
            data_uri = img_file_to_data_uri(current)
            st.markdown(
                f"""
                <div class="photo-frame" style="max-width:560px;margin:0 auto 10px;">
                    <img class="thumb" src="{data_uri}" alt="memorial hero">
                </div>
                """, unsafe_allow_html=True
            )
        st.markdown(
            f"<p style='text-align:center; color:#6C5149;'><b>{st.session_state.carousel_idx + 1} / {n}</b> • 현재 업로드된 사진: <b>{total_photos}장</b></p>",
            unsafe_allow_html=True
        )
    with nextb:
        if st.button("▶", key="carousel_next"):
            st.session_state.carousel_idx = (st.session_state.carousel_idx + 1) % n

    # --- 부고장 ---
    st.subheader("📜 부고장")
    st.markdown(
        """
        <div style="text-align:center; background-color:#FAE8D9; padding:15px; border-radius:15px; margin:10px;">
        사랑하는 반려견 <b>초코</b> 이(가) 무지개다리를 건넜습니다.<br>
        함께한 시간들을 기억하며 따뜻한 마음으로 추모해주세요.
        <br><br>
        🐾 <b>태어난 날:</b> 2015-03-15 <br>
        🌈 <b>무지개다리 건넌 날:</b> 2024-08-10
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
            st.success("메시지가 등록되었습니다. 고맙습니다.")
            st.rerun()
        else:
            st.warning("이름과 메시지를 입력해주세요.")

    # --- 방명록 모음 ---
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

    # --- 온라인 추모관: 업로드/갤러리 ---
    st.subheader("🖼️ 온라인 추모관")
    with st.form("gallery_upload", clear_on_submit=True):
        uploaded_files = st.file_uploader("사진 업로드", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
        submit = st.form_submit_button("업로드")

    if submit and uploaded_files:
        saved, dup = 0, 0
        for uploaded_file in uploaded_files:
            data = uploaded_file.getvalue()
            digest = file_sha256(data)[:16]
            if any(f.startswith(digest + "_") for f in os.listdir(UPLOAD_FOLDER)):
                dup += 1; continue
            safe_name = "".join(c for c in uploaded_file.name if c not in "\\/:*?\"<>|")
            filename = f"{digest}_{safe_name}"
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
                    if os.path.exists(img_path):
                        os.remove(img_path)
                    st.rerun()
    else:
        st.info("아직 업로드된 사진이 없습니다.")
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== ② 장례식 실시간 스트리밍 ====================
with tab2:
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
    st.header("📺 장례식 실시간 스트리밍")
    st.markdown("아래에 YouTube 임베드 링크를 입력하세요 (예: https://www.youtube.com/embed/영상ID)")
    video_url = st.text_input("YouTube 영상 URL 입력", "https://www.youtube.com/embed/dQw4w9WgXcQ")
    st.markdown(
        f"<div style='text-align:center;'><iframe width='560' height='315' src='{video_url}' frameborder='0' allowfullscreen></iframe></div>",
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== ③ 기부 / 꽃바구니 주문 ====================
with tab3:
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
    st.header("💐 조문객 기부 / 꽃바구니 주문")
    st.markdown("- 💳 기부: 카카오페이 / 토스 / 계좌이체 연동 가능\n- 🌹 꽃바구니 주문: 온라인 꽃집 링크 연결 가능")
    link = st.text_input("꽃바구니 주문 링크", "https://www.naver.com")
    st.markdown(
        f"<div style='text-align:center;'><a href='{link}' target='_blank' "
        f"style='font-size:18px; color:#CFA18D; font-weight:bold;'>👉 꽃바구니 주문하러 가기</a></div>",
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== ④ 상담/위치 ====================
with tab4:
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
    st.header("📞 상담 & 위치")
    st.markdown("언제든 연락 주세요. 따뜻하게 안내해 드립니다.")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("연락처")
        st.markdown("""
        - 전화: **[010-0000-0000](tel:01000000000)**
        - 카카오톡: **[상담하기](https://pf.kakao.com/)**  
        - 이메일: **hello@foreverpet.co.kr**
        """)
        st.subheader("간단 문의")
        with st.form("contact_form", clear_on_submit=True):
            uname = st.text_input("성함")
            uphone = st.text_input("연락처")
            umsg = st.text_area("문의 내용")
            sent = st.form_submit_button("문의 보내기")
        if sent:
            with open("inquiries.txt","a",encoding="utf-8") as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|{uname}|{uphone}|{umsg}\n")
            st.success("문의가 접수되었습니다. 빠르게 연락드릴게요.")

    with c2:
        st.subheader("오시는 길")
        # Google Maps 임베드 예시(원하시는 주소로 교체)
        st.markdown("""
        <div style='border-radius:14px; overflow:hidden; box-shadow:0 6px 16px rgba(79,56,50,.12);'>
          <iframe
            src="https://maps.google.com/maps?q=Seoul&t=&z=12&ie=UTF8&iwloc=&output=embed"
            width="100%" height="320" style="border:0;" loading="lazy"></iframe>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- 우하단 플로팅 상담 버튼 ----------
st.markdown("""
<div class="fab-wrap">
  <a class="fab" href="tel:01000000000">📞 전화 상담</a>
  <a class="fab secondary" href="https://pf.kakao.com/" target="_blank">💬 카카오톡</a>
  <a class="fab secondary" href="https://maps.google.com/?q=Seoul" target="_blank">🗺️ 길찾기</a>
</div>
""", unsafe_allow_html=True)

# 본문 끝 (상단 고정바 offset 닫기)
st.markdown('</div>', unsafe_allow_html=True)
