import json
import urllib
import sqlite3
import jwt
import datetime
import logging
import os
from datetime import datetime, timezone, timedelta
import pytz

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(level=logging.DEBUG, filename=os.path.join(BASE_DIR, "get_score.log"), filemode='w')
def html_request(url, headers):
    req = urllib.request.Request(url=url, headers=headers)
    text = urllib.request.urlopen(req).read().decode('gbk')
    return(text)

def html_request2db_NBA_standings(db_path):
    url = 'https://stats.nba.com/stats/leaguestandingsv3?GroupBy=conf&LeagueID=00&Season=2023-24&SeasonType=Regular%20Season&Section=overall'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.nba.com/'
    }
    data_json = html_request(url=url, headers=headers)
    data = json.loads(data_json)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    headers = data['resultSets'][0]['headers']
    # header_types = ['INTEGER'] + ['TEXT' for _ in headers]  # 假设所有列的数据类型都是文本
    # header_info = ', '.join([f'{headers[i]} {header_types[i]}' for i in range(len(headers))])
    cursor.execute(f'CREATE TABLE IF NOT EXISTS Standings (LeagueID TEXT, SeasonID TEXT, TeamID TEXT PRIMARY KEY, {", ".join(headers[3:])})')

    for row in data['resultSets'][0]['rowSet']:
        placeholders = ', '.join(['?'] * len(row))
        cursor.execute(f'INSERT OR REPLACE INTO Standings (LeagueID, SeasonID, TeamID, {", ".join(headers[3:])}) VALUES ({placeholders})', row)
    conn.commit()
    conn.close()
    return

def html_request2db_NBA_today_scoreboard(db_path):
    url = 'https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.nba.com/'
    }
    data_json = html_request(url=url, headers=headers)
    data = json.loads(data_json)
    table_name = 'NBA_' + data['scoreboard']['gameDate'].replace("-", "_")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    logging.error(type(table_name))
    logging.error(table_name)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS {} (
        gameId TEXT PRIMARY KEY,
        gameCode TEXT,
        gameStatus INTEGER,
        gameStatusText TEXT,
        gameTimeUTC TEXT,
        homeTeamName TEXT,
        homeTeamScore INTEGER,
        awayTeamName TEXT,
        awayTeamScore INTEGER
        )'''.format(table_name)
    )
    for game in data['scoreboard']['games']:
        gameId = game['gameId']
        gameCode = game['gameCode']
        gameStatus = game['gameStatus']
        gameStatusText = game['gameStatusText']
        gameTimeUTC = game['gameTimeUTC']
        homeTeamName = game['homeTeam']['teamName']
        homeTeamScore = game['homeTeam']['score']
        awayTeamName = game['awayTeam']['teamName']
        awayTeamScore = game['awayTeam']['score']
        cursor.execute(
            f'INSERT OR REPLACE INTO {table_name} (gameId, gameCode, gameStatus, gameStatusText, gameTimeUTC, homeTeamName, homeTeamScore, awayTeamName, awayTeamScore) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (gameId, gameCode, gameStatus, gameStatusText, gameTimeUTC, homeTeamName, homeTeamScore, awayTeamName, awayTeamScore)
        )
    conn.commit()
    conn.close()
    return table_name

def generate_token(username, secret_key, hours=1):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=hours)
    payload = {
        'username': username,
        'exp': expiration
    }
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token

# 验证令牌的函数
def verify_token(token, secret_key):
    try:
        # 使用密钥验证并解码令牌
        data = jwt.decode(token, secret_key, algorithms=['HS256'])
        return data
    except jwt.ExpiredSignatureError:
        # 令牌过期
        return None
    except jwt.InvalidTokenError:
        # 令牌无效
        return None

def chech_login(token, secret_key):
    if token and token.startswith('Bearer '):
        token = token.split(' ')[1]
        # 在真实应用中，可能需要使用 JWT 或其他方法解码令牌以获取用户名
        data = verify_token(token, secret_key)
        if data is not None:
            username_decode = data['username']
            exp = data['exp']
            return username_decode, exp
        else:
            return None, None

def get_time(format="%Y-%m-%d"):
    eastern = pytz.timezone('US/Eastern')
    now_utc = datetime.now(timezone.utc)
    now_eastern = now_utc.astimezone(eastern)
    formatted_date = now_eastern.strftime(format)
    return formatted_date

print(get_time("%Y-%m-%d %H:%M:%S %Z"))