import sqlite3
from bs4 import BeautifulSoup
from lxml import html

# 指定HTML文件路径
html_file_path = 'web_html_NBA/NBA_team_scores.html'

# 尝试打开HTML文件并读取内容
try:
    with open(html_file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
except FileNotFoundError:
    print(f"文件 '{html_file_path}' 未找到")
except Exception as e:
    print(f"发生错误: {str(e)}")

# 使用Beautiful Soup解析HTML
soup = BeautifulSoup(html_content, 'html.parser')

# 创建SQLite数据库连接
conn = sqlite3.connect('score.db')

# 创建游标
cursor = conn.cursor()

# 创建表格
cursor.execute('''
    CREATE TABLE IF NOT EXISTS basketball_stats (
        team_name TEXT,
        wins INTEGER,
        losses INTEGER,
        win_pct REAL,
        gb TEXT,
        conference_record TEXT,
        division_record TEXT,
        home_record TEXT,
        road_record TEXT,
        ot_record TEXT,
        last_10 TEXT,
        streak TEXT
    )
''')

# 提取HTML表格数据并插入到SQLite表格
tree = html.fromstring(html_content)
tbody = tree.xpath('//*[@id="__next"]/div[2]/div[2]/div[2]/section[2]/div/div[2]/div[2]/table/tbody')[0]

#table = soup.find('table', class_='//*[@id="__next"]/div[2]/div[2]/div[2]/section[2]/div/div[2]/div[2]/table/tbody')
#tbody = table.find('tbody', class_='Crom_body__UYOcU')
for row in tbody.find_all('tr', class_='StatsStandingsTable_row__o6A7G'):
    data = [cell.get_text(strip=True) for cell in row.find_all('td')]
    cursor.execute('''
        INSERT INTO basketball_stats
        (team_name, wins, losses, win_pct, gb, conference_record, division_record, home_record, road_record, ot_record, last_10, streak)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', data)

# 提交更改并关闭数据库连接
conn.commit()
conn.close()

print("数据已插入到SQLite数据库中")