from app import create_app


app = create_app()


if __name__ == '__main__':
    app.run(debug=True, port="5000")



# from app import create_app
# from flask_socketio import SocketIO

# app = create_app()
# socketio = SocketIO(app)  # 初始化 SocketIO，并传递 app 实例

# if __name__ == '__main__':
#     socketio.run(app, debug=True, port=5013)  # 使用 socketio.run 而不是 app.run
