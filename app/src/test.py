# import plotly.graph_objects as go
# import numpy as np
# import streamlit as st
# import plotly.express as px

# def render(dp):
#     df = dp.get_correlation_data()
    
#     # 상관계수 계산
#     corr = df['total_traffic'].corr(df['total_accidents'])
    
#     # 1. 산점도 및 회귀선 (Plotly 버전)
#     fig = px.scatter(df, x="total_traffic", y="total_accidents", 
#                      text="time_slot",
#                      title=f"교통량 vs 사고수 상관관계 (r={corr:.3f})")
#     st.plotly_chart(fig)
    
#     # 2. 표준화된 추이 비교 (Z-score)
#     df['traffic_z'] = (df['total_traffic'] - df['total_traffic'].mean()) / df['total_traffic'].std()
#     df['accident_z'] = (df['total_accidents'] - df['total_accidents'].mean()) / df['total_accidents'].std()
    
#     fig2 = go.Figure()
#     fig2.add_trace(go.Scatter(x=df['time_slot'], y=df['traffic_z'], name="교통량(Z)"))
#     fig2.add_trace(go.Scatter(x=df['time_slot'], y=df['accident_z'], name="사고수(Z)"))
    # st.plotly_chart(fig2)

import streamlit as st
import plotly.express as px
import pandas as pd
import json
import os

def render(dp):
    st.title("🚗 서울시 구별 교통량 포화도 분석")
    st.write("등록 차량 대비 실제 교통량 비율을 통해 도로의 포화 정도를 분석합니다.")

    # 1. 데이터 불러오기 (기존 CSV 로직 유지)
    # 실제 프로젝트 환경에 맞춰 경로를 체크하세요.
    file_path = r"data/processed/지역별_등록차량대비_교통량비율(2시간).csv"
    
    if not os.path.exists(file_path):
        st.error(f"파일을 찾을 수 없습니다: {file_path}")
        return

    df = pd.read_csv(file_path, encoding='utf-8')
    df.columns = df.columns.str.strip()

    # 2. GeoJSON 불러오기 (서울 구 경계 - 로컬 파일 권장)
    with open("app/seoul_geo_gu.json", encoding='utf-8') as f:
        seoul_geo = json.load(f)

    # 3. 자치구 좌표 데이터 (텍스트 표시용)
    seoul_gu_coords = {
        '구': ['강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구',
               '노원구', '도봉구', '동대문구', '동작구', '마포구', '서대문구', '서초구', '성동구',
               '성북구', '송파구', '양천구', '영등포구', '용산구', '은평구', '종로구', '중구', '중랑구'],
        'lat': [37.4959, 37.5492, 37.639, 37.5657, 37.4653, 37.5481, 37.4954, 37.4600,
                37.652, 37.6658, 37.5838, 37.5022, 37.5622, 37.5820, 37.4769, 37.5506,
                37.6023, 37.5048, 37.5270, 37.5206, 37.5311, 37.6176, 37.5861, 37.5579, 37.5953],
        'lon': [127.0664, 127.1464, 127.0147, 126.8226, 126.9438, 127.0857, 126.8581, 126.9007,
                127.07, 127.0317, 127.0507, 126.9443, 126.9087, 126.9356, 127.0158, 127.0406,
                127.0252, 127.1144, 126.8565, 126.9139, 126.9795, 126.9227, 126.9837, 126.9941, 127.0903]
    }
    df_coords = pd.DataFrame(seoul_gu_coords)

    # 4. 시간대 선택
    time_cols = [
        "6시~8시_비율","8시~10시_비율","10시~12시_비율",
        "12시~14시_비율","14시~16시_비율","16시~18시_비율",
        "18시~20시_비율","20시~22시_비율","22시~24시_비율"
    ]
    target_col = st.selectbox("🕒 분석 시간대 선택", time_cols)

    # 데이터 정제 및 좌표 병합
    df_clean = df.dropna(subset=[target_col]).copy()
    df_map = df_clean.merge(df_coords, on='구', how='left')

    # 5. 지도 시각화 (사고수 히트맵 스타일 적용)
    # 비율 데이터이므로 0~1 사이거나 백분율일 것을 고려하여 스케일 설정
    min_val = df_map[target_col].min()
    max_val = df_map[target_col].max()

    fig = px.choropleth_mapbox(
        df_map, 
        geojson=seoul_geo, 
        locations='구', 
        featureidkey="properties.구",
        color=target_col, 
        color_continuous_scale="YlOrRd", # 교통량 혼잡을 나타내는 노랑-빨강 스케일
        range_color=[min_val, max_val],
        mapbox_style="carto-positron", 
        zoom=10, 
        center={"lat": 37.5665, "lon": 126.9780},
        opacity=0.7,
        labels={'구': '자치구', target_col: '포화도 비율'},
        height=700 # 세로 크기 확장
    )

    # 툴팁 스타일 통일 ( : 사용 및 숫자 포맷)
    fig.update_traces(
        hovertemplate=(
            "<b>자치구 : %{location}</b><br>" + 
            f"교통 포화도 : %{{z:.2f}}%<extra></extra>" 
        )
    )

    # 지도 내부에 자치구 이름 표시
    fig.add_scattermapbox(
        lat=df_map['lat'], lon=df_map['lon'],
        mode='text', text=df_map['구'],
        textfont=dict(size=11, color="black"),
        showlegend=False, hoverinfo='skip'
    )

    fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
    st.plotly_chart(fig, use_container_width=True)

    # 6. 상/하위 순위 표시 (기존 로직 유지)
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 포화도 상위 3지역")
        top3 = df_clean.nlargest(3, target_col)
        for i, (idx, row) in enumerate(top3.iterrows()):
            st.write(f"**{i+1}위**: {row['구']} ({row[target_col]:.2f}%)")

    with col2:
        st.subheader("📉 포화도 하위 3지역")
        bottom3 = df_clean.nsmallest(3, target_col)
        for i, (idx, row) in enumerate(bottom3.iterrows()):
            st.write(f"**{i+1}위**: {row['구']} ({row[target_col]:.2f}%)")