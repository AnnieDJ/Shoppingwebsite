# from flask import Flask
# from flask_hashing import Hashing
# from flask import render_template




# app = Flask(__name__)
# hashing = Hashing(app)

# @app.route('/')
# def home():
#     return render_template("index.html")

# if __name__ == '__main__':
#     app.run(debug=True)

# app.py
# 这个文件现在只是作为一个备用的启动脚本使用，不再定义 Flask 应用实例
from app import app  # 从 app 包导入已经创建和配置的 app 实例

if __name__ == '__main__':
    app.run(debug=True)
