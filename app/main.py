import streamlit as st
import json
import os
from data_provider import DataProvider
# 분리된 페이지들을 임포트
from src import summary, accident_hitmap, traffic, risk, faq, advisor, traffic_vol

st.set_page_config(page_title="2023 서울 교통 대시보드", layout="wide")
dp = DataProvider()

# 리소스 로드
@st.cache_data
def load_geo():
    JSON_PATH = os.path.join(os.path.dirname(__file__), 'seoul_geo_gu.json')
    with open(JSON_PATH, encoding='utf-8') as f:
        return json.load(f)

seoul_geo = load_geo()

# 사이드바 메뉴
st.sidebar.title("🚗 Seoul Traffic 2023")
menu = st.sidebar.selectbox("메뉴 선택", ["전체 요약", "사고 지도 히트맵", "종합 지수 분석", "위험 지수 분석",
                                      "운전 가이드","test", "FAQ"])

# 페이지 라우팅 (선택된 메뉴에 따라 해당 파일의 render 함수 실행)
if menu == "전체 요약":
    summary.render(dp)
elif "종합 지수 분석" in menu:
    traffic.render(dp)
elif menu == "위험 지수 분석":
    risk.render(dp)
elif menu == "사고 지도 히트맵":
    accident_hitmap.render(dp)
elif menu == "운전 가이드":
    advisor.render(dp)
elif menu == "test":
    traffic_vol.render(dp)
elif menu == "FAQ":
    faq.render()
    
# elif "종합 지수 분석" in menu:
#   traffic.render(dp)