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

    # 2. 자치구별 사고 건수 그래프 (위)Z
    st.divider()

    # --- 섹션 2 & 3: 사고 건수 및 평균 혼잡도 좌우 배치 ---
    st.subheader("자치구별 주요 교통 지표 비교")
    
    # 1:1 비율로 컬럼 나누기
    col_chart_l, col_chart_r = st.columns(2)

    # 왼쪽 컬럼: 사고 건수 그래프
    with col_chart_l:
        danger_df = dp.get_danger_index().sort_values(by='total_accidents', ascending=True)
        fig_acc = px.bar(
            danger_df, x='gu', y='total_accidents',
            title="자치구별 사고 건수 순위 (적은 순)",
            color='total_accidents', 
            color_continuous_scale='Reds',
            labels={'gu': '자치구', 'total_accidents': '사고 건수(건)'},
            height=450 # 좌우 배치 시 높이를 살짝 줄이는 게 보기 좋습니다 (기존 600)
        )
        # x축 레이블 각도와 폰트 크기 조정으로 가독성 확보
        fig_acc.update_layout(
            xaxis=dict(tickangle=-45, tickfont=dict(size=10)),
            margin=dict(l=10, r=10, t=30, b=30) # 여백 조정
        )
        st.plotly_chart(fig_acc, use_container_width=True)

    # 오른쪽 컬럼: 평균 혼잡도 그래프
    with col_chart_r:
        congest_df_sorted = gu_congest_df.sort_values(by='avg_congest', ascending=True)
        fig_con = px.bar(
            congest_df_sorted, x='gu', y='avg_congest',
            title="자치구별 평균 혼잡도 순위 (낮은 순)",
            color='avg_congest', 
            color_continuous_scale='Blues',
            labels={'gu': '자치구', 'avg_congest': '평균 혼잡도'},
            height=450
        )
        # x축 레이블 각도와 폰트 크기 조정으로 가독성 확보
        fig_con.update_layout(
            xaxis=dict(tickangle=-45, tickfont=dict(size=10)),
            margin=dict(l=10, r=10, t=30, b=30) # 여백 조정
        )
        st.plotly_chart(fig_con, use_container_width=True)
