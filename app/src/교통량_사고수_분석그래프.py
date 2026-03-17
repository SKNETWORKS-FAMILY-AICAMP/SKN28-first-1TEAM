import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# -----------------------------
# 한글 폰트 설정 (강제 적용)
# -----------------------------
font_path = "C:/Windows/Fonts/malgun.ttf"   # 윈도우 맑은 고딕
font_prop = fm.FontProperties(fname=font_path)

plt.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['axes.unicode_minus'] = False

# -----------------------------
# 제목
# -----------------------------
st.title("서울시 시간대별 교통량 vs 사고 분석")

# -----------------------------
# 파일 경로 (수정 가능)
# -----------------------------
traffic_file = r"C:\Users\Playdata\Desktop\1st_project\서울_권역별_시간대_교통량_수정.csv"
accident_file = r"C:\Users\Playdata\Desktop\1st_project\서울_권역별_시간대_사고수_수정.csv"

# -----------------------------
# 데이터 불러오기
# -----------------------------
traffic_df = pd.read_csv(traffic_file, encoding="utf-8")
accident_df = pd.read_csv(accident_file, encoding="utf-8")

# -----------------------------
# 시간대 컬럼
# -----------------------------
time_cols = [
    "6시~8시","8시~10시","10시~12시","12시~14시",
    "14시~16시","16시~18시","18시~20시",
    "20시~22시","22시~24시"
]

# -----------------------------
# 서울 전체 합계
# -----------------------------
traffic_total = traffic_df[time_cols].sum()
accident_total = accident_df[time_cols].sum()

summary_df = pd.DataFrame({
    "시간대": time_cols,
    "교통량": traffic_total.values,
    "사고수": accident_total.values
})

# -----------------------------
# 표 출력
# -----------------------------
st.subheader("📊 시간대별 데이터")
st.dataframe(summary_df)

# -----------------------------
# 상관계수
# -----------------------------
corr = summary_df["교통량"].corr(summary_df["사고수"])
st.subheader("📈 상관계수")
st.write(f"교통량 vs 사고수 상관계수: {corr:.3f}")

# -----------------------------
# 산점도 + 회귀선
# -----------------------------
st.subheader("📍 교통량 vs 사고수 산점도")

x = summary_df["교통량"]
y = summary_df["사고수"]

coef = np.polyfit(x, y, 1)
trend = np.poly1d(coef)

x_line = np.linspace(x.min(), x.max(), 100)
y_line = trend(x_line)

fig1, ax1 = plt.subplots()
ax1.scatter(x, y)

for i in range(len(summary_df)):
    ax1.text(x[i], y[i], summary_df["시간대"][i])

ax1.plot(x_line, y_line)
ax1.set_xlabel("교통량")
ax1.set_ylabel("사고수")
ax1.set_title(f"상관관계 (r={corr:.3f})")

st.pyplot(fig1)

# -----------------------------
# 표준화
# -----------------------------
summary_df["교통량_z"] = (
    summary_df["교통량"] - summary_df["교통량"].mean()
) / summary_df["교통량"].std()

summary_df["사고수_z"] = (
    summary_df["사고수"] - summary_df["사고수"].mean()
) / summary_df["사고수"].std()

# -----------------------------
# 교통량 그래프
# -----------------------------
st.subheader("🚗 시간대별 교통량 변화")

fig2, ax2 = plt.subplots()
ax2.plot(summary_df["시간대"], summary_df["교통량_z"], marker="o")
ax2.set_xlabel("시간대")
ax2.set_ylabel("교통량 (z-score)")
ax2.set_title("교통량 변화")
plt.xticks(rotation=45)

st.pyplot(fig2)

# -----------------------------
# 사고수 그래프
# -----------------------------
st.subheader("🚑 시간대별 사고수 변화")

fig3, ax3 = plt.subplots()
ax3.plot(summary_df["시간대"], summary_df["사고수_z"], marker="o")
ax3.set_xlabel("시간대")
ax3.set_ylabel("사고수 (z-score)")
ax3.set_title("사고수 변화")
plt.xticks(rotation=45)

st.pyplot(fig3)