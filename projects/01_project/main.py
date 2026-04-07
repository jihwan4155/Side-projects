import os
from dotenv import load_dotenv
import requests
import sqlite3 # SQLite 데이터베이스 모듈
import webbrowser

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


def get_unread_news():
    """DB에서 읽지 않은 뉴스 목록을 가져와 출력하는 함수"""
    cursor.execute("SELECT id, title, link FROM news WHERE is_read = 0")
    unread_list = cursor.fetchall()

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
    cursor.execute("UPDATE news SET is_read = 1 WHERE id = ?", (news_id,))
    conn.commit()
    print(f"\n✔ {news_id}번 뉴스를 읽음 처리했습니다.")


def read_news(news_id):
    """뉴스를 브라우저로 열고, DB 상태를 읽음으로 변경"""
    # 해당 ID의 링크 가져오기
    cursor.execute("SELECT link FROM news WHERE id = ?", (news_id,))
    result = cursor.fetchone()
    
    if result:
        url = result[0]
        # 브라우저로 열기
        print(f"\n🌐 브라우저에서 뉴스를 엽니다: {url}")
        webbrowser.open(url)
        
        # 읽음 처리 
        mark_as_read(news_id)
    else:
        print("⚠️ 해당 번호의 뉴스를 찾을 수 없습니다.")


def search_news(keyword):
    """제목에 키워드가 포함된 뉴스 검색"""
    query_keyword = f"%{keyword}%"
    cursor.execute("SELECT id, title, is_read FROM news WHERE title LIKE ?", (query_keyword,))
    results = cursor.fetchall() # 리스트 형태로 가져옴

    if not results:
        print(f"\n🔎 '{keyword}'(이)가 포함된 뉴스가 없습니다.")
    else:
        print(f"\n🔎 '{keyword}' 검색 결과 ({len(results)}건):")
        for row in results:
            status = "✅" if row[2] == 1 else "🆕"
            print(f"[{row[0]}] {status} {row[1]}")


while True:
    # 무한 루프 메뉴 구성
    print("\n" + "="*30)
    print(" 📰 지환의 뉴스 대시보드 ")
    print("="*30)
    print("1. 🔄 새로운 뉴스 수집")
    print("2. 📋 읽지 않은 뉴스 보기")
    print("3. ✅ 뉴스 간단 읽음 처리 (ID 입력)")
    print("4. 🔎 뉴스 검색하기")
    print("5. 🌐 뉴스 읽기 (브라우저 열기)")
    print("6. ❌ 프로그램 종료")
    print("="*30)

    choice = input("원하는 작업 번호를 입력하세요:  ")
    
    if choice == "1":
        # 1. DB에서 키워드 목록 가져오기
        cursor.execute("SELECT name FROM keywords")
        keywords = [row[0] for row in cursor.fetchall()]
        print(f"\n{len(keywords)}개의 키워드로 뉴스를 수집합니다...")
        for kw in keywords:
            fetch_and_save_news(kw)
    
    elif choice == "2":
        # 2. 안 읽은 뉴스 출력 함수
        get_unread_news()
    
    elif choice == "3":
        # 3. 사용자에게 ID를 입력받아 읽음 처리
        target_id = input("읽음 처리할 뉴스 번호(ID)를 입력하세요:  ")
        # 입력받은 ID가 숫자인지 확인
        if target_id.isdigit():
            mark_as_read(int(target_id))
        else:
            print("⚠️ 숫자 번호를 입력해 주세요.")
    
    elif choice == "4":
        word = input("검색할 키워드를 입력하세요: ")
        search_news(word)

    elif choice == "5":
        news_id = input("읽을 뉴스 번호를 입력하세요: ")
        read_news(news_id)
    
    elif choice == "6":
        print("\n오늘의 뉴스 읽기 습관, 성공적! 종료합니다. 👋")
        break

    else:
        print("\n⚠️ 잘못된 번호입니다. 1~6 사이의 숫자를 입력해 주세요.")

# 루프 끝나면 안전하게 DB 연결 종료
conn.close()