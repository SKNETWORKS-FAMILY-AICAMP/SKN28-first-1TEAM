import streamlit as st

def render():
    st.title("🙋 FAQ")
    with st.expander("데이터 정렬 기준은 무엇인가요?"):
        st.write("메인 페이지 차트는 사고 발생 건수가 적은 지역부터 오름차순으로 나열되어 있습니다.")