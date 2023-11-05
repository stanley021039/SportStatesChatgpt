import urllib.request
import json
import sqlite3
import os

url = 'https://stats.nba.com/stats/leaguestandingsv3?GroupBy=conf&LeagueID=00&Season=2023-24&SeasonType=Regular%20Season&Section=overall'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://www.nba.com/'
}


req = urllib.request.Request(url=url, headers=headers)
text =urllib.request.urlopen(req).read().decode('gbk')

# 解析 JSON 数据
data = json.loads(text)

# 创建表格
table_name = 'Standings'
headers = ['ID'] + data['resultSets'][0]['headers']
header_types = ['INTEGER'] + ['TEXT' for _ in headers]  # 假设所有列的数据类型都是文本
header_info = ', '.join([f'{headers[i]} {header_types[i]}' for i in range(len(headers))])

# 连接到 SQLite 数据库
db_path = 'standings.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
# 如果表不存在，创建表
if not cursor.fetchone():
    cursor.execute(f'CREATE TABLE {table_name} ({header_info})')

# 插入数据
for id, row in enumerate(data['resultSets'][0]['rowSet'], 1):
    placeholders = ', '.join(['?'] * len(row))
    cursor.execute(f'INSERT OR REPLACE INTO {table_name} VALUES (?, {placeholders})', (id, *row))

# 提交更改并关闭数据库连接
conn.commit()
conn.close()
