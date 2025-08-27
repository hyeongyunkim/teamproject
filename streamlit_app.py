import streamlit as st
import os
import uuid
import hashlib
import shutil
from datetime import datetime
import html  # 메시지 안전 표시용 (특수문자 이스케이프)
from PIL import Image
from io import BytesIO

# -------------------- 페이지 기본 설정 --------------------
st.set_page_config(page_title="반려견 추모관", page_icon="🐾", layout="wide")

# -------------------- 색감/스타일 --------------------
st.markdown("""
    <style>
    body { background-color: #FDF6EC; color: #4B3832; }
    h1, h2, h3 { color: #4B3832 !important; }
    .stButton>button {
        background-color: #CFA18D; color: white; border-radius: 10px;
        padding: 6px 15px; border: none; font-size: 14px; transition: all .15s ease;
    }
    .stButton>button:hover { background-color: #D9A7A0; color: #fff; }
    .stTextInput>div>div>input, .stTextArea textarea {
        background-color: #fff; border: 1px solid #CFA18D; border-radius: 10px;
    }
    .topbar {
        background-color:#FAE8D9; padding:12px 18px; border-radius:0 0 14px 14px;
        border-bottom: 1px solid #EED7CA;
    }
    .nav-divider { height:8px; }

    /* ---------- 방명록 카드 스타일 ---------- */
    .guest-card {
        background: linear-gradient(180deg, #FFF8F1 0%, #FFFFFF 100%);
        border: 1px solid #EED7CA;
        border-left: 6px solid #CFA18D;
        border-radius: 14px;
        padding: 14px 16px;
        margin: 10px 0 16px 0;
        box-shadow: 0 4px 10px rgba(79, 56, 50, 0.08);
    }
    .guest-card-header { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
    .guest-avatar {
        width: 34px; height: 34px; min-width:34px; border-radius: 50%;
        background: #F0D9CF; color:#4B3832; display:flex; align-items:center; justify-content:center; font-weight: 700;
    }
    .guest-name-time { display:flex; flex-direction:column; line-height:1.2; }
    .guest-name { font-weight:700; }
    .guest-time { font-size:12px; color:#8B6F66; }
    .guest-msg { font-size:16px; color:#4B3832; white-space:pre-wrap; margin: 6px 0 0 0; }

    /* ---------- 탭 헤더 균등 정렬 ---------- */
    div[data-baseweb="tab-list"] {
        justify-content: space-between !important;
        gap: 12px !important;
        width: 100% !important;
    }
    button[role="tab"] {
        flex: 1 1 0 !important;
        text-align: center !important;
        border-radius: 999px !important;
        border: 1px solid #EED7CA !important;
        background: #FFF6EE !important;
        color: #4B3832 !important;
        font-weight: 600 !important;
    }
    button[aria-selected="true"][role="tab"] {
        background: #CFA18D !important;
        color: #fff !important;
        border-color: #CFA18D !important;
        box-shadow: 0 2px 6px rgba(207,161,141,.35);
    }

    /* --- 부고장 위 대표 이미지 가운데 정렬 --- */
    .centered-img { display:flex; justify-content:center; }

    /* --- 온라인 추모관 액자 스타일 --- */
    .photo-frame {
        background:#fff;
        border: 6px solid #F3E2D8;
        box-shadow: 0 8px 18px rgba(79,56,50,0.12);
        border-radius: 16px;
        padding: 10px;
        margin-bottom: 16px;
    }
    .photo-frame img {
        width: 100%;
        height: auto;
        display:block;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------- 상단바 --------------------
with st.container():
    st.markdown('<div class="topbar"></div>', unsafe_allow_html=True)
    left, right = st.columns([1.8, 6.2], gap="large")
    with left:
        st.markdown("### 🐾 Pet Memorialization")
        st.markdown(
            "<p style='font-size:18px; font-weight:500; color:#5A3E36;'>소중한 반려견을 추모하는 공간</p>",
            unsafe_allow_html=True
        )
    with right:
        st.write("")

st.markdown('<div class="nav-divider"></div>', unsafe_allow_html=True)

# -------------------- 공용 경로/유틸 --------------------
UPLOAD_FOLDER = "uploaded_images"
THUMB_DIR = "uploaded_images_thumbs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(THUMB_DIR, exist_ok=True)

MAX_SIDE = 2560  # 업로드 이미지 최대 변 길이
THUMB_SIZE = (600, 600)  # 썸네일 크기 (가로/세로 최대)

def build_image_list():
    """대표 이미지 + 업로드 이미지 목록 (대표 이미지는 URL)"""
    base_img = "https://github.com/hyeongyunkim/teamproject/raw/main/petfuneral.png"
    uploaded = [
        os.path.join(UPLOAD_FOLDER, f)
        for f in os.listdir(UPLOAD_FOLDER)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ]
    return [base_img] + sorted(uploaded)

def initials_from_name(name: str) -> str:
    name = name.strip()
    if not name:
        return "🕊️"
    return name[0].upper()

def file_sha256(byte_data: bytes) -> str:
    return hashlib.sha256(byte_data).hexdigest()

@st.cache_data(show_spinner=False)
def get_thumbnail(src_path: str, size=THUMB_SIZE) -> str:
    """원본 이미지로부터 썸네일 파일을 생성/재사용하고 경로 반환"""
    base = os.path.basename(src_path)
    dst_path = os.path.join(THUMB_DIR, base + ".jpg")
    if not os.path.exists(dst_path):
        try:
            with Image.open(src_path) as im:
                im.thumbnail(size)
                im.convert("RGB").save(dst_path, format="JPEG", quality=85, optimize=True)
        except Exception:
            # 썸네일 실패 시 원본을 그대로 쓰도록 원본 경로 반환
            return src_path
    return dst_path

# ====== 갤러리 초기화(사진만) ======
def reset_gallery():
    """업로드된 모든 사진/썸네일 삭제하고 초기화"""
    if os.path.exists(UPLOAD_FOLDER):
        shutil.rmtree(UPLOAD_FOLDER)
    if os.path.exists(THUMB_DIR):
        shutil.rmtree(THUMB_DIR)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(THUMB_DIR, exist_ok=True)
    if "carousel_idx" in st.session_state:
        del st.session_state["carousel_idx"]
    st.success("✅ 사진이 모두 삭제되어 초기 상태로 돌아갔습니다.")
    st.rerun()

# -------------------- 상단 탭 --------------------
tab1, tab2, tab3 = st.tabs(["📜 부고장/방명록/추모관", "📺 장례식 스트리밍", "💐 기부/꽃바구니"])

# ==================== ① 부고장/방명록/추모관 ====================
with tab1:
    st.markdown("<h2 style='text-align:center;'>In Loving Memory</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>소중한 반려견을 추모할 수 있는 공간입니다</p>", unsafe_allow_html=True)

    # --- 대표 이미지 캐러셀 ---
    img_list = build_image_list()
    n = len(img_list)
    if "carousel_idx" not in st.session_state:
        st.session_state.carousel_idx = 0
    st.session_state.carousel_idx %= max(n, 1)

    nav_prev, img_col, nav_next = st.columns([1,6,1])
    with nav_prev:
        if st.button("◀", key="carousel_prev"):
            st.session_state.carousel_idx = (st.session_state.carousel_idx - 1) % n
    with img_col:
        st.markdown("<div class='centered-img'>", unsafe_allow_html=True)
        # 대표 이미지는 URL, 업로드 이미지는 로컬 경로
        current_img = img_list[st.session_state.carousel_idx]
        st.image(current_img, width=500)
        st.markdown("</div>", unsafe_allow_html=True)
    with nav_next:
        if st.button("▶", key="carousel_next"):
            st.session_state.carousel_idx = (st.session_state.carousel_idx + 1) % n

    # --- 부고장 ---
    st.subheader("📜 부고장")
    pet_name = "초코"
    birth_date = "2015-03-15"
    death_date = "2024-08-10"
    st.markdown(
        f"""
        <div style="text-align:center; background-color:#FAE8D9; padding:15px; border-radius:15px; margin:10px;">
        사랑하는 반려견 <b>{pet_name}</b> 이(가) 무지개다리를 건넜습니다.<br>
        함께한 시간들을 기억하며 따뜻한 마음으로 추모해주세요.
        <br><br>
        🐾 <b>태어난 날:</b> {birth_date} <br>
        🌈 <b>무지개다리 건넌 날:</b> {death_date}
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

    # --- 방명록 목록(카드) + 삭제 ---
    st.subheader("📖 추모 메시지 모음")
    try:
        with open("guestbook.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []

    # OOM 방지: 너무 많으면 최근 100개만
    MAX_MSG = 100
    if len(lines) > MAX_MSG:
        lines = lines[-MAX_MSG:]

    if not lines:
        st.info("아직 등록된 메시지가 없습니다.")
    else:
        for idx, line in enumerate(reversed(lines)):  # 최신이 위로
            try:
                time_str, user, msg = line.strip().split("|", 2)
            except ValueError:
                continue

            user_safe = html.escape(user)
            time_safe = html.escape(time_str)
            msg_safe = html.escape(msg)

            c1, c2 = st.columns([12, 1])
            with c1:
                st.markdown(
                    f"""
                    <div class="guest-card">
                        <div class="guest-card-header">
                            <div class="guest-avatar">{html.escape(initials_from_name(user))}</div>
                            <div class="guest-name-time">
                                <span class="guest-name">🕊️ {user_safe}</span>
                                <span class="guest-time">{time_safe}</span>
                            </div>
                        </div>
                        <div class="guest-msg">{msg_safe}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with c2:
                if st.button("❌", key=f"delete_msg_{idx}"):
                    lines.pop(len(lines) - 1 - idx)  # 역순 보정
                    with open("guestbook.txt", "w", encoding="utf-8") as f:
                        f.writelines(lines)
                    st.rerun()

    # --- 온라인 추모관 (초기화/업로드/목록) ---
    st.subheader("🖼️ 온라인 추모관")

    # 사진 전체 삭제 초기화 (방명록은 유지)
    with st.expander("🧹 온라인 추모관 초기화", expanded=False):
        st.warning("⚠️ 업로드된 모든 사진이 삭제됩니다. 되돌릴 수 없습니다.")
        agree = st.checkbox("사진 전체 삭제에 동의합니다.")
        if st.button("사진 전체 삭제"):
            if agree:
                reset_gallery()
            else:
                st.error("삭제에 동의해 주세요.")

    # 업로드(중복 방지 + 대형 리사이즈)
    with st.form("gallery_upload", clear_on_submit=True):
        uploaded_file = st.file_uploader("사진 업로드", type=["png", "jpg", "jpeg"])
        submit = st.form_submit_button("업로드")

    if submit and uploaded_file is not None:
        data = uploaded_file.getvalue()
        digest = file_sha256(data)[:16]
        # 중복 방지: 동일 해시 파일 존재 여부
        existing = [f for f in os.listdir(UPLOAD_FOLDER) if f.startswith(digest + "_")]
        if existing:
            st.info("이미 같은 사진이 업로드되어 있어요. (중복 업로드 방지)")
        else:
            safe_name = "".join(c for c in uploaded_file.name if c not in "\\/:*?\"<>|")
            filename = f"{digest}_{safe_name}"
            save_path = os.path.join(UPLOAD_FOLDER, filename)

            # 큰 이미지는 저장 전에 리사이즈 (메모리/저장 공간 절약)
            try:
                with Image.open(BytesIO(data)) as im:
                    im.thumbnail((MAX_SIDE, MAX_SIDE))
                    im.convert("RGB").save(save_path, format="JPEG", quality=88, optimize=True)
            except Exception:
                # 이미지 파싱 실패 시 원본을 그냥 저장
                with open(save_path, "wb") as f:
                    f.write(data)

            # 썸네일 미리 생성 (첫 화면 렌더링 속도 향상)
            _ = get_thumbnail(save_path)

            st.success(f"{uploaded_file.name} 업로드 완료!")
        st.rerun()

    # ===== 갤러리 목록 (썸네일 + 페이지네이션) =====
    image_files = sorted([
        f for f in os.listdir(UPLOAD_FOLDER)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ])

    if image_files:
        # 페이지네이션
        page_size = 9
        total = len(image_files)
        max_page = max(1, (total - 1) // page_size + 1)
        page = st.number_input("페이지", min_value=1, max_value=max_page, value=1)
        start, end = (page - 1) * page_size, min(page * page_size, total)

        cols = st.columns(3)
        for i, img_file in enumerate(image_files[start:end], start=start):
            img_path = os.path.join(UPLOAD_FOLDER, img_file)
            thumb_path = get_thumbnail(img_path)

            with cols[(i - start) % 3]:
                st.markdown("<div class='photo-frame'>", unsafe_allow_html=True)
                st.image(thumb_path, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

                c1, c2 = st.columns([1, 1])
                with c1:
                    if st.button("🔍 보기", key=f"zoom_{i}"):
                        with st.modal("사진 보기"):
                            st.image(img_path, use_container_width=True)
                with c2:
                    if st.button("삭제", key=f"delete_img_{i}"):
                        # 원본 삭제
                        try:
                            os.remove(img_path)
                        except FileNotFoundError:
                            pass
                        # 썸네일 삭제
                        try:
                            os.remove(os.path.join(THUMB_DIR, img_file + ".jpg"))
                        except FileNotFoundError:
                            pass
                        st.rerun()
    else:
        st.info("아직 업로드된 사진이 없습니다.")

# ==================== ② 장례식 실시간 스트리밍 ====================
with tab2:
    st.header("📺 장례식 실시간 스트리밍")
    st.markdown("아래에 YouTube 임베드 링크를 입력하세요 (예: https://www.youtube.com/embed/영상ID)")
    video_url = st.text_input("YouTube 영상 URL 입력", "https://www.youtube.com/embed/dQw4w9WgXcQ")
    st.markdown(
        f"<div style='text-align:center;'><iframe width='560' height='315' src='{video_url}' frameborder='0' allowfullscreen></iframe></div>",
        unsafe_allow_html=True
    )

# ==================== ③ 기부 / 꽃바구니 주문 ====================
with tab3:
    st.header("💐 조문객 기부 / 꽃바구니 주문")
    st.markdown("- 💳 기부: 카카오페이 / 토스 / 계좌이체 연동 가능\n- 🌹 꽃바구니 주문: 온라인 꽃집 링크 연결 가능")
    link = st.text_input("꽃바구니 주문 링크", "https://www.naver.com")
    st.markdown(
        f"<div style='text-align:center;'><a href='{link}' target='_blank' "
        f"style='font-size:18px; color:#CFA18D; font-weight:bold;'>👉 꽃바구니 주문하러 가기</a></div>",
        unsafe_allow_html=True
    )
