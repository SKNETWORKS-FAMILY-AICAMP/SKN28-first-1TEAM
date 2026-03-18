import streamlit as st
import plotly.express as px

def render(dp):
    st.title("2023 서울시 교통 데이터 개요")
    
    # 데이터 로드 (수정된 메서드 호출)
    summary_data = dp.get_main_summary()
    avg_total_traffic, gu_traffic_df = dp.get_total_traffic_metrics()
    
    # 1. 상단 지표 (Metric)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("총 등록 인구", f"{int(summary_data['total_pop'][0]):,} 명")
    col2.metric("총 등록 차량", f"{int(summary_data['total_cars'][0]):,} 대")
    col3.metric("총 사고 건수", f"{int(summary_data['total_accidents'][0]):,} 건")
    # 자치구별 총 교통량의 평균으로 변경
    col4.metric("총 교통량", f"{avg_total_traffic:,.0f} 대")

    st.divider()

    # 2. 자치구별 사고 건수 그래프 (기존 유지)
    danger_df = dp.get_danger_index().sort_values(by='total_accidents', ascending=True)
    fig_acc = px.bar(
        danger_df, x='gu', y='total_accidents',
        title="자치구별 사고 건수 순위 (적은 순)",
        color='total_accidents', 
        color_continuous_scale='Reds',
        labels={'gu': '자치구', 'total_accidents': '사고 건수(건)'}
    )
    fig_acc.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_acc, use_container_width=True)

    st.write("") 

    # 3. 자치구별 총 교통량 그래프 (수정 부분)
    # 'total_traffic' 기준으로 정렬
    traffic_df_sorted = gu_traffic_df.sort_values(by='total_traffic', ascending=True)
    
    fig_tra = px.bar(
        traffic_df_sorted, x='gu', y='total_traffic',
        title="자치구별 총 교통량 순위 (합계 기준)",
        color='total_traffic', 
        color_continuous_scale='Viridis',
        labels={'gu': '자치구', 'total_traffic': '총 교통량(대)'}
    )
    fig_tra.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_tra, use_container_width=True)