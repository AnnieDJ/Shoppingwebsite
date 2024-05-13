# from flask import Flask
# from flask_hashing import Hashing

# app = Flask(__name__)
# hashing = Hashing(app)

# app.secret_key = 'the first secret key for ava'

# app.config['UPLOAD_FOLDER'] = 'app/static'  # Define where to store the uploaded files
# app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}  # Allowed upload file extensions


# from app import customer_views
# from app import staff_views
# from app import local_manager_views
# from app import home_views
# from app import national_manager_views
# from app import admin_views

# from .customer_views import *
# from .staff_views import *
# from .local_manager_views import *
# from .home_views import *
# from .national_manager_views import *
# from .admin_views import *


################################################################修改版本
# app/__init__.py
from flask import Flask
from flask_hashing import Hashing
from .home_views import home_bp


def create_app():
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = 'app/static'
    app.config['DB_USER'] = 'root'
    app.config['DB_PASSWORD'] = '12345'
    app.config['DB_HOST'] = 'localhost'
    app.config['DB_NAME'] = 'maevaas$agrihire'
    app.register_blueprint(home_bp, url_prefix='/')
        # Set the secret key
    app.secret_key = 'the first secret key for ava'

    from . import home_views, customer_views, staff_views, local_manager_views, national_manager_views, admin_views
    return app
