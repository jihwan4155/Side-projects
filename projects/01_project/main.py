import os
from dotenv import load_dotenv
import requests
import sqlite3 # SQLite 데이터베이스 모듈
import webbrowser
from datetime import datetime

# 환경 변수로 env 파일의 API키 가져오기
load_dotenv()
CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
# 1. 현재 실행 중인 이 파일(main.py)의 절대 경로를 찾습니다.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 2. 그 경로 뒤에 DB 이름을 붙여줍니다. (폴더 경로 + 파일 이름)
db_path = os.path.join(BASE_DIR, 'news_dashboard.db')



def get_db_connection():
    """매번 새로운 연결을 생성하여 'Closed Database' 에러 방지"""
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """데이터베이스 테이블 및 초기 키워드 설정"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS news(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        link TEXT UNIQUE NOT NULL,
        pub_date TEXT,
        is_read INTEGER DEFAULT 0
    )''')
    cursor.execute("CREATE TABLE IF NOT EXISTS keywords (id INTEGER PRIMARY KEY, name TEXT UNIQUE)")
    cursor.execute("INSERT OR IGNORE INTO keywords (name) VALUES ('HBF'), ('오타니'), ('삼성전자')")
    conn.commit()
    conn.close()

def fetch_and_save_news(keyword):
    """네이버 API에서 뉴스를 가져와 DB에 저장 함수"""

    # 뉴스 검색 API 주소 
    url = "https://openapi.naver.com/v1/search/news.json"

    # 헤더 설정 
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET
    }

    # 파라미터 설정
    params = {
        "query": keyword, # 원하는 키워드
        "display": 5 # 가져올 뉴스 개수
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            items = response.json().get('items', [])
            conn = get_db_connection()
            cursor = conn.cursor()

            for item in items:
                # b 태그 및 특수문자 제거
                clean_title = item['title'].replace("<b>", "").replace("</b>", "").replace("&quot;", "'")
                cursor.execute(
                    "INSERT OR IGNORE INTO news (title, link, pub_date) VALUES (?, ?, ?)",
                    (clean_title, item['link'], item['pubDate'])
                )
            conn.commit()
            conn.close()
            print(f"'{keyword}' 관련 뉴스 수집 완료!")
        else:
            print(f"⚠️ API 요청 에러: {response.status_code}")
    except Exception as e:
        print(f"❌ 수집 중 오류 발생: {e}")
    


def get_unread_news():
    """DB에서 읽지 않은 뉴스 목록을 가져와 출력하는 함수"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, link FROM news WHERE is_read = 0 ORDER BY id DESC")
    unread_list = cursor.fetchall()
    conn.close()

    if not unread_list:
        print("\n✅ 모든 뉴스를 다 읽으셨습니다!")
        return
    
    print(f"\n--- [읽지 않은 뉴스 목록 ({len(unread_list)}개)] ---")
    for news in unread_list:
        print(f"[{news[0]}] {news[1]}")
        print(f"    링크: {news[2]}")
    print("-" * 40)

def mark_as_read(news_id):
    """특정 ID의 뉴스를 읽음 처리하는 함수"""
    conn = get_db_connection()
    conn.execute("UPDATE news SET is_read = 1 WHERE id = ?", (news_id,))
    conn.commit()
    conn.close()
    print(f"\n✔ {news_id}번 뉴스를 읽음 처리했습니다.")


def read_news(news_id):
    """뉴스를 브라우저로 열고, DB 상태를 읽음으로 변경"""
    # 해당 ID의 링크 가져오기
    conn = get_db_connection()
    result = conn.execute("SELECT link FROM news WHERE id = ?", (news_id,))
    conn.close()
    
    if result:
        webbrowser.open(result[0])
        mark_as_read(news_id)


def search_news(keyword):
    """제목에 키워드가 포함된 뉴스 검색"""
    conn = get_db_connection()
    query_keyword = f"%{keyword}%"
    results = conn.execute("SELECT id, title, is_read FROM news WHERE title LIKE ?", (query_keyword,))
    conn.close()

    if not results:
        print(f"\n🔎 '{keyword}'(이)가 포함된 뉴스가 없습니다.")
    else:
        print(f"\n🔎 '{keyword}' 검색 결과 ({len(results)}건):")
        for row in results:
            status = "✅" if row[2] == 1 else "🆕"
            print(f"[{row[0]}] {status} {row[1]}")

def format_date(raw_date):
    # API 날짜 형식: "Tue, 15 Apr 2026 22:39:00 +0900"
    try:
        clean_date = datetime.strptime(raw_date, '%a, %d %b %Y %H:%M:%S +0900')
        return clean_date.strftime('%Y-%m-%d %H:%M')
    except:
        return raw_date
    

if __name__ == "__main__":
    # 1. DB 초기화 (테이블 없으면 만들기)
    init_db()

    while True:
        conn = get_db_connection()
        total = conn.execute("SELECT COUNT(*) FROM news").fetchone()[0]
        read_count = conn.execute("SELECT COUNT(*) FROM news WHERE is_read = 1").fetchone()[0]
        conn.close()

        print(f"\n📊 [현황] 총 뉴스: {total} | 읽음: {read_count}")
        print("\n1.🔄수집 2.📋목록 3.✅읽음처리 4.🔎검색 5.🌐브라우저 6.❌종료")
        choice = input("번호 입력: ")
        
        if choice == "1":
            conn = get_db_connection()
            keywords = [row['name'] for row in conn.execute("SELECT name FROM keywords").fetchall()]
            conn.close()
            for kw in keywords:
                fetch_and_save_news(kw)
        elif choice == "2": get_unread_news()
        elif choice == "3": 
            tid = input("ID: ")
            if tid.isdigit(): mark_as_read(int(tid))
        elif choice == "4": search_news(input("키워드: "))
        elif choice == "5": read_news(input("ID: "))
        elif choice == "6": break