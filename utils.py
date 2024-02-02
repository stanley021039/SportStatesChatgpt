import json
import requests
import urllib.request
from urllib.error import URLError, HTTPError
import sqlite3
import jwt
import datetime
import logging
import os
from datetime import datetime, timezone, timedelta
import pytz


def html_request2db_NBA_standings(db_path, json_path, season='2024'):
    season_start = datetime(year=int(season), month=6, day=1)
    season_end = datetime(year=int(season)+1, month=6, day=1)
    table_name = f'season_{season}'
    if is_table_exist(db_path, table_name):
        refresh_frequency = timedelta(days=1)
        if not is_table_refresh(db_path, table_name, season_start, season_end, refresh_frequency):
            return
    
    print(f"request Standings of season {season} from https://api-nba-v1.p.rapidapi.com/standings")
    url = "https://api-nba-v1.p.rapidapi.com/standings"
    querystring = {"league":"standard","season":f'{str(season)}'}
    headers = {
        "X-RapidAPI-Key": "69279f7c5bmsh53855af68a98650p1f66cajsn08d10824f731",
        "X-RapidAPI-Host": "api-nba-v1.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()
    with open(json_path, 'w') as json_file:
        json.dump(data, json_file)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Create table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS {} (
            team_name TEXT PRIMARY KEY,
            logo_url TEXT,
            wins INTEGER,
            win_percentage REAL,
            losses INTEGER,
            loss_percentage REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )'''.format(table_name)
    )

    # Insert data into the table
    for team_data in data['response']:
        team_name = team_data['team']['name']
        logo_url = team_data['team']['logo']
        wins = team_data['win']['total']
        win_percentage = float(team_data['win']['percentage'])
        losses = team_data['loss']['total']
        loss_percentage = float(team_data['loss']['percentage'])

        cursor.execute(
            f'INSERT OR REPLACE INTO {table_name} (team_name, logo_url, wins, win_percentage, losses, loss_percentage) VALUES (?, ?, ?, ?, ?, ?)',
            (team_name, logo_url, wins, win_percentage, losses, loss_percentage)
        )

    conn.commit()
    conn.close()
    return

def html_request2db_NBA_today_scoreboard(db_path, json_path, date:str):
    table_name = f"NBA_{date.replace('-', '_')}"
    if is_table_exist(db_path, table_name):
        year, month, day = date.split('-')
        start = datetime(year=int(year), month=int(month), day=int(day))
        end = datetime(year=int(year), month=int(month), day=int(day)+1)
        refresh_frequency = timedelta(hours=1)
        if not is_table_refresh(db_path, table_name, start, end, refresh_frequency):
            return
    print(f"request score board of {date} from https://api-nba-v1.p.rapidapi.com/games")
    url = "https://api-nba-v1.p.rapidapi.com/games"
    querystring = {"date":f"{date}"}
    headers = {
        "X-RapidAPI-Key": "69279f7c5bmsh53855af68a98650p1f66cajsn08d10824f731",
        "X-RapidAPI-Host": "api-nba-v1.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()
    # write json
    simplified_data = []
    for game in data["response"]:
        simplified_game = {
            "date": game["date"],
            "home_team": game["teams"]["home"]["name"],
            "away_team": game["teams"]["visitors"]["name"],
            "home_score": game["scores"]["home"]["points"],
            "away_score": game["scores"]["visitors"]["points"],
            "status": game["status"]["long"]
        }
        simplified_data.append(simplified_game)
    with open(json_path, "w") as f:
        json.dump(simplified_data, f, indent=4)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
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
            awayTeamScore INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )'''.format(table_name)
    )

    for game in data['response']:
        gameId = str(game['id'])
        gameCode = game.get('code', '')
        gameStatus = game.get('status', {}).get('short', 0)
        gameStatusText = game.get('status', {}).get('long', '')
        gameTimeUTC = game.get('date', {}).get('start', '')
        homeTeamName = game.get('teams', {}).get('home', {}).get('name', '')
        homeTeamScore = game.get('scores', {}).get('home', {}).get('points', 0)
        awayTeamName = game.get('teams', {}).get('visitors', {}).get('name', '')
        awayTeamScore = game.get('scores', {}).get('visitors', {}).get('points', 0)

        cursor.execute(
            f'INSERT OR REPLACE INTO {table_name} (gameId, gameCode, gameStatus, gameStatusText, gameTimeUTC, homeTeamName, homeTeamScore, awayTeamName, awayTeamScore) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (gameId, gameCode, gameStatus, gameStatusText, gameTimeUTC, homeTeamName, homeTeamScore, awayTeamName, awayTeamScore)
        )
    conn.commit()
    conn.close()
    return

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

def get_date(format="%Y-%m-%d"):
    eastern = pytz.timezone('US/Eastern')
    now_utc = datetime.now(timezone.utc)
    now_eastern = now_utc.astimezone(eastern)
    formatted_date = now_eastern.strftime(format)
    return formatted_date

def is_table_exist(db_path, table_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    result = cursor.fetchone()
    conn.close()
    return result is not None

def is_table_refresh(db_path, table_name, start, end, refresh_frequency=timedelta(hours=1)):
    current_time = datetime.now()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM {table_name} LIMIT 1')
    row = cursor.fetchone()
    column_names = [description[0] for description in cursor.description]
    if row:
        timestamp_value = row[column_names.index('timestamp')]
        timestamp_datetime = datetime.strptime(timestamp_value, "%Y-%m-%d %H:%M:%S")
        print('start', start, 'end', end, 'timestamp_value', timestamp_value, 'current_time', current_time, 'refresh_frequency', refresh_frequency)
        if not (current_time > start and timestamp_datetime < end and current_time - timestamp_datetime > refresh_frequency):
            return False
    return True

