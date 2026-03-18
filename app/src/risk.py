import streamlit as st
import plotly.express as px
px.defaults.color_discrete_sequence = px.colors.qualitative.Alphabet


def render(dp):
    st.title("교통 혼잡도 / 사고 위험지수 분석")
    st.divider()
    st.subheader("사고 위험지수")
    # 1. 정의 및 분석 가이드
    st.info("""
    💡 **위험 지수란?** 교통량 대비 발생하는 사고 건수를 의미하며, 수치가 높을수록 교통 안전이 취약함을 나타냅니다.  
    아래 차트에서 **원의 크기가 클수록** 해당 구의 위험 지수가 높음을 의미합니다.
    """)

    df = dp.get_danger_index()
    
    # 위험 지수 계산
    df['danger_score'] = (df['total_accidents'] / df['total_traffics']) * 100000
    
    # 2. 주요 지표 요약 (Metric Card)
    max_danger_gu = df.loc[df['danger_score'].idxmax()]
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("가장 위험 지수가 높은 구", f"{max_danger_gu['gu']}")
    with col_b:
        st.metric("최고 위험 지수", f"{max_danger_gu['danger_score']:.2f}", delta="주의 필요", delta_color="inverse")

    st.divider()

    # 3. 상단 차트: 버블 차트 (상관관계 분석)
    st.subheader("교통량과 사고 발생의 상관관계")
    fig1 = px.scatter(
        df, x="total_traffics", y="total_accidents", 
        size="danger_score", color="gu",
        hover_name="gu",
        size_max=50, 
        template="plotly_white",
        labels={'total_traffics': '총 교통량', 'total_accidents': '총 사고 건수'},
        title="원의 크기: 인구 대비 위험도"
    )
    fig1.update_layout(height=600)
    st.plotly_chart(fig1, use_container_width=True)

    st.divider()

    # 4. 하단 상세 분석: 위험 지수 TOP 5 강조 (주영님이 요청하신 부분)
    st.subheader("자치구별 위험 지수 상세 분석")
    
    # 데이터 정렬 (위험 지수 높은 순)
    df_sorted = df.sort_values(by='danger_score', ascending=False).reset_index(drop=True)
    
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        st.error("**위험 지수 상위 TOP 5**")
        # 1위부터 5위까지 루프를 돌며 깔끔하게 표시
        for i in range(5):
            gu_name = df_sorted.iloc[i]['gu']
            score = df_sorted.iloc[i]['danger_score']
            st.write(f"**{i+1}위 : {gu_name}** ({score:.2f})")

    with col2:
        st.success("**분석요약**")
        # 분석 인사이트 텍스트
        st.write(f"""
        현재 데이터 분석 결과, **{max_danger_gu['gu']}** 지역이 인구 대비 사고 발생률이 가장 높게 나타났습니다. 
        이는 단순히 차량이 많은 것과는 별개로, 해당 지역의 **도로 구조, 유동 인구의 특성, 혹은 교통 안전 시설의 부족** 등이 원인일 수 있습니다.
        
        - **중점 관리 대상**: 상위 5개 구역 ({', '.join(df_sorted['gu'][:5])})
        - **권고 사항**: 해당 지역 내 교통 법규 준수 캠페인 및 사고 다발 구역 정밀 진단 필요
        """)

    st.divider()
    # 마지막 강조 문구
    st.warning(f"💡 분석 결과 서울시 교통 안전 최우선 관리 자치구는 **{max_danger_gu['gu']}**입니다.")

    st.divider()
    
    st.header("교통 혼잡도")
    try:
        df = dp.get_integrated_indices()
    except Exception as e:
        st.error(f"데이터베이스에서 지표를 계산하는 중 오류가 발생했습니다: {e}")
        return
    
    chart_col1, chart_col2 = st.columns(2)

    # 왼쪽 컬럼: 안전 지수
    with chart_col1:
        st.markdown("#### 자치구별 안전 지수 (낮을수록 안전)")
        df_safety = df.sort_values('safety_index', ascending=False)
        
        fig_safety = px.bar(
            df_safety, x='gu', y='safety_index',
            color='safety_index', 
            color_continuous_scale='Blues',
            labels={'gu': '자치구', 'safety_index': '안전 지수'},
            height=450  # 좌우 배치 시 높이를 살짝 줄이는 게 보기 좋습니다
        )
        fig_safety.update_layout(
        xaxis=dict(
        tickmode='linear',
        tickangle=0,            
        tickfont=dict(size=10)  
    ),
    margin=dict(l=10, r=10, t=40, b=50),
    height=450
)
        fig_safety.update_layout(xaxis_tickangle=-45, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_safety, use_container_width=True)
        st.caption("※ 낮을수록 등록 차량 대비 사고 위험도가 낮음")

    # 오른쪽 컬럼: 혼잡 지수
    with chart_col2:
        st.markdown("#### 자치구별 혼잡 지수 (낮을수록 쾌적)")
        df_congest = df.sort_values('congestion_index', ascending=False)
        
        fig_congest = px.bar(
            df_congest, x='gu', y='congestion_index',
            color='congestion_index', 
            color_continuous_scale='YlOrRd',
            labels={'gu': '자치구', 'congestion_index': '혼잡 지수'},
            height=450
        )
        fig_congest.update_layout(
            xaxis=dict(
                tickmode='linear',
                tickangle=-45,            
                tickfont=dict(size=10)  
            ),
            margin=dict(l=10, r=10, t=30, b=50),
            height=450
        )
        st.plotly_chart(fig_congest, use_container_width=True)
        st.caption("※ 도로의 정체 빈도와 지속 시간을 결합한 수치")

    st.divider()