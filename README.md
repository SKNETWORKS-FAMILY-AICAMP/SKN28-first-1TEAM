# 서울시 교통 데이터 분석 프로젝트
> **지역별 차량 등록, 교통 혼잡도 및 안전도 분석을 통한 교통 인사이트 제공**

## 팀 소개
| <img src="https://github.com/user-attachments/assets/a0f39641-5049-4efe-8a72-0132eb956e3d" width="160"> | <img src="https://github.com/user-attachments/assets/fdd955dd-9d82-4aa3-af73-601e76b5fb2c" width="160"> | <img src="https://github.com/user-attachments/assets/ff8fbfd1-b3b8-4851-9f87-99f33d83db5b" width="160"> | <img src="https://github.com/user-attachments/assets/b5e12a17-a3c9-41e4-9c66-df2f62bf3004" width="160">| <img src="https://github.com/user-attachments/assets/438912d8-f1f9-405e-8a65-b4d6e5024875" width="160"> |
| :---: | :---: | :---: | :---: | :---: |
|김민욱|김주영|심기성|심윤성|임한샘|

**개발 기간:** 2025.03.17 - 2025.03.18 (총 2일)

## 프로젝트 개요

### 1. 주제
**서울시 자치구별 자동차 등록 대수와 교통량, 교통사고 발생 건수의 상관관계 분석**
- 단순 수치 나열을 넘어, 특정 지역의 차량 보유량이 실제 교통 혼잡도나 사고 발생에 미치는 **기여도를 수치화**

### 2. 선정 배경
- **공급과 수요의 괴리:** 차량 등록 대수(공급)와 실제 교통량(수요) 사이의 차이를 분석하여 교통 정책의 사각지대 확인
- **데이터 기반 근거:** 등록 대수와 사고 발생 사이의 명확한 통계적 근거 확보

### 3. 프로젝트 목표
- **DB 통합:** 분산된 공공데이터(3종 이상)를 MySQL로 통합 및 정규화된 DB 구축
- **인과관계 도출:** 데이터 간의 통계적 상관계수 및 분석 지표 산출
- **서비스 구현:** 사용자가 지역 선택 시 위험도/혼잡도를 한눈에 파악하는 **Streamlit** 기반 서비스 구현

### 4. 기대효과
- 도심 교통 유입 패턴 시각화를 통한 **효율적 교통 관리** 기여
- 등록 차량 대비 사고율이 높은 **'교통 안전 취약 지역'** 식별 및 대책 근거 마련
- 공공데이터 핸들링 역량 강화 및 **데이터 기반 의사결정** 프로세스 체득

- ---

## 기술 스택 (Tech Stack)
- **Language:** `Python 3.10+`
- **Database:** `MySQL`
- **Web Framework:** `Streamlit`
- **Visualization:** `Plotly`, `Pandas`, `Matplotlib`

## 사용한 데이터
시간 별 교통량 테이터 
https://viewt.ktdb.go.kr/cong/map/TableMove_Zeke.do 

시간 별 교통 사고 수, 교통사고 사상자 수 데이터 
https://taas.koroad.or.kr/sta/acs/exs/typical.do?menuId=WEB_KMP_OVT_UAS_ASA

지역 별 차량 등록 수 데이터
https://kosis.kr/statHtml/statHtml.do?sso=ok&returnurl=https%3A%2F%2Fkosis.kr%3A443%2FstatHtml%2FstatHtml.do%3FtblId%3DDT_MLTM_5498%26orgId%3D116%26

## 파일구조

```text
SKN28-FIRST-1TEAM/
├── app/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── accident_hitmap.py  # 교통사고 히트맵 시각화 모듈
│   │   ├── advisor.py           # 분석 결과 기반 어드바이저 모듈
│   │   ├── faq.py               # 프로젝트 안내 및 FAQ 페이지
│   │   ├── risk.py              # 자치구별 위험도 분석 모듈
│   │   ├── summary.py           # 전체 데이터 요약 및 통계
│   │   └── traffic_vol.py       # 교통량 분석 및 시각화 모듈
│   ├── data_provider.py         # DB 데이터 로드 및 전처리 모듈
│   ├── main.py                  # Streamlit 메인 실행 파일
│   └── seoul_geo_gu.json        # 서울시 자치구 경계 GeoJSON 데이터
├── data/
│   ├── processed/               # 전처리 완료된 CSV 데이터
│   └── raw/                     # 수집된 원천 데이터 (Raw Data)
├── database/
│   ├── db_making.sql            # MySQL 테이블 생성 스크립트
│   └── excel_to_db.py           # Excel 데이터를 DB로 적재하는 스크립트
├── requirements.txt             # 프로젝트 의존성 라이브러리 목록
└── README.md                    # 프로젝트 설명 문서
```

## 데이터베이스 구조 
<img width="800" height="500" alt="image" src="https://github.com/user-attachments/assets/549ab063-296d-4b5b-b325-32c38af535f0" />

- ---
### 5. 프로젝트 결과
- 서울시 각 자치구별 자동차 등록 대수와 교통량, 교통사고 발생 건수 등의 상관 관계를 다각도로 분석
- 개별 수치를 나열하는 것이 아니라, 특정 지역의 차량 보유량이 실제 교통 혼잡도나 사고 발생에 얼마나 기여도를 가지는지 수치화
- Python과 MySQL을 활용해 데이터를 가공하고, Streamlit 기반의 시각화를 통해 지역별 교통 정보를 제공

