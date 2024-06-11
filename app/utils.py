import mysql.connector
from flask import current_app
from contextlib import contextmanager
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from functools import wraps
from flask import redirect, session
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def get_db_connection():
    return mysql.connector.connect(
        user=current_app.config['DB_USER'],
        password=current_app.config['DB_PASSWORD'],
        host=current_app.config['DB_HOST'],
        database=current_app.config['DB_NAME'],
        auth_plugin='mysql_native_password',
        autocommit=True
    )

def get_cursor():
    conn = get_db_connection()
    return conn.cursor(dictionary=True)

from contextlib import contextmanager

def db_cursor():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    return conn, cursor

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def current_date_time():
    return datetime.now()

def one_month_later():
    return datetime.now() + relativedelta(months=1)

def one_year_later():
    return datetime.now() + timedelta(days=365)

def register_age_validation(date_of_birth):
    current_date = datetime.now()
    eighteen_years_ago = current_date - timedelta(days=16*365)
    return current_date - date_of_birth > eighteen_years_ago


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if isAuthenticated() == False:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

    
def isAuthenticated():
    return "username" in session







