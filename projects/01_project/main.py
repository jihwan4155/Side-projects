import os
from dotenv import load_dotenv
import requests

# 환경 변수로 env 파일의 API키 가져오기
load_dotenv()
client_id = os.getenv("NAVER_CLIENT_ID")
client_secret = os.getenv("NAVER_CLIENT_SECRET") 

# 뉴스 검색 API 주소 
url = "https://openapi.naver.com/v1/search/news.json"

# 헤더 설정 
headers = {
    "X-Naver-Client-Id": client_id,    
    "X-Naver-Client-Secret": client_secret 
}

# 파라미터 설정
params = {
    "query": "HBF", # 원하는 키워드
    "display": 5 # 가져올 뉴스 개수
}

# 요청 (헤더와 파라미터 같이)
response = requests.get(url, headers=headers, params=params)

# json 요청하고 딕셔너리로 파씽
data = response.json()

news_list = data.get('items', []) # items라는 키 안에 뉴스 리스트만
for news in news_list:
    raw_title = news['title']
    clean_title = raw_title.replace("<b>", "").replace("</b>", "").replace("&quot:,", "'")
    # title의 b태그 제거, 특수문자 지우기
    link = news['link']

import sqlite3 # SQLite 데이터베이스 모듈

# 1. 현재 실행 중인 이 파일(main.py)의 절대 경로를 찾습니다.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 2. 그 경로 뒤에 DB 이름을 붙여줍니다. (폴더 경로 + 파일 이름)
db_path = os.path.join(BASE_DIR, 'news_dashboard.db')

conn = sqlite3.connect(db_path) # DB 연결

cursor = conn.cursor() # 커서 생성

# 테이블 생성
cursor.execute('''
CREATE TABLE IF NOT EXISTS news(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,       -- 뉴스 제목
    link TEXT UNIQUE NOT NULL, -- 뉴스 링크 (UNIQUE로 중복 링크 방지)
    pub_date TEXT,              -- 뉴스 날짜
    is_read INTEGER DEFAULT 0  -- 0은 '안 읽음', 1은 '읽음'
)
''')

news_title = "'메모리가 GPU를 삼킨다'… HBM의 아버지 김정호 교수의 경고"
news_link = "https://www.ajunews.com/view/20260330165729378"
news_date = "2026-03-30"

sql = "INSERT INTO news (title, link, pub_date, is_read) VALUES (?, ?, ?, ?)"
cursor.execute(sql, (news_title, news_link, news_date, 0))

conn.commit() # 변경 사항 저장 (안하면 DB 파일에 반영 X)

print("뉴스 저장 완료")
