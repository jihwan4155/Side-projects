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

    