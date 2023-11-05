import json
import urllib
import sqlite3
import jwt
import datetime

def get_standings_from_web_NBA():
    url = 'https://stats.nba.com/stats/leaguestandingsv3?GroupBy=conf&LeagueID=00&Season=2023-24&SeasonType=Regular%20Season&Section=overall'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.nba.com/'
    }


    req = urllib.request.Request(url=url, headers=headers)
    text = urllib.request.urlopen(req).read().decode('gbk')
    return(text)

def write_json_to_db_NBA(json_file, db_save_path):
    # 解析 JSON 数据
    data = json.loads(json_file)

    # 连接到 SQLite 数据库
    conn = sqlite3.connect(db_save_path)
    cursor = conn.cursor()

    # 创建表格
    table_name = 'Standings'
    headers = data['resultSets'][0]['headers']
    header_types = ['INTEGER'] + ['TEXT' for _ in headers]  # 假设所有列的数据类型都是文本
    header_info = ', '.join([f'{headers[i]} {header_types[i]}' for i in range(len(headers))])
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    # 如果表不存在，创建表
    if not cursor.fetchone():
        cursor.execute(f'CREATE TABLE {table_name} (LeagueID TEXT, SeasonID TEXT, TeamID TEXT PRIMARY KEY, {", ".join(headers[3:])})')

    # 插入数据
    for id, row in enumerate(data['resultSets'][0]['rowSet'], 1):
        placeholders = ', '.join(['?'] * len(row))
        cursor.execute(f'INSERT OR REPLACE INTO {table_name} (LeagueID, SeasonID, TeamID, {", ".join(headers[3:])}) VALUES ({placeholders})', row)



    # 提交更改并关闭数据库连接
    conn.commit()
    conn.close()
    return

def generate_token(username, secret_key):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    payload = {
        'username': username,
        'exp': expiration
    }
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token