import streamlit as st
import plotly.express as px
import pandas as pd
import json

def render(dp):
    st.title("🚗 서울시 교통 지표 통합 분석 히트맵")

    # 2. GeoJSON 불러오기 (서울 구 경계 - 로컬 파일 권장)
    with open("app\seoul_geo_gu.json", encoding='utf-8') as f:
        seoul_geo = json.load(f)

    # 자치구 중심점 좌표 (텍스트 표시용)
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

    # 2. 지표 선택 (라디오 버튼)
    view_option = st.radio("표시할 지표를 선택하세요", ["사고 수", "교통량", "교통 포화도"], horizontal=True)

    # 3. 선택된 지표에 따라 DB에서 데이터 호출
    if view_option == "사고 수":
        map_data = dp.get_accident_map_data()
        col, label, scale = 'accidents', '사고 건수', "OrRd"
        min_range, max_range = dp.get_accident_stats()
    
    elif view_option == "교통량":
        map_data = dp.get_traffic_matrix_data()
        col, label, scale = 'traffic', '교통량', "Viridis_r"
        min_range = map_data[col].min()
        max_range = map_data[col].max()
    
    else:  # 교통 포화도 (DB JOIN을 통해 실시간 계산된 값 사용)
        # DataProvider에 추가한 get_congestion_map_data() 호출
        map_data = dp.get_congestion_map_data()
        col, label, scale = 'congestion_rate', '교통 포화도 (%)', "YlOrRd"
        min_range = map_data[col].min()
        max_range = map_data[col].max()

    # 4. 시간대 선택 필터링
    time_slots = map_data['time_slot'].unique()
    selected_time = st.selectbox("시간대 선택", options=time_slots)
    
    filtered_map = map_data[map_data['time_slot'] == selected_time].copy()
    # 좌표 데이터와 병합
    filtered_map = filtered_map.merge(df_coords, on='gu', how='left')

    # 5. Plotly 지도시각화
    fig = px.choropleth_mapbox(
        filtered_map,
        geojson=seoul_geo,
        locations='gu',
        featureidkey="properties.구",
        color=col,
        color_continuous_scale=scale,
        range_color=[min_range, max_range],
        mapbox_style="carto-positron",
        zoom=9.8,
        center={"lat": 37.5665, "lon": 126.9780},
        opacity=0.7,
        labels={'gu': '자치구', col: label},
        height=500  
    )

    val_format = ":.2f" if view_option == "교통 포화도" else ":,"
    fig.update_traces(
        hovertemplate=f"<b>자치구 : %{{location}}</b><br>{label} : %{{z{val_format}}}<extra></extra>"
    )

    # 지도 위에 구 이름 항상 표시
    fig.add_scattermapbox(
        lat=filtered_map['lat'],
        lon=filtered_map['lon'],
        mode='text',
        text=filtered_map['gu'],
        textfont=dict(size=12, color="black", family="Arial Black"),
        showlegend=False,
        hoverinfo='skip'
    )

    fig.update_layout(margin={"r":0, "t":40, "l":0, "b":0})
    
    # 지도 출력
    st.plotly_chart(fig, use_container_width=True)

    # 6. 하단 요약 정보 (선택 사항)
    st.caption(f"현재 선택된 데이터: {view_option} | 시간대: {selected_time} | 적용 스케일: {int(min_range)} ~ {int(max_range)}")