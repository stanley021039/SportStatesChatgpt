from flask import Flask, render_template, jsonify, request
from flask_restful import Api, Resource, reqparse
import sqlite3
import os
import logging
import openai
import json
from utils import get_standings_from_web_NBA, write_json_to_db_NBA, generate_token

app=Flask(__name__)
app.config['SECRET_KEY'] = 'w8eg4as21dg56f'
api = Api(app)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(level=logging.DEBUG, filename=os.path.join(BASE_DIR, "get_score.log"), filemode='w')

@app.route('/')
def index():
    return render_template('index.html')

db_path = os.path.join(BASE_DIR, "standings.db")
@app.route('/get_score', methods=['POST'])
def get_score():
    try:
        standings_json = get_standings_from_web_NBA()
        write_json_to_db_NBA(standings_json, db_path)
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

@app.route("/chat", methods=['POST'])
def chat_with_gpt():
    api_key = open(os.path.join(BASE_DIR, 'resource\ChatGPT_api_key.txt')).read()
    openai.api_key = api_key
    openai.organization = "org-J0PWE1RbQlGThBFfHT3iYmgO"
    json_input = request.get_json()
    prompt = json_input['text'] + "\n用繁體中文回答"
    # prompt = 'Which team won the 2020 NBA World Championship?'
    messages=[{"role": "user", "content": prompt}]
    logging.info('prompt:')
    logging.info(prompt)
    logging.info('key:')
    logging.info(api_key)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7,
        max_tokens=50
    )
    # with open(os.path.join(BASE_DIR,"gpt_response/response.json"), "r") as json_file:
    #     response = json.load(json_file)

    with open(os.path.join(BASE_DIR,"gpt_response/response.json"), "w") as json_file:
        json.dump(response, json_file)

    return jsonify({"response": response.choices[0].message.content})
    # return jsonify({"response": 'abc'})

@app.route('/Standings')
def standings_page():
    standings_json = get_standings_from_web_NBA()
    write_json_to_db_NBA(standings_json, db_path)
    # 连接到SQLite数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 执行查询，获取数据
    cursor.execute('SELECT TeamCity, TeamName, WINS, LOSSES FROM Standings')
    data = cursor.fetchall()

    column_names = [description[0] for description in cursor.description]

    # 关闭数据库连接
    conn.close()

    return render_template('Standings.html', data=data, column_names=column_names)

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/useraction')
def useraction_page():
    return render_template('useraction.html')

parser = reqparse.RequestParser()
parser.add_argument("username", type=str, help="用户名是必需的", required=True)
parser.add_argument("password", type=str, help="密码是必需的", required=True)

DATABASE = os.path.join(BASE_DIR, "users.db")
conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()
cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", ('users',))
if not cursor.fetchone():
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)")
    conn.commit()
    conn.close()

class UserResource(Resource):
    def get(self, username):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        conn.close()
        if user:
            return {"username": user[1], "password": user[2]}
        else:
            return {"message": "用户未找到"}, 404

    def put(self, username):
        args = parser.parse_args()
        new_password = args["password"]
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE username=?", (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            cursor.execute("UPDATE users SET password=? WHERE username=?", (new_password, username))
            conn.commit()
            conn.close()
            return {"message": "用户密码已更新"}
        else:
            conn.commit()
            conn.close()
            return {"message": "用戶不存在"}

    def delete(self, username):
        args = parser.parse_args()
        password = args["password"]
        conn = sqlite3.connect(DATABASE)
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
                conn.commit()
                conn.close()
                return {"message": str(username) + "密码錯誤"}
        else:
            conn.commit()
            conn.close()
            return {"message": str(username) + "用戶不存在"}

api.add_resource(UserResource, "/user/<string:username>")

class CreateUserResource(Resource):
    def post(self):
        args = parser.parse_args()
        username = args["username"]
        password = args["password"]
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            return {"message": str(username) + "用户已创建"}
        except Exception as e:
            return jsonify({'message': "錯誤：用户已存在" + str(e)})
        finally:
            conn.commit()
            conn.close()

api.add_resource(CreateUserResource, "/user")

class LoginResource(Resource):
    def post(self):
        args = parser.parse_args()
        username = args['username']
        password = args['password']
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT username, password FROM users WHERE username=?", (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            stored_username, stored_password = existing_user
            if password == stored_password:
                conn.close()
                token = generate_token(username=username, secret_key=app.config['SECRET_KEY'])
                return {'token': token,
                        'message': str(username) + "登入成功" + str(token)}, 200
            else:
                conn.close()
                return {"message": str(username) + "密码錯誤"}, 401
        else:
            conn.close()
            return {"message": str(username) + "用戶不存在"}, 401

api.add_resource(LoginResource, "/user/login")


if __name__ == '__main__':
   api_key = open('resource\ChatGPT_api_key.txt').read()
   openai.api_key = api_key
   app.run()