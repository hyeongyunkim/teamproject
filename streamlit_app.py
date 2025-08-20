import streamlit as st
import os
from datetime import datetime
import base64

# 페이지 기본 설정
st.set_page_config(page_title="반려견 추모관", page_icon="🐾", layout="centered")

# --- 사이드바 메뉴 ---
menu = st.sidebar.selectbox(
    "메뉴 선택",
    ["부고장 + 방명록 + 추모관", "장례식 실시간 스트리밍", "기부 / 꽃바구니 주문"]
)

# --- 1페이지: 부고장 + 방명록 + 추모관 ---
if menu == "부고장 + 방명록 + 추모관":
    st.markdown("<h1 style='text-align: center;'>🐾 Pet Memorialization 🐾</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>In Loving Memory</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>소중한 반려견을 추모할 수 있는 공간입니다</p>", unsafe_allow_html=True)

    # --- 추모 이미지 (GitHub에서 불러오기) ---
    img_url = "https://github.com/hyeongyunkim/teamproject/raw/main/petfuneral.png"
    st.markdown(f"<div style='text-align: center;'><img src='{img_url}' width='300'></div>", unsafe_allow_html=True)

    # --- 부고장 ---
    st.markdown("<h2 style='text-align: center;'>📜 부고장</h2>", unsafe_allow_html=True)
    pet_name = "초코"
    birth_date = "2015-03-15"
    death_date = "2024-08-10"
    st.markdown(
        f"""
        <p style='text-align: center;'>
        사랑하는 반려견 <b>{pet_name}</b> 이(가) 무지개다리를 건넜습니다.<br>
        함께한 시간들을 기억하며 따뜻한 마음으로 추모해주세요.
        </p>
        <p style='text-align: center;'>
        🐾 <b>태어난 날:</b> {birth_date} <br>
        🌈 <b>무지개다리 건넌 날:</b> {death_date}
        </p>
        """,
        unsafe_allow_html=True
    )

   # --- 방명록 ---
    st.markdown("<h2 style='text-align: center;'>✍️ 방명록</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        name = st.text_input("이름")
        message = st.text_area("메시지")
        if st.button("추모 메시지 남기기"):
            if name and message:
                with open("guestbook.txt", "a", encoding="utf-8") as f:
                    f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|{name}|{message}\n")
                st.success("메시지가 등록되었습니다. 고맙습니다.")
            else:
                st.warning("이름과 메시지를 입력해주세요.")

    st.markdown("<h3 style='text-align: center;'>📖 추모 메시지 모음</h3>", unsafe_allow_html=True)

    try:
        with open("guestbook.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []

    if not lines:
        st.info("아직 등록된 메시지가 없습니다.")
    else:
        for idx, line in enumerate(reversed(lines)):  # 최신 메시지가 위로
            try:
                time_str, user, msg = line.strip().split("|", 2)
            except ValueError:
                continue  # 잘못된 형식은 무시

            with st.container():
                st.markdown(
                    f"""
                    <div style="
                        background-color:#f9f9f9;
                        padding:15px;
                        margin:10px 0;
                        border-radius:10px;
                        box-shadow: 2px 2px 6px rgba(0,0,0,0.1);">
                        <p style="color:#333; font-size:14px; margin:0;"><b>🕊️ {user}</b></p>
                        <p style="color:#555; font-size:16px; margin:5px 0;">{msg}</p>
                        <p style="color:gray; font-size:12px; text-align:right; margin:0;">{time_str}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                if st.button("❌ 삭제", key=f"delete_msg_{idx}"):
                    lines.pop(len(lines)-1-idx)  # 역순 때문에 인덱스 조정
                    with open("guestbook.txt", "w", encoding="utf-8") as f:
                        f.writelines(lines)
                    st.rerun()

    # --- 온라인 추모관 ---
    st.markdown("<h2>🖼️ 온라인 추모관</h2>", unsafe_allow_html=True)
    UPLOAD_FOLDER = "uploaded_images"
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    uploaded_file = st.file_uploader("사진 업로드", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        save_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"{uploaded_file.name} 업로드 완료!")

    image_files = os.listdir(UPLOAD_FOLDER)
    if image_files:
        cols_count = 3 if len(image_files) >= 3 else max(1, len(image_files))
        cols = st.columns(cols_count)
        for idx, img_file in enumerate(image_files):
            img_path = os.path.join(UPLOAD_FOLDER, img_file)
            with open(img_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
            with cols[idx % cols_count]:
                st.markdown(f'<img src="data:image/png;base64,{encoded}" width="200">', unsafe_allow_html=True)
                if st.button(f"삭제 {img_file}", key=f"delete_img_{img_file}"):
                    os.remove(img_path)
                    st.rerun()
    else:
        st.info("아직 업로드된 사진이 없습니다.")

# --- 2페이지: 장례식 실시간 스트리밍 ---
elif menu == "장례식 실시간 스트리밍":
    st.header("📺 장례식 실시간 스트리밍 (원격 조문 지원)")
    st.markdown("아래에 실시간 스트리밍 영상을 삽입할 수 있습니다 (YouTube 연동).")

    video_url = st.text_input(
        "YouTube 영상 URL 입력", 
        "https://youtu.be/0q_htb-wGTM?si=t7n2par5CUs3WFFo"
    )

    # --- 유튜브 URL 처리 ---
    if "youtube.com" in video_url or "youtu.be" in video_url:
        if "watch?v=" in video_url:
            video_id = video_url.split("watch?v=")[-1].split("&")[0]
        elif "youtu.be/" in video_url:
            video_id = video_url.split("youtu.be/")[-1].split("?")[0]
        else:
            video_id = None

        if video_id:
            embed_url = f"https://www.youtube.com/embed/{video_id}"
            st.markdown(
                f"<iframe width='560' height='315' src='{embed_url}' frameborder='0' allowfullscreen></iframe>", 
                unsafe_allow_html=True
            )
        else:
            st.error("유효한 YouTube 링크를 입력해주세요.")
    else:
        st.error("YouTube URL만 지원됩니다.")


# --- 3페이지: 기부 / 꽃바구니 주문 ---
elif menu == "기부 / 꽃바구니 주문":
    st.header("💐 조문객 기부 / 꽃바구니 주문")
    st.markdown("이 페이지에서 조문객이 온라인으로 기부하거나 꽃바구니를 주문할 수 있습니다.")
    st.markdown("- 💳 기부: 카카오페이 / 토스 / 계좌이체 연동 가능")
    st.markdown("- 🌹 꽃바구니 주문: 온라인 꽃집 링크 연결 가능")
    link = st.text_input("꽃바구니 주문 링크", "https://www.naver.com")
    st.markdown(f"[👉 꽃바구니 주문하러 가기]({link})")
