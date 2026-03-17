import streamlit as st
import plotly.express as px

def render(dp, seoul_geo):
    st.title("📍 시간대별 사고 발생 지도")
    map_data = dp.get_accident_map_data()
    min_acc, max_acc = dp.get_accident_stats()
    
    time_order = ['6시~8시', '8시~10시', '10시~12시', '12시~14시', '14시~16시', '16시~18시', '18시~20시', '20시~22시', '22시~24시']
    selected_time = st.selectbox("시간대 분석", options=time_order)
    
    filtered_map = map_data[map_data['time_slot'] == selected_time]
    
    fig = px.choropleth_mapbox(
        filtered_map, geojson=seoul_geo, locations='gu', featureidkey="properties.구",
        color='accidents', color_continuous_scale="Reds", range_color=[min_acc, max_acc],
        mapbox_style="carto-positron", zoom=9.7, center={"lat": 37.5665, "lon": 126.9780},
        opacity=0.7
    )
    fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
    st.plotly_chart(fig, use_container_width=True)