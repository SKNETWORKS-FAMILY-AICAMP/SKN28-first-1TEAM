import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

def render(dp):
    st.title("안전 운전 가이드")
    st.markdown("서울시 공공데이터 기반, 교통량과 사고 발생률을 종합 분석한 결과입니다.")
    
    col1, col2 = st.columns(2)
    with col1:
        gu_list = ["강남구", "강동구", "강북구", "강서구", "관악구", "광진구", "구로구", "금천구", "노원구", "도봉구", "동대문구", "동작구", "마포구", "서대문구", "서초구", "성동구", "성북구", "송파구", "양천구", "영등포구", "용산구", "은평구", "종로구", "중구", "중랑구"]
        selected_gu = st.selectbox("목적지 선택", gu_list)
    with col2:
        # 1. 시각적으로 '시'가 붙은 리스트 생성
        display_time_list = ["06~08시", "08~10시", "10~12시", "12~14시", "14~16시", "16~18시", "18~20시", "20~22시", "22~24시"]
        selected_time_display = st.selectbox("시간 선택", display_time_list)
        
        # 2. DB 조회를 위해 '시'를 제거한 원래 형식으로 변환
        selected_time = selected_time_display.replace("시", "")

    if st.button("위험도 분석 실행", use_container_width=True):
        data = dp.get_driving_score(selected_gu, selected_time)
        
        if not data.empty:
            acc = int(data['accidents'].iloc[0])
            traffic = int(data['traffic'].iloc[0])
            freq = int(data['congestion_frequency'].iloc[0])
            
            # --- [밸런스 조정 로직] ---
            # 1. 사고 점수 (23~525 스케일)
            acc_score = (np.sqrt(acc) - np.sqrt(23)) / (np.sqrt(525) - np.sqrt(23)) * 100
            
            # 2. 교통량 점수 (8.7만 ~ 216만 스케일)
            traffic_score = ((traffic - 87017) / (1800000 - 87017)) * 100
            
            # 점수 범위 제한 (0~100)
            acc_score = min(100, max(0, acc_score))
            traffic_score = min(100, max(0, traffic_score))
            
            # 3. 최종 통합 위험 점수 (가중치 밸런스)
            final_score = int((acc_score * 0.4) + (freq * 0.3) + (traffic_score * 0.3))

            # --- [결과 출력] ---
            st.divider()
            
            if final_score >= 75: 
                st.error(f"### 최종 위험 지수: {final_score}점 - 🔴 매우 위험")
                st.markdown(f"**{selected_gu}**의 **{selected_time_display}**는 현재 교통 흐름이 매우 정체되며 사고 밀도가 높습니다.")
            elif final_score >= 40: 
                st.warning(f"### 최종 위험 지수: {final_score}점 - 🟡 주의")
                st.markdown(f"**{selected_gu}**의 **{selected_time_display}**는 차량이 다소 많고 흐름이 답답할 수 있습니다.")
            else:
                st.success(f"### 최종 위험 지수: {final_score}점 - 🟢 양호")
                st.markdown(f"**{selected_gu}**의 **{selected_time_display}**는 전반적으로 쾌적하고 안전한 주행이 가능합니다.")

            # 시각화: 레이더 차트
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=[acc_score, freq, traffic_score],
                theta=['사고 지수', '혼잡 빈도', '교통 밀집도'],
                fill='toself',
                line=dict(color='#FF4B4B')
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=False, height=450
            )
            st.plotly_chart(fig, use_container_width=True)

            # 상세 지표 메트릭
            m1, m2, m3 = st.columns(3)
            m1.metric("사고 건수", f"{acc}건")
            m2.metric("총 교통량", f"{traffic:,}대")
            m3.metric("혼잡 빈도", f"{freq}%")