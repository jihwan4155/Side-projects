from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import main
from main import fetch_and_save_news


app = Flask(__name__)

# DB 연결 함수
def get_db_connections():
    conn = sqlite3.connect('news_dashboard.db',)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    selected_keyword = request.args.get('keyword')
    # 서버 작동 확인용 데이터
    conn = get_db_connections()
    
    query_keywords = """
        SELECT k.name, COUNT(n.id) as news_count 
        FROM keywords k 
        LEFT JOIN news n ON n.title LIKE '%' || k.name || '%'
        GROUP BY k.name
    """
    
    keywords = conn.execute(query_keywords).fetchall()
    
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

@app.route('/add_keyword', methods=['POST'])
def add_keyword():
    new_kw = request.form.get('keyword_name')
    if new_kw:
        conn = get_db_connections()
        conn.execute("INSERT OR IGNORE INTO keywords (name) VALUES (?)", (new_kw,))
        conn.commit()
        conn.close()
    return redirect(url_for('index'))

@app.route('/delete_keyword/<string:name>')
def delete_keyword(name):
    conn = get_db_connections()
    conn.execute("DELETE FROM keywords WHERE name = ?", (name,))
    
    conn.execute("DELETE FROM news WHERE title LIKE ?", ('%' + name + '%',))
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))


@app.route('/collect')
def collect():
    conn = get_db_connections()
    keywords = conn.execute('SELECT name FROM keywords').fetchall()
    conn.close()

    print("웹에서 뉴스 수집을 시작합니다...")
    for kw in keywords:
        fetch_and_save_news(kw['name'])
    
    return redirect(url_for('index'))


@app.route('/read_news/<int:news_id>')
def read_news(news_id):
    conn = get_db_connections()
    news = conn.execute("SELECT link FROM news WHERE id = ?", (news_id,)).fetchone()

    if news:
        conn.execute("UPDATE news SET is_read = 1 WHERE id = ?", (news_id,))
        conn.commit()
        conn.close()
        return redirect(news['link'])

    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # 서버 실행
    app.run(host='0.0.0.0', port=5000, debug=True)
