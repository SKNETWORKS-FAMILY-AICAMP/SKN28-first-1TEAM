import streamlit as st
import plotly.express as px

def render(dp):
    st.title("🧪 인구/차량 대비 사고 위험도 분석")
    df = dp.get_danger_index()
    df['danger_score'] = (df['total_accidents'] / df['population_count']) * 10000
    fig = px.scatter(df, x="car_count", y="total_accidents", size="danger_score", color="gu", hover_name="gu")
    st.plotly_chart(fig, use_container_width=True)