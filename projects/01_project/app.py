from flask import Flask, render_template, request
import sqlite3
import main

app = Flask(__name__)

# DB 연결 함수
def get_db_connections():
    conn = sqlite3.connect('news_dashboard.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    selected_keyword = request.args.get('keyword')
    # 서버 작동 확인용 데이터
    conn = get_db_connections()
    keywords = conn.execute('SELECT name FROM keywords').fetchall()
    
    if selected_keyword:
        query = "SELECT * FROM news WHERE title LIKE ? ORDER BY id DESC"
        news_data = conn.execute(query, ('%' + selected_keyword + '%',)).fetchall()
    else:
        news_data = conn.execute('SELECT * FROM news ORDER BY id DESC LIMIT 10').fetchall()
    
    conn.close()

    return render_template('index.html', 
                           news_list=news_data, 
                           keyword_list=keywords, 
                           active_keyword=selected_keyword)

if __name__ == '__main__':
    # 서버 실행
    app.run(host='0.0.0.0', port=5000, debug=True)
