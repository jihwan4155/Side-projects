import os
from dotenv import load_dotenv
import requests
import sqlite3 # SQLite 데이터베이스 모듈

# 환경 변수로 env 파일의 API키 가져오기
load_dotenv()
client_id = os.getenv("NAVER_CLIENT_ID")
client_secret = os.getenv("NAVER_CLIENT_SECRET") 

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

conn.commit() # 변경 사항 저장 (안하면 DB 파일에 반영 X)


def fetch_and_save_news(keyword):
    """네이버 API에서 뉴스를 가져와 DB에 저장 함수"""

    # 뉴스 검색 API 주소 
    url = "https://openapi.naver.com/v1/search/news.json"

    # 헤더 설정 
    headers = {
        "X-Naver-Client-Id": os.getenv("NAVER_CLIENT_ID"),    
        "X-Naver-Client-Secret": os.getenv("NAVER_CLIENT_SECRET")

    }

    # 파라미터 설정
    params = {
        "query": keyword, # 원하는 키워드
        "display": 5 # 가져올 뉴스 개수
    }

    # 요청 (헤더와 파라미터 같이)
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200: # 정상 연결시
        items = response.json().get('items', [])
        # json 요청하고 딕셔너리로 파씽

        for item in items:
            # 데이터 가공
            clean_title = item['title'].replace("<b>", "").replace("</b>", "").replace("&quot;", "'")
            # title의 b태그 제거, 특수문자 지우기
            link = item['link']
            pub_date = item['pubDate']

            # DB 저장 (Ignore INTO => 중복 무시)
            sql = "INSERT or IGNORE INTO news (title, link, pub_date) VALUES (?, ?, ?)"
            cursor.execute(sql, (clean_title, link, pub_date))

        conn.commit()
        print(f"'{keyword}'관련 뉴스 수집 및 저장 완료!")
    else:
        print(f"에러 발생: {response.status_code}")

# 키워드를 저장할 표 생성
cursor.execute("CREATE TABLE IF NOT EXISTS keywords (id INTEGER PRIMARY KEY, name TEXT UNIQUE)")
# 검색하고 싶은 키워드를 미리 넣기
cursor.execute("INSERT OR IGNORE INTO keywords (name) VALUES ('HBF'), ('오타니'), ('삼성전자')")
conn.commit()

# DB에서 키워드를 가져오기
cursor.execute("SELECT name FROM keywords")
keywords = [row[0] for row in cursor.fetchall()]

for keyword in keywords:
    fetch_and_save_news(keyword)

# 작업이 다 끝나면 닫기
conn.close()