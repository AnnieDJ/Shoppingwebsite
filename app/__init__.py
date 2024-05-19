from flask import Flask
from .home_views import home_bp
from .customer_views import customer_bp
from .staff_views import staff_bp
from .local_manager_views import local_manager_bp
from .national_manager_views import national_manager_bp
from .admin_views import admin_bp

def create_app():
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = 'app/static'
    app.config['DB_USER'] = 'root'
    app.config['DB_PASSWORD'] = '12345'
    app.config['DB_HOST'] = 'localhost'
    app.config['DB_NAME'] = 'maevaas$agrihire'
    app.register_blueprint(home_bp, url_prefix='/')
    app.register_blueprint(customer_bp, url_prefix='/customer')
    app.register_blueprint(staff_bp, url_prefix='/staff')
    app.register_blueprint(local_manager_bp, url_prefix='/local_manager')
    app.register_blueprint(national_manager_bp, url_prefix='/national_manager')
    app.register_blueprint(admin_bp, url_prefix='/admin')
   
    app.secret_key = 'the first secret key for ava'

    return app
