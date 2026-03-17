import streamlit as st

def render(dp):
    st.title("🚗 AI 운전 가이드")
    
    col1, col2 = st.columns(2)
    with col1:
        gu_list = ["강남구", "강동구", "강북구", "강서구", "관악구", "광진구", "구로구", "금천구", "노원구", "도봉구", "동대문구", "동작구", "마포구", "서대문구", "서초구", "성동구", "성북구", "송파구", "양천구", "영등포구", "용산구", "은평구", "종로구", "중구", "중랑구"]
        selected_gu = st.selectbox("목적지 선택", gu_list)
    with col2:
        time_list = ["06~08", "08~10", "10~12", "12~14", "14~16", "16~18", "18~20", "20~22", "22~24"]
        selected_time = st.selectbox("시간 선택", time_list)

    if st.button("분석 시작"):
        data = dp.get_driving_score(selected_gu, selected_time)
        
        # LEFT JOIN을 썼으므로 데이터프레임 자체는 비어있지 않을 확률이 높음
        if not data.empty:
            acc = int(data['accidents'].iloc[0])
            traffic = int(data['traffic'].iloc[0])
            freq = int(data['congestion_frequency'].iloc[0])
            
            # 모든 값이 0이라면 데이터 매칭에 실패한 것임
            if acc == 0 and traffic == 0 and freq == 0:
                st.error(f"❌ '{selected_gu}'의 '{selected_time}' 데이터를 찾을 수 없습니다.")
                st.info("DB의 시간대(time_slot) 형식이 '06~08'과 일치하는지 확인이 필요합니다.")
                return

            # 1. 사고 위험 기여도 (최대 60점 할당)
            # 사고 건수가 500건일 때 60점 만점에 도달한다고 가정
            acc_danger = (acc / 500) * 60
            acc_danger = min(60, acc_danger) # 60점 상한선

            # 2. 혼잡 위험 기여도 (최대 40점 할당)
            # 혼잡 빈도(%) 수치의 40%를 점수화 (예: 100% 혼잡이면 40점)
            congest_danger = freq * 0.4

            # 3. 최종 위험 점수 산출
            final_score = int(acc_danger + congest_danger)

            # 100점이 넘지 않도록 제한
            final_score = min(100, final_score)

            # 점수에 따른 상태 출력 (위험할수록 높은 점수)
            # src/advisor.py 내 결과 출력 부분 수정

            if not data.empty:
                acc = int(data['accidents'].iloc[0])
                traffic = int(data['traffic'].iloc[0])
                freq = int(data['congestion_frequency'].iloc[0])
                
                # 1. 위험 점수 계산 (높을수록 위험)
                acc_danger = min(60, (acc / 500) * 60)
                congest_danger = min(40, freq * 0.4)
                final_score = int(acc_danger + congest_danger)

                st.divider()

                # 2. 점수별 메인 타이틀
                if final_score >= 80:
                    st.error(f"### 분석 결과: {final_score}점 - 🔴 위험도가 매우 높습니다!")
                elif final_score >= 40:
                    st.warning(f"### 분석 결과: {final_score}점 - 🟡 주의가 필요한 단계입니다.")
                else:
                    st.success(f"### 분석 결과: {final_score}점 - 🟢 비교적 안전하고 원활합니다.")

                # 3. 지표별 구체적인 상세 설명 생성
                descriptions = []

                # 사고 관련 설명
                if acc >= 300:
                    descriptions.append(f"🚨 **사고 위험 극심**: 해당 시간대 사고가 **{acc}건**으로 매우 빈번하게 발생합니다. 급정거와 차선 변경에 각별히 유의하세요.")
                elif acc >= 100:
                    descriptions.append(f"⚠️ **사고 주의**: 사고 발생이 적지 않은 편입니다. 전방 주시를 철저히 하세요.")
                else:
                    descriptions.append(f"✅ **사고 낮음**: 사고 발생 건수가 낮아 상대적으로 안전한 주행이 가능합니다.")

                # 혼잡도 관련 설명
                if freq >= 70:
                    descriptions.append(f"🚗 **도로 마비**: 혼잡 빈도가 **{freq}%**에 달해 거의 모든 구간에서 정체가 예상됩니다. 우회 도로를 권장합니다.")
                elif freq >= 30:
                    descriptions.append(f"🐢 **서행 예상**: 차량 흐름이 다소 답답할 수 있습니다. 예상 소요 시간보다 여유 있게 출발하세요.")
                else:
                    descriptions.append(f"🏃 **소통 원활**: 정체 구간이 거의 없어 소통이 매우 원활한 상태입니다.")

                # 4. 설명란 출력
                st.info("\n\n".join(descriptions))

            m1, m2, m3 = st.columns(3)
            m1.metric("사고 건수", f"{acc} 건")
            m2.metric("통행량", f"{traffic:,}")
            m3.metric("혼잡 빈도", f"{freq}%")