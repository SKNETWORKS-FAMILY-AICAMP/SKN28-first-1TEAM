import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import json
import os

def render(dp):
# -----------------------------
# 1. 제목
# -----------------------------
    st.title("서울시 교통량 Choropleth 지도")
    st.write(os.getcwd())
# -----------------------------
# 2. 데이터 불러오기
# -----------------------------
    df = pd.read_csv(r"C:\Users\test\OneDrive\Desktop\SKN28-first-1TEAM\data\processed\지역별_등록차량대비_교통량비율(2시간).csv",
                     encoding='utf-8')

    df.columns = df.columns.str.strip()

    st.write("📄 데이터 미리보기", df.head())

# -----------------------------
# 3. 시간대 선택
# -----------------------------
    time_cols = [
    "6시~8시_비율","8시~10시_비율","10시~12시_비율",
    "12시~14시_비율","14시~16시_비율","16시~18시_비율",
    "18시~20시_비율","20시~22시_비율","22시~24시_비율"
]

    target_col = st.selectbox("🕒 시간대 선택", time_cols)

    df_clean = df.dropna(subset=[target_col])
# -----------------------------
# 4. GeoJSON 불러오기 (서울 구 경계)
# -----------------------------
    import requests

    url = "https://raw.githubusercontent.com/southkorea/seoul-maps/master/kostat/2013/json/seoul_municipalities_geo_simple.json"
    geo_data = requests.get(url).json()

# -----------------------------
# 5. 지도 생성
# -----------------------------
    m = folium.Map(location=[37.55, 126.98], zoom_start=11)

# Choropleth (핵심🔥)
    folium.Choropleth(
        geo_data=geo_data,
        data=df,
        columns=["구", target_col],
        key_on="feature.properties.name",
        fill_color="YlOrRd",
        fill_opacity=0.8,
        line_opacity=0.3,
        legend_name=f"{target_col} 값"
    ).add_to(m)

# -----------------------------
# 6. Hover 시 정보 표시
# -----------------------------
    folium.GeoJson(
        geo_data,
        tooltip=folium.GeoJsonTooltip(
            fields=["name"],
            aliases=["지역:"],
            localize=True
        )
    ).add_to(m)

    st_folium(m, width=800, height=600)

# -----------------------------
# 7. 상위 / 하위 3개 지역
# -----------------------------
    top3 = df_clean.sort_values(by=target_col, ascending=False).head(3)
    bottom3 = df_clean.sort_values(by=target_col, ascending=True).head(3)

# 순위 추가
    top3["순위"] = range(1, 4)
    bottom3["순위"] = range(1, 4)

# -----------------------------
# 8. 결과 출력 (표 형태)
# -----------------------------
    st.subheader("📈 상위 3개 지역")

    st.table(
        top3[["순위", "구", target_col]].rename(columns={
            "구": "지역",
            target_col: "값"
        })
    )

    st.subheader("📉 하위 3개 지역")

    st.table(
        bottom3[["순위", "구", target_col]].rename(columns={
            "구": "지역",
            target_col: "값"
        })
    )