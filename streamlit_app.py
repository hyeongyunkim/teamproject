# -------------------- 플로팅 + 버튼 --------------------
if "fab_open" not in st.session_state:
    st.session_state.fab_open = False

# 버튼 토글
def toggle_fab():
    st.session_state.fab_open = not st.session_state.fab_open

# CSS로 오른쪽 하단 고정
st.markdown("""
<style>
.fab-container {
    position: fixed;
    bottom: 24px;
    right: 24px;
    z-index: 10000;
    display: flex;
    flex-direction: column;
    align-items: flex-end;
}
.fab-main {
    width: 56px; height: 56px;
    border-radius: 50%;
    background: #CFA18D; color: white;
    font-size: 28px; font-weight: bold;
    border: none; cursor: pointer;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}
.fab-menu {
    margin-bottom: 10px;
    display: flex;
    flex-direction: column;
    align-items: flex-end;
}
.fab-item {
    background: #FAE8D9;
    color: #4B3832;
    padding: 8px 14px;
    border-radius: 20px;
    margin: 6px 0;
    text-decoration: none;
    font-weight: 600;
    font-size: 14px;
    border: 1px solid #EED7CA;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# HTML + Streamlit 버튼 결합
with st.container():
    st.markdown('<div class="fab-container">', unsafe_allow_html=True)

    # 펼쳐진 상태일 때만 메뉴 표시
    if st.session_state.fab_open:
        st.markdown("""
        <div class="fab-menu">
            <a class="fab-item" href="https://pf.kakao.com/_example" target="_blank">💬 카카오톡 문의</a>
            <a class="fab-item" href="tel:010-1234-5678">📞 전화 문의</a>
            <a class="fab-item" href="mailto:help@foreverpet.com">✉️ 이메일 문의</a>
        </div>
        """, unsafe_allow_html=True)

    # 메인 + 버튼 (열림/닫힘 토글)
    if st.button("＋" if not st.session_state.fab_open else "✕", key="fab_button"):
        toggle_fab()

    st.markdown('</div>', unsafe_allow_html=True)
