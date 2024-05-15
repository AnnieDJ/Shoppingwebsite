import mysql.connector
from flask import current_app
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


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

# Usage of get_cursor with context manager for safer resource handling
from contextlib import contextmanager

@contextmanager
def db_cursor():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        yield cursor
    finally:
        cursor.close()
        conn.close()

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
