import sys, os
# 设置虚拟环境目录
activate_this = 'D:/VSProjects/SportStatesChatgpt/venv/Scripts/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

sys.path.insert(0, os.path.dirname(__file__))
from SportStatesChatgpt import app
application = app