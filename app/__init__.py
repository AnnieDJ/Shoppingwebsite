from flask import Flask, jsonify, request, session
from .home_views import home_bp
from .customer_views import customer_bp
from .staff_views import staff_bp
from .local_manager_views import local_manager_bp
from .national_manager_views import national_manager_bp
from .admin_views import admin_bp
from .chat_view import chat_bp
import redis
import json

def create_app():
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = 'app/static'
    app.config['DB_USER'] = 'root'
    app.config['DB_PASSWORD'] = 'root1234'
    app.config['DB_HOST'] = 'localhost'
    app.config['DB_NAME'] = 'agrihire'
    app.secret_key = 'the first secret key for ava'

    # Initialize Redis connection
    redis_conn = redis.Redis(host='localhost', port=6379, db=0)
    redis_conn.flushall()

    # Register blueprints
    app.register_blueprint(home_bp, url_prefix='/')
    app.register_blueprint(customer_bp, url_prefix='/customer')
    app.register_blueprint(staff_bp, url_prefix='/staff')
    app.register_blueprint(local_manager_bp, url_prefix='/local_manager')
    app.register_blueprint(national_manager_bp, url_prefix='/national_manager')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(chat_bp, url_prefix='/chat')

    @app.route('/send_message', methods=['POST'])
    def send_message():
        data = request.get_json()
        message_info = {
            'username': session.get('username', 'Guest'),
            'role': session.get('role', 'NoRole'),
            'message': data['message']
        }
        redis_conn.lpush('chat_messages', json.dumps(message_info))
        return jsonify({"status": "Message sent"})

    @app.route('/get_messages', methods=['GET'])
    def fetch_chat_messages():
        try:
            # Fetch all messages; assume they are stored as JSON strings
            raw_messages = redis_conn.lrange('chat_messages', 0, -1)
            # Decode each message and parse as JSON, skip empty or malformatted data
            messages = [json.loads(msg.decode('utf-8')) for msg in raw_messages if msg.strip()]
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return jsonify({"error": "Error decoding messages"}), 400
        except Exception as e:
            print(f"Unexpected error: {e}")
            return jsonify({"error": "Unexpected error occurred"}), 500

        return jsonify(messages)

    return app
