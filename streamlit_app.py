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
