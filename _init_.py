from flask import Flask

app = Flask(__name__)

app.secret_key = 'the first secret key for ava'

app.config['UPLOAD_FOLDER'] = 'app/static'  # Define where to store the uploaded files
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}  # Allowed upload file extensions


from app import customer_views
from app import staff_views
from app import local_manager_views
from app import home_views
from app import national_manager_views
from app import admin_views

