from flask import Flask, render_template, jsonify, request, make_response
from flask_restful import Api, Resource, reqparse
from flask_cors import cross_origin
import jwt
import sqlite3
import os
import logging
import openai
import json
from datetime import datetime, timezone, timedelta
import pytz
from utils import html_request2db_NBA_standings, html_request2db_NBA_today_scoreboard, generate_token, chech_login

app=Flask(__name__)
app.config['SECRET_KEY'] = 'w8eg4as21dg56f'
api = Api(app)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(level=logging.DEBUG, filename=os.path.join(BASE_DIR, "app.log"), filemode='w')

@app.route('/ID_verify', methods=['GET'])
def ID_verify():
    logging.error('ID_verify')
    token = request.headers.get('qwdadrization')
    logging.error(token)
    current_user, exp = chech_login(token, secret_key=app.config['SECRET_KEY'])
    return {'current_user': current_user}

class homeResource(Resource):
    def get(self):
        return make_response(render_template('index.html'))

api.add_resource(homeResource, "/")

db_path = os.path.join(BASE_DIR, "standings.db")
@app.route('/get_score', methods=['POST'])
def get_score():
    try:
        html_request2db_NBA_standings(db_path)
        # 連接到 SQLite 資料庫
        json_input = request.get_json()
        team_input = json_input['text']
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        logging.info('team_input:')
        logging.info(team_input)
        # 執行 SQL 查詢以獲取比分資訊
        cursor.execute('SELECT WINS, LOSSES FROM Standings WHERE TeamSlug = ?', (team_input,))
        row = cursor.fetchone()

        if row:
            wins, losses = row
            score_data = {'wins': wins, 'losses': losses}
            logging.info('no error')
            return jsonify(score_data)
        else:
            logging.info('error')
            return jsonify({'error': '未找到比分記錄'})

    except Exception as e:
        logging.info('Exception')
        return jsonify({'error': str(e)})
    finally:
        conn.close()

class chatGPTResource(Resource):
    def __init__(self):
        self.db_score_path = os.path.join(BASE_DIR, "databases/scoreboard.db")
        self.template_path = os.path.join(BASE_DIR, "gpt_sys_prompt/template.json")
        self.cache_path = os.path.join(BASE_DIR, "gpt_sys_prompt/cache.json")
        api_key = open(os.path.join(BASE_DIR, 'resource/ChatGPT_api_key.txt')).read()
        openai.api_key = api_key
        openai.organization = "org-J0PWE1RbQlGThBFfHT3iYmgO"
    def cread_template_prompt(self):
        current_time = self.get_time()
        # table_name = "NBA_" + current_time.replace("-", "_")
        table_name = 'NBA_2023_11_09'
        conn = sqlite3.connect(self.db_score_path)
        cursor = conn.cursor()
        headers = "gameStatus, gameStatusText, homeTeamName, homeTeamScore, awayTeamScore, awayTeamName"
        cursor.execute(f"SELECT {headers} FROM {table_name}")
        rows = cursor.fetchall()
        conn.close()
        template_message = [{"role": "system", "content": "You are a helpful assistant of a sports score Website."}]
        formatted_data = '\n'.join([', '.join(map(str, row))+'\n' for row in rows]) + "\n"
        formatted_data = f'\n表格名稱{table_name}\n' + headers + formatted_data
        database_message = {"role": "user", "content": formatted_data}
        template_message.append(database_message)
        with open(self.template_path, 'w') as file:
            json.dump(template_message, file)
    def load_prompts(self):
        if os.path.exists(self.cache_path) and os.path.getsize(self.cache_path) != 0:
            with open(self.cache_path, 'r') as file:
                self.messages = json.load(file)
        else:
            self.cread_template_prompt()
            with open(self.template_path, 'r') as file:
                self.messages = json.load(file)
    def get_time(self, format="%Y-%m-%d"):
        eastern = pytz.timezone('US/Eastern')
        now_utc = datetime.now(timezone.utc)
        now_eastern = now_utc.astimezone(eastern)
        formatted_date = now_eastern.strftime(format)
        return formatted_date
    def post(self):
        input_prompt = request.get_json()['text']
        self.load_prompts()
        current_time = self.get_time()
        prompt = "今天是" + current_time + "\n" + input_prompt + "\n用繁體中文回答"
        user_messages = {"role": "user", "content": prompt}
        self.messages.append(user_messages)

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.messages,
            temperature=0.7,
            max_tokens=100
        )
        text_response = response.choices[0].message.content
        self.messages.append({"role": "assistant", "content": text_response})

        with open(self.cache_path, "w") as file:
            json.dump(self.messages, file)
        return jsonify({"response": text_response})

api.add_resource(chatGPTResource, "/chat")

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/useraction')
def useraction_page():
    return render_template('useraction.html')

@app.route('/userinfo')
def userinfo_page():
    return render_template('userinfo.html')

class StandingsResource(Resource):
    def __init__(self):
        self.db_path = os.path.join(BASE_DIR, "databases/Standings.db")
    def get(self):
        html_request2db_NBA_standings(db_path=self.db_path)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT TeamCity, TeamName, WINS, LOSSES FROM Standings')
        data = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        conn.close()
        return make_response(render_template('Standings.html', data=data, column_names=column_names))

api.add_resource(StandingsResource, "/NBA/Standings")

class Today_scoreboardResource(Resource):
    def __init__(self):
        self.db_path = os.path.join(BASE_DIR, "databases/scoreboard.db")
    def get(self):
        table_name_today = html_request2db_NBA_today_scoreboard(db_path=self.db_path)
        # 连接到SQLite数据库
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f'SELECT gameStatus, gameStatusText, homeTeamName, homeTeamScore, awayTeamScore, awayTeamName FROM {table_name_today}')
        data = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        conn.close()
        return make_response(render_template('today_scoreboard.html', data=data, column_names=column_names))

api.add_resource(Today_scoreboardResource, "/NBA/Today_scoreboard")

class UserResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('username', type=str, required=True, help='用户名不能为空')
        self.parser.add_argument('password', type=str, required=True, help='密码不能为空')
        self.DATABASE = os.path.join(BASE_DIR, "users.db")
        conn = sqlite3.connect(self.DATABASE)
        cursor = conn.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", ('users',))
        if not cursor.fetchone():
            cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, token TEXT, coin INTEGER, sex TEXT)")
            conn.commit()
            conn.close()
    
    def get(self, username):
        token = request.headers.get('qwdadrization')
        username = request.headers.get('X-User-Data')
        username_decode, exp = chech_login(token=token, secret_key=app.config['SECRET_KEY'])
        logging.error('username' + username)
        logging.error(exp)

        conn = sqlite3.connect(self.DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user:
            if username_decode == username:
                return {"message": "user found", "username": user[1], "coin": user[4], "sex": user[5]}, 200
            else:
                return {"message": "user found", "username": user[1], "coin": user[4], "sex": ''}, 200
        else:
            return {"message": "user not found"}

    def put(self, username):
        args = self.parser.parse_args()
        username = args["username"]
        new_password = args["password"]
        conn = sqlite3.connect(self.DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE username=?", (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            cursor.execute("UPDATE users SET password=? WHERE username=?", (new_password, username))
            conn.commit()
            conn.close()
            return {"message": "用户密码已更新"}
        else:
            conn.close()
            return {"message": "用戶不存在"}

    def delete(self, username):
        args = self.parser.parse_args()
        username = args["username"]
        password = args["password"]
        conn = sqlite3.connect(self.DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT username, password FROM users WHERE username=?", (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            stored_username, stored_password = existing_user
            if password == stored_password:
                cursor.execute("DELETE FROM users WHERE username=?", (username,))
                conn.commit()
                conn.close()
                return {"message": str(username) + "用户已刪除"}
            else:
                conn.close()
                return {"message": str(username) + "密码錯誤"}
        else:
            conn.close()
            return {"message": str(username) + "用戶不存在"}
    
    def post(self, username):
        post_parser = reqparse.RequestParser()
        post_parser.add_argument('username', type=str, required=True, help='用户名不能为空')
        post_parser.add_argument('password', type=str, required=True, help='密码不能为空')
        post_parser.add_argument('sex', type=str, default='', help='性別')
        args = post_parser.parse_args()
        username = args["username"]
        password = args["password"]
        sex = args["sex"]
        conn = sqlite3.connect(self.DATABASE)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password, coin, sex) VALUES (?, ?, ?, ?)", (username, password, 500, sex))
            return {"message": str(username) + "用户已创建"}
        except Exception as e:
            return jsonify({'message': "錯誤：用户已存在" + str(e)})
        finally:
            conn.commit()
            conn.close()

api.add_resource(UserResource, "/user/<string:username>")

class LoginResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('username', type=str, required=True, help='用户名不能为空')
        self.parser.add_argument('password', type=str, required=True, help='密码不能为空')
        self.DATABASE = os.path.join(BASE_DIR, "users.db")
        conn = sqlite3.connect(self.DATABASE)
        cursor = conn.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", ('users',))
        if not cursor.fetchone():
            cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, token TEXT, coin INTEGER, sex TEXT)")
            conn.commit()
            conn.close()
    
    def post(self):
        args = self.parser.parse_args()
        username = args['username']
        password = args['password']
        conn = sqlite3.connect(self.DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT username, password FROM users WHERE username=?", (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            stored_username, stored_password = existing_user
            if password == stored_password:
                conn.close()
                token = generate_token(username=username, secret_key=app.config['SECRET_KEY'])
                return {'token': token,
                        'message': str(username) + "登入成功"}, 200
            else:
                conn.close()
                return {"message": "密码錯誤"}, 401
        else:
            conn.close()
            return {"message": "用戶不存在"}, 401

api.add_resource(LoginResource, "/user/login")


if __name__ == '__main__':
   api_key = open('resource/ChatGPT_api_key.txt').read()
   openai.api_key = api_key
   app.run()