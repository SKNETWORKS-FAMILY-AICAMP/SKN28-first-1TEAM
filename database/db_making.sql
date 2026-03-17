-- Active: 1773042173092@@127.0.0.1@3306@1st_project_db
CREATE DATABASE 1st_project_db;
GRANT ALL PRIVILEGES ON 1st_project_db.* TO 'practice'@'%'; -- 자기 db 아이디로 변경

-- 테이블 삭제
DROP TABLE IF EXISTS locals;
DROP TABLE IF EXISTS car_reg;
DROP TABLE IF EXISTS populations;
DROP TABLE IF EXISTS car_traffic_by_time;
DROP TABLE IF EXISTS car_accident_by_time;
DROP TABLE IF EXISTS car_casualties_by_time;
DROP Table IF EXISTS congestion;

-- 테이블 생성
-- 지역 코드
CREATE TABLE IF NOT EXISTS locals(
	local_codes INT AUTO_INCREMENT PRIMARY KEY COMMENT '지역 코드',
	local_name VARCHAR(255)	NOT NULL COMMENT '지역 이름'
);

INSERT INTO locals
VALUES 
(NULL, '종로구'), (NULL, '중구'), (NULL, '용산구'), (NULL, '성동구'), (NULL, '광진구'),
(NULL, '동대문구'), (NULL, '중랑구'), (NULL, '성북구'), (NULL, '강북구'), (NULL, '도봉구'),
(NULL, '노원구'), (NULL, '은평구'), (NULL, '서대문구'), (NULL, '마포구'), (NULL, '양천구'),
(NULL, '강서구'), (NULL, '구로구'), (NULL, '금천구'), (NULL, '영등포구'), (NULL, '동작구'),
(NULL, '관악구'), (NULL, '서초구'), (NULL, '강남구'), (NULL, '송파구'), (NULL, '강동구');

-- 차량 등록
CREATE TABLE car_reg (
	local_code_reg INT NOT NULL COMMENT '지역 코드',
	car_count INT DEFAULT 0 COMMENT '차량 수',
    FOREIGN KEY (local_code_reg) REFERENCES locals (local_codes)
);

-- 인구 수
CREATE TABLE populations (
	local_code_pop INT NOT NULL COMMENT '지역 코드',
	population_count INT DEFAULT 0 COMMENT '인구 수',
    FOREIGN KEY (local_code_pop) REFERENCES locals (local_codes)
);

-- 시간별 교통량
CREATE TABLE car_traffic_by_time (
    local_code_traffic INT,  -- locals 테이블의 local_codes를 참조하도록 변경
    time_slot VARCHAR(50), 
    volume INT, 
    FOREIGN KEY (local_code_traffic) REFERENCES locals (local_codes)
);

-- 시간별 사고 수
CREATE TABLE car_accident_by_time (
    local_code_accident INT,  -- locals 테이블의 local_codes를 참조하도록 변경
    time_slot VARCHAR(50), 
    volume INT, 
    FOREIGN KEY (local_code_accident) REFERENCES locals (local_codes)
);

-- 시간별 사상자 수
CREATE TABLE car_casualties_by_time (
    local_code_casualties INT,  -- locals 테이블의 local_codes를 참조하도록 변경
    time_slot VARCHAR(50), 
    volume INT, 
    FOREIGN KEY (local_code_casualties) REFERENCES locals (local_codes)
);

CREATE TABLE congestion (
    local_code_congestion INT,  -- locals 테이블의 local_codes를 참조하도록 변경
    congestion_frequency INT, 
    congestion_time INT, 
    FOREIGN KEY (local_code_congestion) REFERENCES locals (local_codes)
);