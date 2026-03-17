import pandas as pd
import mysql.connector

######### sql 아이디 비번 변경
# --- 1. DB 및 파일 설정 ---
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'practice',
    'password': 'practice',
    'database': '1st_project_db'
}


######### 파일 위치에 맞게 변경
FILES = {
    'population': 'first_project/data/등록인구_20260314203932.csv',
    'car_reg': 'first_project/data/자동차등록(월별_구별)_20260314203841.csv',
    'traffic': 'first_project/data/서울_권역별_시간대_교통량_수정.csv',
    'accident': 'first_project/data/서울_권역별_시간대_사고수_수정.csv',
    'casualties': 'first_project/data/서울_권역별_시간대_사상자수_수정.csv',
    'congestion': 'first_project/data/서울_권역별_혼잡강도.csv'
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

try:
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. 지역 매핑 정보 가져오기
    cursor.execute("SELECT local_codes, local_name FROM locals")
    region_map = {name.strip(): code for (code, name) in cursor.fetchall()}

    # 2. 인구 데이터 
    df_pop = pd.read_csv(FILES['population'], skiprows=3)
    df_pop_clean = df_pop.iloc[:, [1, 2]].copy() 
    df_pop_clean.columns = ['name', 'value']
    df_pop_clean = df_pop_clean[df_pop_clean['name'] != '소계'].dropna()
    
    pop_data = [(region_map[r['name'].strip()], int(str(r['value']).replace(',', ''))) 
                for _, r in df_pop_clean.iterrows() if r['name'].strip() in region_map]
    
    cursor.execute("DELETE FROM populations")
    cursor.executemany("INSERT INTO populations (local_code_pop, population_count) VALUES (%s, %s)", pop_data)
    print(f"인구(전체 합계) 적재 완료: {len(pop_data)}건")

    # 3. 자동차 등록 데이터
    df_car = pd.read_csv(FILES['car_reg'], skiprows=4).iloc[:, [1, 2]]
    df_car.columns = ['name', 'value']
    df_car = df_car[df_car['name'] != '소계'].dropna()
    car_data = [(region_map[r['name'].strip()], int(str(r['value']).replace(',', ''))) 
                for _, r in df_car.iterrows() if r['name'].strip() in region_map]
    cursor.execute("DELETE FROM car_reg")
    cursor.executemany("INSERT INTO car_reg (local_code_reg, car_count) VALUES (%s, %s)", car_data)
    print(f"자동차 등록 데이터 적재 완료: {len(car_data)}건")

    # 4. 혼잡강도 데이터
    df_con = pd.read_csv(FILES['congestion'])
    con_data = []
    for _, r in df_con.iterrows():
        name = r['권역'].strip()
        if name in region_map:
            freq = int(str(r['혼잡빈도강도(%)']).replace('%', '').replace(',', ''))
            t_intensity = int(str(r['혼잡시간강도(%)']).replace('%', '').replace(',', ''))
            con_data.append((region_map[name], freq, t_intensity))
    cursor.execute("DELETE FROM congestion")
    cursor.executemany("INSERT INTO congestion (local_code_congestion, congestion_frequency, congestion_time) VALUES (%s, %s, %s)", con_data)
    print(f"혼잡강도 데이터 적재 완료: {len(con_data)}건")

    # 5. 시간대별 공통 처리 함수 (교통량, 사고수, 사상자수)
    def process_time_data(file_key, table_name, fk_col):
        df = pd.read_csv(FILES[file_key])
        id_col = df.columns[0] 
        df_melted = df.melt(id_vars=[id_col], var_name='time_slot', value_name='val')
        
        to_insert = []
        for _, r in df_melted.iterrows():
            name = r[id_col].strip()
            if name in region_map:
                val_str = str(r['val']).replace(',', '')
                val = int(float(val_str)) if val_str not in ['nan', 'None', ''] else 0
                to_insert.append((region_map[name], r['time_slot'], val))
        
        cursor.execute(f"DELETE FROM {table_name}")
        cursor.executemany(f"INSERT INTO {table_name} ({fk_col}, time_slot, volume) VALUES (%s, %s, %s)", to_insert)
        print(f"{file_key.upper()} 데이터 적재 완료: {len(to_insert)}건")

    process_time_data('traffic', 'car_traffic_by_time', 'local_code_traffic')
    process_time_data('accident', 'car_accident_by_time', 'local_code_accident')
    process_time_data('casualties', 'car_casualties_by_time', 'local_code_casualties')

    conn.commit()
    print("\n모든 데이터가 정상적으로 DB에 업데이트되었습니다!")

except Exception as e:
    print(f"오류 발생: {e}")
    if conn: conn.rollback()
finally:
    if conn and conn.is_connected():
        cursor.close()
        conn.close()