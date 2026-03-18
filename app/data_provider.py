import pandas as pd
import mysql.connector

class DataProvider:
    def __init__(self):
        self.config = {
            'host': '127.0.0.1',
            'user': 'practice',
            'password': 'practice',
            'database': '1st_project_db'
        }

    def get_query_data(self, query):
        conn = mysql.connector.connect(**self.config)
        df = pd.read_sql(query, conn)
        conn.close()
        return df

    def get_main_summary(self):
        query = """
        SELECT 
            (SELECT SUM(population_count) FROM populations) as total_pop,
            (SELECT SUM(car_count) FROM car_reg) as total_cars,
            (SELECT SUM(volume) FROM car_accident_by_time) as total_accidents,
            (SELECT SUM(volume) FROM car_casualties_by_time) as total_casualties
        """
        return self.get_query_data(query)

    def get_accident_map_data(self):
        query = """
        SELECT l.local_name as gu, a.time_slot, a.volume as accidents
        FROM car_accident_by_time a
        JOIN locals l ON a.local_code_accident = l.local_codes
        """
        return self.get_query_data(query)

    def get_accident_stats(self):
        query = "SELECT MIN(volume) as min_val, MAX(volume) as max_val FROM car_accident_by_time"
        res = self.get_query_data(query)
        min_val = float(res['min_val'][0]) if res['min_val'][0] is not None else 0
        max_val = float(res['max_val'][0]) if res['max_val'][0] is not None else 100
        return min_val, max_val

    def get_traffic_matrix_data(self):
        query = """
        SELECT l.local_name as gu, t.time_slot, t.volume as traffic
        FROM car_traffic_by_time t
        JOIN locals l ON t.local_code_traffic = l.local_codes
        """
        return self.get_query_data(query)

    def get_scaled_traffic_data(self):
        df = self.get_traffic_matrix_data()
        if df.empty: return pd.DataFrame(), pd.DataFrame()
        matrix = df.pivot(index='gu', columns='time_slot', values='traffic')
        scaled_matrix = matrix.apply(lambda x: (x - x.min()) / (x.max() - x.min() + 1e-9), axis=1)
        return matrix, scaled_matrix

    def get_danger_index(self):
        query = """
        SELECT l.local_name as gu, p.population_count, c.car_count, 
               SUM(a.volume) as total_accidents
        FROM locals l
        JOIN populations p ON l.local_codes = p.local_code_pop
        JOIN car_reg c ON l.local_codes = c.local_code_reg
        JOIN car_accident_by_time a ON l.local_codes = a.local_code_accident
        GROUP BY l.local_name, p.population_count, c.car_count
        """
        return self.get_query_data(query)
    

    def get_integrated_indices(self):
        query = """
        SELECT 
            l.local_name as gu,
            -- 안전 지수
            ((SUM(a.volume) * 0.4 + SUM(cas.volume) * 0.6) / c.car_count) * 10 as safety_index,
            -- 혼잡 지수 
            (cong.congestion_frequency + cong.congestion_time) / 2 as congestion_index
        FROM locals l
        JOIN car_reg c ON l.local_codes = c.local_code_reg
        JOIN car_accident_by_time a ON l.local_codes = a.local_code_accident
        JOIN car_casualties_by_time cas ON l.local_codes = cas.local_code_casualties
        JOIN congestion cong ON l.local_codes = cong.local_code_congestion 
        GROUP BY l.local_name, c.car_count, cong.congestion_frequency, cong.congestion_time
        """
        return self.get_query_data(query)
    
    def get_total_traffic_metrics(self):
        """자치구별 전체 시간대 교통량 합계 및 그 합계들의 평균 추출"""
        # 1. 자치구별 총 교통량 (Bar Chart용: 모든 시간대 합산)
        gu_query = """
        SELECT l.local_name as gu, SUM(t.volume) as total_traffic
        FROM car_traffic_by_time t
        JOIN locals l ON t.local_code_traffic = l.local_codes
        GROUP BY l.local_name
        """
        gu_df = self.get_query_data(gu_query)
        
        # 2. 자치구별 총 교통량들의 평균 (Metric 표시용)
        if not gu_df.empty:
            avg_total_traffic = gu_df['total_traffic'].mean()
        else:
            avg_total_traffic = 0
            
        return avg_total_traffic, gu_df
    
    def get_driving_score(self, gu_name, time_slot):
        """특정 구와 시간대의 데이터를 분석하여 운전 점수 산출"""
        
        # 1. '06~08' 형식을 '6시~8시' 형식으로 변환 (앞의 0 제거 및 '시' 추가)
        start_t, end_t = time_slot.split('~')
        db_time_slot = f"{int(start_t)}시~{int(end_t)}시"

        # 2. 서브쿼리를 이용해 각각의 테이블에서 데이터를 안전하게 가져옴
        query = f"""
        SELECT 
            l.local_name as gu,
            -- 사고 건수
            (SELECT IFNULL(SUM(volume), 0) 
             FROM car_accident_by_time 
             WHERE local_code_accident = l.local_codes 
               AND time_slot = '{db_time_slot}') as accidents,
            -- 통행량
            (SELECT IFNULL(SUM(volume), 0) 
             FROM car_traffic_by_time 
             WHERE local_code_traffic = l.local_codes 
               AND time_slot = '{db_time_slot}') as traffic,
            -- 혼잡도
            IFNULL(cong.congestion_frequency, 0) as congestion_frequency,
            IFNULL(cong.congestion_time, 0) as congestion_time
        FROM locals l
        LEFT JOIN congestion cong ON l.local_codes = cong.local_code_congestion
        WHERE l.local_name = '{gu_name}'
        LIMIT 1
        """
        return self.get_query_data(query)
    
    def get_congestion_map_data(self):
        """
        DB 데이터를 JOIN 하여 실시간 교통 포화도(비율)를 계산합니다.
        (교통량 / 등록차량수) * 100 산식을 사용합니다.
        """
        query = """
        SELECT 
            l.local_name AS gu,
            t.time_slot,
            -- (교통량 / 등록대수) * 100을 통해 포화도(congestion_rate) 산출
            (CAST(t.volume AS FLOAT) / r.car_count) * 100 AS congestion_rate
        FROM car_traffic_by_time t
        JOIN car_reg r ON t.local_code_traffic = r.local_code_reg
        JOIN locals l ON t.local_code_traffic = l.local_codes
        """
        return self.get_query_data(query)