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
        --bg:#FAF7F2; --ink:#3F3A37; --accent:#BFAAA0; --accent-2:#F1E8E2; --line:#E8DED8;
        --muted:#6C645F; --shadow:0 6px 18px rgba(63,58,55,0.08);
    }
    body { background: var(--bg); color: var(--ink); }
    h1,h2,h3 { color: var(--ink) !important; }

    /* ===== 상단 고정 브랜드 바 (차분하게) ===== */
    .topbar-fixed {
        position: fixed; top: 0; left: 0; right: 0; height: 56px;
        background: #F6F1EC; border-bottom: 1px solid var(--line);
        display: flex; align-items: center; padding: 0 20px; z-index: 1000;
    }
    .topbar-fixed .brand {
        display: flex; align-items: center; gap: 8px;
        font-size: 20px; font-weight: 800; color: #3F3A37; letter-spacing: -0.2px;
    }
    .topbar-fixed .logo { font-size: 22px; }
    .main-block { margin-top: 68px; }  /* 상단바 여백 */

    /* 공통 입력/버튼 (톤다운) */
    .stButton>button{
        background: var(--accent); color: #fff; border: none; border-radius: 10px;
        padding: 8px 14px; font-weight: 600; box-shadow: 0 2px 8px rgba(191,170,160,.25);
        transition: filter .15s ease;
    }
    .stButton>button:hover{ filter: brightness(1.04); }
    .stTextInput>div>div>input, .stTextArea textarea{
        background:#fff; border:1px solid var(--line); border-radius:10px;
    }

    .page-wrap{ max-width:1120px; margin:0 auto; }
    .section { margin: 24px 0; }

    /* ---------- 히어로 영역 (따뜻하고 절제된) ---------- */
    .hero{
        background: linear-gradient(180deg, #F9F4EF 0%, #F4EEE8 100%);
        border:1px solid var(--line); border-radius:22px; box-shadow: var(--shadow);
        padding: 24px 28px;
    }
    .hero-grid{ display:grid; grid-template-columns: 1.5fr .9fr; gap:22px; align-items:center; }
    .tagline{ font-size:17px; color:var(--muted); margin-bottom:10px; }
    .badges{ display:flex; gap:10px; flex-wrap:wrap; }
    .badge{
        display:inline-flex; align-items:center; gap:8px; padding:6px 10px; border-radius:999px;
        font-weight:700; font-size:13px; background:#fff; border:1px solid var(--line);
        color:#5C5551;
    }
    .kv{ width:160px; height:160px; border-radius:50%; overflow:hidden; margin: 0 auto;
         border:6px solid #EADFD8; box-shadow: var(--shadow); background:#fff; }
    .kv img{ width:100%; height:100%; object-fit:cover; }

    /* ---------- 우리의 약속 (3개 카드) ---------- */
    .values{ display:grid; grid-template-columns:repeat(3,1fr); gap:14px; }
    .value-card{
        background:#fff; border:1px solid var(--line); border-radius:14px; padding:16px;
        box-shadow:0 3px 12px rgba(63,58,55,.06);
    }
    .value-ico{ font-size:22px; }
    .value-title{ font-weight:800; margin-top:6px; }
    .value-desc{ color:var(--muted); font-size:14px; margin-top:6px; line-height:1.5; }

    /* ---------- 절차 안내 (간단) ---------- */
    .timeline{ display:grid; grid-template-columns:repeat(5,1fr); gap:8px; }
    .step{ background:#fff; border:1px dashed var(--line); border-radius:12px; padding:12px; text-align:center; }
    .step .t{ font-weight:700; }
    .step .d{ color:var(--muted); font-size:13px; margin-top:4px; }

    /* ---------- 방명록 카드 ---------- */
    .guest-card{
        background: linear-gradient(180deg, #FFF9F5 0%, #FFFFFF 100%);
        border: 1px solid var(--line);
        border-left: 6px solid #BFAAA0;
        border-radius: 12px; padding: 14px 16px; margin: 10px 0 14px 0;
        box-shadow: 0 3px 10px rgba(63, 58, 55, 0.06);
    }
    .guest-card-header{ display:flex; align-items:center; gap:10px; margin-bottom:8px; }
    .guest-avatar{ width:32px; height:32px; min-width:32px; border-radius:50%;
        background:#E8DAD2; color:#3F3A37; display:flex; align-items:center; justify-content:center; font-weight:700; }
    .guest-name-time{ display:flex; flex-direction:column; line-height:1.2; }
    .guest-name{ font-weight:700; }
    .guest-time{ font-size:12px; color:#8A827D; }
    .guest-msg{ font-size:15px; color:#3F3A37; white-space:pre-wrap; margin-top:4px; }

    /* ---------- 탭 헤더 (중립 톤) ---------- */
    div[data-baseweb="tab-list"]{ justify-content:center !important; gap:10px !important; width:100% !important; }
    button[role="tab"]{
        min-width: 210px; text-align:center !important; border-radius: 999px !important;
        border: 1px solid var(--line) !important; background:#F7F2EE !important;
        color: var(--ink) !important; font-weight:700 !important;
    }
    button[aria-selected="true"][role="tab"]{
        background: #BFAAA0 !important; color:#fff !important; border-color: #BFAAA0 !important;
        box-shadow: 0 2px 6px rgba(191,170,160,.28);
    }

    /* ---------- 갤러리(액자+정사각 썸네일) ---------- */
    .photo-frame{ background:#fff; border: 5px solid #EADFD8; box-shadow: 0 6px 16px rgba(63,58,55,0.10);
        border-radius:14px; padding:10px; margin-bottom:12px; }
    .photo-frame .thumb{ width:82%; aspect-ratio:1/1; object-fit:cover; display:block; border-radius:10px; margin:0 auto; }

    /* ---------- 우하단 도움 버튼 (1개만, 은은하게) ---------- */
    .help-fab{
        position: fixed; right: 18px; bottom: 18px; z-index: 9999;
        background:#3F3A37; color:#fff; border-radius:999px; padding:10px 16px;
        text-decoration:none; font-weight:700; box-shadow:0 6px 16px rgba(63,58,55,.25);
        opacity:.92;
    }
    .help-fab:hover{ opacity:1; }
    </style>
""", unsafe_allow_html=True)

# -------------------- 상단 고정 브랜드 바 --------------------
st.markdown("""
<div class="topbar-fixed">
  <div class="brand"><span class="logo">🐾</span> Forever Pet</div>
</div>
""", unsafe_allow_html=True)

# 본문 시작(상단 고정바 여백)
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
          <div class="tagline">그리움과 감사의 마음을, 조용히 기록하는 공간입니다.</div>
          <div class="badges">
            <span class="badge">사진 {photo_count}장</span>
            <span class="badge">메시지 {message_count}개</span>
            <span class="badge">개인정보 보호 우선</span>
          </div>
        </div>
        <div class="kv"><img src="{BASE_IMG_URL}" alt="memorial"></div>
      </div>
    </div>
    """, unsafe_allow_html=True
)
st.markdown('</div>', unsafe_allow_html=True)

# --- 우리의 약속 (3가지) ---
st.markdown('<div class="section page-wrap">', unsafe_allow_html=True)
st.markdown("""
<div class="values">
  <div class="value-card">
    <div class="value-ico">🤍</div>
    <div class="value-title">존엄과 배려</div>
    <div class="value-desc">작은 존재의 삶도 존중받아야 합니다. 모든 과정을 차분하게 진행합니다.</div>
  </div>
  <div class="value-card">
    <div class="value-ico">🕯️</div>
    <div class="value-title">투명한 안내</div>
    <div class="value-desc">불필요한 권유 없이, 필요한 정보만 명확하게 제공합니다.</div>
  </div>
  <div class="value-card">
    <div class="value-ico">🔒</div>
    <div class="value-title">개인정보 보호</div>
    <div class="value-desc">사진과 메시지는 요청 시 언제든 삭제할 수 있습니다.</div>
  </div>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 간단 절차 안내 ---
st.markdown('<div class="section page-wrap">', unsafe_allow_html=True)
st.markdown("""
### 절차 안내 (간단히)
<div class="timeline">
  <div class="step"><div class="t">상담</div><div class="d">필요한 만큼만 안내</div></div>
  <div class="step"><div class="t">안치</div><div class="d">차분하고 안전하게</div></div>
  <div class="step"><div class="t">추모</div><div class="d">헌화·방명록·사진</div></div>
  <div class="step"><div class="t">작별</div><div class="d">엄숙히 진행</div></div>
  <div class="step"><div class="t">기억</div><div class="d">기록과 보관</div></div>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section"></div>', unsafe_allow_html=True)

# -------------------- 탭 --------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📜 부고장/방명록/추모관", "📺 장례식 스트리밍", "🌿 마음 전하기", "📞 도움/위치"
])

# ==================== ① 부고장/방명록/추모관 ====================
with tab1:
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)

    st.markdown("<h2 style='text-align:center;'>In Loving Memory</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#6C645F'>조용한 마음으로, 함께 기억합니다.</p>", unsafe_allow_html=True)

    # --- 대표 이미지 캐러셀 ---
    img_list = build_image_list()
    n = len(img_list)
    total_photos = max(0, n - 1)
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
                <div class="photo-frame" style="max-width:520px;margin:0 auto 8px;">
                    <img class="thumb" src="{current}" alt="memorial hero">
                </div>""", unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div class="photo-frame" style="max-width:520px;margin:0 auto 8px;">
                    <img class="thumb" src="{img_file_to_data_uri(current)}" alt="memorial hero">
                </div>""", unsafe_allow_html=True
            )
        st.markdown(
            f"<p style='text-align:center; color:#6C645F;'><b>{st.session_state.carousel_idx + 1} / {n}</b> • 사진 <b>{total_photos}장</b></p>",
            unsafe_allow_html=True
        )
    with nextb:
        if st.button("▶", key="carousel_next"):
            st.session_state.carousel_idx = (st.session_state.carousel_idx + 1) % n

    # --- 부고장 ---
    st.subheader("📜 부고장")
    st.markdown(
        """
        <div style="text-align:center; background:#F1E8E2; padding:14px; border-radius:14px; margin:8px;">
        사랑하는 반려견 <b>초코</b>를 떠나보내며, 함께한 시간을 감사히 기억합니다.
        <br><br>
        🐾 <b>태어난 날:</b> 2015-03-15 &nbsp;&nbsp;|&nbsp;&nbsp; 🌈 <b>무지개다리 건넌 날:</b> 2024-08-10
        </div>
        """,
        unsafe_allow_html=True
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
                """,
                unsafe_allow_html=True
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
                st.markdown(
                    f"""
                    <div class="photo-frame">
                        <img class="thumb" src="{img_file_to_data_uri(img_path)}" alt="memorial photo">
                    </div>
                    """,
                    unsafe_allow_html=True
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
    st.caption("멀리 계신 가족·지인이 함께 마음을 모을 수 있도록 도와드립니다.")
    video_url = st.text_input("YouTube 임베드 링크 (예: https://www.youtube.com/embed/영상ID)", "https://www.youtube.com/embed/dQw4w9WgXcQ")
    st.markdown(
        f"<div style='text-align:center;'><iframe width='560' height='315' src='{video_url}' frameborder='0' allowfullscreen></iframe></div>",
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== ③ 마음 전하기 ====================
with tab3:
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
    st.header("🌿 마음 전하기")
    st.caption("작은 꽃 한 송이, 짧은 메시지, 혹은 조용한 기부로 마음을 전하실 수 있어요.")
    link = st.text_input("추모꽃/마음 전하기 링크(선택)", "https://www.naver.com")
    st.markdown(
        f"<div style='text-align:center; margin-top:6px;'><a href='{link}' target='_blank' "
        f"style='font-size:16px; color:#3F3A37; font-weight:700; text-decoration:underline;'>👉 마음 전하러 가기</a></div>",
        unsafe_allow_html=True
    )

    st.markdown("---")
    st.subheader("애도 리소스")
    st.markdown("- 반려동물과의 이별을 겪는 분들을 위한 글/상담처를 찾아보세요.")
    st.markdown("- 가까운 분들과 기억을 나누는 일도 큰 힘이 됩니다.")

    st.markdown("---")
    st.subheader("기억하기 제안")
    st.markdown("- 함께한 장소를 산책하며 사진을 조금씩 정리해보세요.")
    st.markdown("- 방명록에 짧은 편지를 남기고, 시간이 지나 다시 읽어보세요.")
    st.markdown('- 이름을 부르며 “고마웠어”라는 한마디를 기록해보세요.')

    st.markdown('</div>', unsafe_allow_html=True)

# ==================== ④ 도움/위치 ====================
with tab4:
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
    st.header("📞 도움 & 위치")
    st.caption("필요하실 때 잠시 기대어도 괜찮습니다.")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("연락")
        st.markdown("""
        - 전화: **[010-0000-0000](tel:01000000000)**
        - 이메일: **hello@foreverpet.co.kr**
        - 개인정보/삭제 요청: guestbook이나 사진의 삭제를 원하시면 언제든 알려주세요.
        """)

        st.subheader("간단 문의")
        with st.form("contact_form", clear_on_submit=True):
            uname = st.text_input("성함")
            uphone = st.text_input("연락처")
            umsg = st.text_area("문의 내용")
            sent = st.form_submit_button("보내기")
        if sent:
            with open("inquiries.txt","a",encoding="utf-8") as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|{uname}|{uphone}|{umsg}\n")
            st.success("문의가 접수되었습니다. 가능한 빠르게 답장 드리겠습니다.")

    with c2:
        st.subheader("오시는 길")
        st.markdown("""
        <div style='border-radius:12px; overflow:hidden; box-shadow:0 6px 14px rgba(63,58,55,.12);'>
          <iframe
            src="https://maps.google.com/maps?q=Seoul&t=&z=12&ie=UTF8&iwloc=&output=embed"
            width="100%" height="320" style="border:0;" loading="lazy"></iframe>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- 우하단 도움 버튼 ----------
st.markdown("""
<a class="help-fab" href="tel:01000000000" title="도움이 필요하신가요?">도움이 필요하신가요?</a>
""", unsafe_allow_html=True)

# 본문 끝
st.markdown('</div>', unsafe_allow_html=True)
