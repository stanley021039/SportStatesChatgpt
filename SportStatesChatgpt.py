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
from utils import html_request2db_NBA_standings, html_request2db_NBA_today_scoreboard, generate_token, chech_login, get_date

app=Flask(__name__)
app.config['SECRET_KEY'] = 'w8eg4as21dg56f'
api = Api(app)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(level=logging.DEBUG, filename=os.path.join(BASE_DIR, "logs", "app.log"), filemode='w')

@app.before_request
def set_application_root():
    script_name = request.headers.get('X-Script-Name', '')
    app.config['APPLICATION_ROOT'] = script_name

@app.route('/ID_verify', methods=['GET'])
def ID_verify():
    logging.error('ID_verify')
    token = request.headers.get('qwdadrization')
    logging.error(token)
    current_user, exp = chech_login(token, secret_key=app.config['SECRET_KEY'])
    return {'current_user': current_user}

class homeResource(Resource):
    def get(self):
        template_variables = {'APPLICATION_ROOT': app.config['APPLICATION_ROOT']}
        return make_response(render_template('index.html', **template_variables))
api.add_resource(homeResource, "/")

class GPTResource(Resource):
    def __init__(self):
        self.db_scoreboard_path = os.path.join(BASE_DIR, "data/databases/scoreboard.db")
        self.db_standings_path = os.path.join(BASE_DIR, "data/databases/Standings.db")
        self.template_path = os.path.join(BASE_DIR, "GPT_resources/template.json")
    
    def load_prompts(self):
        with open(self.template_path, 'r') as file:
            self.messages = json.load(file)

    def post(self):
        frontpage = request.args.get('frontpage', '')
        season = request.args.get('season', '')
        date = request.args.get('date', '')
        if frontpage == 'scoreboard':
            with open(os.path.join(BASE_DIR, f"data/data_json/scoreboard_{date}.json"), 'r') as file:
                data_prompt = json.dumps(json.load(file))
                print(data_prompt[:10])
        elif frontpage == 'standings':
            with open(os.path.join(BASE_DIR, f"data/data_json/standings_{season}.json"), 'r') as file:
                data_prompt = json.dumps(json.load(file))
        user_prompt = request.get_json()['text']
        self.load_prompts()
        end_prompt = "但請用繁體中文回答，請用30字內的簡答\n"
        user_messages = {"role": "user", "content": f'{data_prompt}\n{user_prompt}\n{end_prompt}'}
        self.messages.append(user_messages)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.messages,
            temperature=0.7,
            max_tokens=100
        )
        text_response = response.choices[0].message.content
        self.messages.append({"role": "assistant", "content": text_response})

        return jsonify({"response": text_response})

api.add_resource(GPTResource, f"{app.config['APPLICATION_ROOT']}/GPT")

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


def get_standings_data(season):
    season_start = datetime(year=int(season), month=6, day=1)
    if datetime.now() < season_start:
        return {'data': []}
    db_path = os.path.join(BASE_DIR, "data/databases/Standings.db")
    json_path = os.path.join(BASE_DIR, f"data/data_json/standings_{season}.json")
    html_request2db_NBA_standings(db_path=db_path, json_path=json_path, season=season)
    table_name = f'season_{season}'
    print(f'get standings of season {season} from {db_path}, {table_name}')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f'SELECT team_name, wins, win_percentage, losses, loss_percentage FROM {table_name}')
    data = cursor.fetchall()
    conn.close()

    return {'data': data}

class StandingsPage(Resource):
    def get(self):
        season = str(int(get_date("%Y")) - 1)
        # data = get_standings_data(season)
        # print(data)
        return make_response(render_template('Standings.html', season=season, **app.config))

class StandingsData(Resource):
    def get(self):
        season = request.args.get('season', '2023')
        data = get_standings_data(season)
        return jsonify(data)

api.add_resource(StandingsPage, f"{app.config['APPLICATION_ROOT']}/NBA/Standings")
api.add_resource(StandingsData, f"{app.config['APPLICATION_ROOT']}/api/NBA/Standings_season_data")


def get_scoreboard_data(date):
    column_names = ['Game Status', 'Home Team', 'Score(Home)', 'Score(Away)', 'Away Team']
    year, month, day = date.split('-')
    date_start = datetime(year=int(year), month=int(month), day=int(day))
    if datetime.now() < date_start:
        return {'data': [], 'column_names': column_names}
    db_path = os.path.join(BASE_DIR, "data/databases/scoreboard.db")
    json_path = os.path.join(BASE_DIR, f"data/data_json/scoreboard_{date}.json")
    html_request2db_NBA_today_scoreboard(db_path=db_path, json_path=json_path, date=date)
    table_name = f"NBA_{date.replace('-', '_')}"
    print(f'get score board of {date} from {db_path}, {table_name}')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f'SELECT gameStatusText, homeTeamName, homeTeamScore, awayTeamScore, awayTeamName FROM {table_name}')
    data = cursor.fetchall()
    conn.close()

    return {'data': data, 'column_names': column_names}

class TodayScoreboardPage(Resource):
    def get(self):
        date = get_date()
        # data = get_scoreboard_data(date)
        return make_response(render_template('scoreboard.html', todate=date, **app.config))

class TodayScoreboardData(Resource):
    def get(self):
        date = request.args.get('date', '2024-01-19')
        data = get_scoreboard_data(date)
        return jsonify(data)

api.add_resource(TodayScoreboardPage, f"{app.config['APPLICATION_ROOT']}/NBA/scoreboard")
api.add_resource(TodayScoreboardData, f"{app.config['APPLICATION_ROOT']}/api/NBA/scoreboard_data")


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
   api_key = open('GPT_resources/ChatGPT_api_key.txt').read()
   openai.api_key = api_key
   openai.organization = "org-J0PWE1RbQlGThBFfHT3iYmgO"
   app.run(host='0.0.0.0', port=8000)