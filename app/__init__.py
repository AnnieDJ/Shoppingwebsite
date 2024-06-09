from flask import Flask, jsonify,request
from .home_views import home_bp
from .customer_views import customer_bp
from .staff_views import staff_bp
from .local_manager_views import local_manager_bp
from .national_manager_views import national_manager_bp
from .admin_views import admin_bp
from .chat_view import chat_bp
from datetime import datetime
import redis
from threading import Thread

def create_app():
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = 'app/static'
    app.config['DB_USER'] = 'root'
    app.config['DB_PASSWORD'] = 'root1234'
    app.config['DB_HOST'] = 'localhost'
    app.config['DB_NAME'] = 'agrihire'
    app.register_blueprint(home_bp, url_prefix='/')
    app.register_blueprint(customer_bp, url_prefix='/customer')
    app.register_blueprint(staff_bp, url_prefix='/staff')
    app.register_blueprint(local_manager_bp, url_prefix='/local_manager')
    app.register_blueprint(national_manager_bp, url_prefix='/national_manager')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(chat_bp, url_prefix='/chat')
    app.secret_key = 'the first secret key for ava'
    messages = []  

    redis_conn = redis.Redis(host='localhost', port=6379, db=0)  

    @app.route('/send_message', methods=['POST'])
    def send_message():
        content = request.json['message']
        redis_conn.lpush('chat_messages', content)  
        return jsonify({"status": "Message sent"})

    @app.route('/get_messages', methods=['GET'])
    def fetch_chat_messages():
        messages = redis_conn.lrange('chat_messages', 0, -1)  
        messages = [msg.decode('utf-8') for msg in messages]
        return jsonify(messages)


    return app
