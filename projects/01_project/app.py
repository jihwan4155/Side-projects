from flask import Flask, render_template
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
    # 서버 작동 확인용 데이터
    conn = get_db_connections()
    news_data = conn.execute('SELECT * FROM news ORDER BY id DESC LIMIT 5').fetchall()
    conn.close()

    return render_template('index.html', news_list=news_data)

if __name__ == '__main__':
    # 서버 실행
    app.run(host='0.0.0.0', port=5000, debug=True)
