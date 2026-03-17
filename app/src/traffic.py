import streamlit as st
import plotly.express as px

def render(dp):
    st.title("⚖️ 자치구별 종합 지수 분석")
    st.info("사고 심각도를 반영한 **안전 지수**와 통행 정체를 반영한 **혼잡 지수**를 분석합니다.")
    
    # 1. 데이터 로드
    try:
        df = dp.get_integrated_indices()
    except Exception as e:
        st.error(f"데이터베이스에서 지표를 계산하는 중 오류가 발생했습니다: {e}")
        return

    # --- 섹션 1: 안전 지수 ---
    st.subheader("🛡️ 자치구별 안전 지수 (낮을수록 안전)")
    # 안전 지수 식: ((사고*0.4 + 사상자*0.6) / 차량수) * 10
    df_safety = df.sort_values('safety_index', ascending=True)
    
    fig_safety = px.bar(
        df_safety, x='gu', y='safety_index',
        color='safety_index', 
        color_continuous_scale='Blues', # 낮을수록 연한 파란색
        labels={'gu': '자치구', 'safety_index': '안전 지수'}
    )
    fig_safety.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_safety, use_container_width=True)
    st.caption("※ 안전 지수가 낮을수록 해당 자치구의 등록 차량 대비 사고 위험도가 낮음을 의미합니다.")

    st.divider()

    # --- 섹션 2: 혼잡 지수 ---
    st.subheader("🚦 자치구별 혼잡 지수 (낮을수록 쾌적)")
    # 혼잡 지수 식: (혼잡빈도 + 혼잡시간) / 2
    df_congest = df.sort_values('congestion_index', ascending=True)
    
    fig_congest = px.bar(
        df_congest, x='gu', y='congestion_index',
        color='congestion_index', 
        color_continuous_scale='YlOrRd', # 낮을수록 노란색, 높을수록 빨간색
        labels={'gu': '자치구', 'congestion_index': '혼잡 지수'}
    )
    fig_congest.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_congest, use_container_width=True)
    st.caption("※ 혼잡 지수는 도로의 정체 빈도와 지속 시간을 결합한 수치입니다.")

    st.divider()

    # --- 섹션 3: 상관관계 분석 ---
    st.subheader("🧪 안전 vs 혼잡 상관관계 분석")
    fig_scatter = px.scatter(
        df, x="congestion_index", y="safety_index", 
        color="gu", hover_name="gu", 
        size=[15]*len(df),
        labels={'congestion_index': '혼잡 지수', 'safety_index': '안전 지수'},
        title="교통 혼잡도와 안전 지수의 분포"
    )
    # 추세선 등을 시각적으로 파악하기 좋은 산점도
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.write("상단으로 갈수록 **위험**하고, 우측으로 갈수록 **혼잡**한 자치구입니다.")