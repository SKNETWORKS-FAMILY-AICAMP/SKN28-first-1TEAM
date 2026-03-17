import streamlit as st
import plotly.express as px

def render(dp):
    st.title("📊 2023 서울시 교통 데이터 개요")
    
    # 데이터 로드
    summary_data = dp.get_main_summary()
    total_avg_congest, gu_congest_df = dp.get_congestion_metrics()
    
    # 1. 상단 지표 (Metric) - 4칸 구성
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("총 등록 인구", f"{int(summary_data['total_pop'][0]):,} 명")
    col2.metric("총 등록 차량", f"{int(summary_data['total_cars'][0]):,} 대")
    col3.metric("총 사고 건수", f"{int(summary_data['total_accidents'][0]):,} 건")
    col4.metric("평균 혼잡도", f"{total_avg_congest:,.0f} 대")

    st.divider()

    # 2. 자치구별 사고 건수 그래프 (위)
    danger_df = dp.get_danger_index().sort_values(by='total_accidents', ascending=True)
    fig_acc = px.bar(
        danger_df, x='gu', y='total_accidents',
        title="자치구별 사고 건수 순위 (적은 순)",
        color='total_accidents', 
        color_continuous_scale='Reds',
        labels={'gu': '자치구', 'total_accidents': '사고 건수(건)'}
    )
    # x축 레이블 각도 조정으로 가독성 확보
    fig_acc.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_acc, use_container_width=True)

    st.write("") # 간격 조절용 빈 줄

    # 3. 자치구별 평균 혼잡도 그래프 (아래)
    congest_df_sorted = gu_congest_df.sort_values(by='avg_congest', ascending=True)
    fig_con = px.bar(
        congest_df_sorted, x='gu', y='avg_congest',
        title="자치구별 평균 혼잡도 순위 (낮은 순)",
        color='avg_congest', 
        color_continuous_scale='Viridis',
        labels={'gu': '자치구', 'avg_congest': '평균 혼잡도'}
    )
    fig_con.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_con, use_container_width=True)