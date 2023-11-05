import sqlite3

# 連接到 SQLite 數據庫文件（如果不存在，將創建它）
conn = sqlite3.connect('score.db')

# 創建一個數據表以存儲比分信息
conn.execute('''CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_a_score INTEGER,
    team_b_score INTEGER
)''')

# 插入一條初始比分記錄（可選）
conn.execute('''INSERT INTO scores (team_a_score, team_b_score) VALUES (0, 0)''')

# 提交更改並關閉連接
conn.commit()
conn.close()
