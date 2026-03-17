import streamlit as st
import plotly.express as px
import pandas as pd
import json
import os

def render(dp):
    st.title("시간대별 교통 사고량/교통량 히트맵")

    # 1. 지도 데이터 로드
    with open("seoul_geo_gu.json", encoding='utf-8') as f:
        seoul_geo = json.load(f)

    # 2. 자치구 좌표 데이터
    seoul_gu_coords = {
        'gu': ['강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구',
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

    # 3. 데이터 선택 및 필터링
    view_option = st.radio("표시할 데이터 선택", ["사고량", "교통량"], horizontal=True)
    
    # 지표에 따른 고정 스케일 설정 부분
    if view_option == "사고량":
        map_data = dp.get_accident_map_data()
        col, label, scale = 'accidents', '사고 건수', "OrRd"
        # 사고량 전용 고정 스케일 (DB 통계값 활용)
        min_range, max_range = dp.get_accident_stats()
    else:
        map_data = dp.get_traffic_matrix_data()
        col, label, scale = 'traffic', '교통량', "Viridis_r"
        # 교통량 전용 고정 스케일 (교통량 데이터의 전체 최소/최대로 고정)
        # 만약 고정 수치를 원하시면 [0, 2500000] 처럼 직접 입력 가능합니다.
        min_range = map_data['traffic'].min()
        max_range = map_data['traffic'].max()

    time_slots = map_data['time_slot'].unique()
    selected_time = st.selectbox("시간대 선택", options=time_slots)
    filtered_map = map_data[map_data['time_slot'] == selected_time].copy()
    filtered_map = filtered_map.merge(df_coords, on='gu', how='left')

    # 4. 지도 시각화
    fig = px.choropleth_mapbox(
        filtered_map, geojson=seoul_geo, locations='gu', featureidkey="properties.구",
        color=col, color_continuous_scale=scale, 
        range_color=[min_range, max_range], # 여기서 각 지표에 맞는 고정 스케일이 적용됨
        mapbox_style="carto-positron", zoom=10.2, center={"lat": 37.5665, "lon": 126.9780},
        opacity=0.7, labels={col: label,'gu':'구'}, height = 600,
        hover_data={
            'gu': True, 
            col: ':,', #툴팁 수치에 천 단위 콤마(,) 적용
            'lat': False, 
            'lon': False
        }
    )

    fig.update_traces(
        hovertemplate=(
            "<b>자치구 : %{location}</b><br>" + 
            f"{label} : %{{z:,}}<extra></extra>"
        )
    )
    
    fig.add_scattermapbox(
        lat=filtered_map['lat'], lon=filtered_map['lon'],
        mode='text', text=filtered_map['gu'],
        textfont=dict(size=12, color="black", family="Arial Black"),
        showlegend=False, hoverinfo='skip'
    )
    
    fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"현재 선택된 데이터: {view_option} | 시간대: {selected_time} | 적용 스케일: {int(min_range)} ~ {int(max_range)}")