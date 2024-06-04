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

# Usage of get_cursor with context manager for safer resource handling
from contextlib import contextmanager

#@contextmanager
def db_cursor():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    return conn, cursor
    #try:
     #   yield cursor
    #finally:
     #   cursor.close()
      #  conn.close()

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



def fetch_checklist_entries(cursor, store_id, date, limit=None):
    query = """
    SELECT r.rental_id, r.equipment_id, e.name AS equipment_name, 
           r.start_date, r.end_date, r.status, r.id_verified, co.first_name, co.family_name
    FROM rentals r
    JOIN equipment e ON r.equipment_id = e.equipment_id
    JOIN user u ON r.user_id = u.user_id
    LEFT JOIN customer co ON u.user_id = co.user_id
    WHERE r.start_date = %s AND r.status IN ('Completed', 'Pending', 'Canceled')
    AND e.store_id = %s
    ORDER BY r.start_date DESC
    """
    if limit:
        query += " LIMIT %s"
        cursor.execute(query, (date, store_id, limit))
    else:
        cursor.execute(query, (date, store_id))
    return cursor.fetchall()

def fetch_returns(cursor, store_id, date, limit=None):
    query = """
    SELECT r.rental_id, r.equipment_id, e.name AS equipment_name, 
           r.start_date, r.end_date, r.status, co.first_name, co.family_name
    FROM rentals r
    JOIN equipment e ON r.equipment_id = e.equipment_id
    JOIN user u ON r.user_id = u.user_id
    LEFT JOIN customer co ON u.user_id = co.user_id
    WHERE r.end_date = %s AND r.status IN ('Completed', 'Pending', 'Canceled')
    AND e.store_id = %s
    ORDER BY r.end_date DESC
    """
    if limit:
        query += " LIMIT %s"
        cursor.execute(query, (date, store_id, limit))
    else:
        cursor.execute(query, (date, store_id))
    return cursor.fetchall()

def fetch_rentals(cursor, store_id, limit=None):
    query = """
    SELECT r.*, u.username, e.name as equipment_name
    FROM rentals r
    JOIN user u ON r.user_id = u.user_id
    JOIN equipment e ON r.equipment_id = e.equipment_id
    WHERE e.store_id = %s
    ORDER BY r.start_date DESC
    """
    if limit:
        query += " LIMIT %s"
        cursor.execute(query, (store_id, limit))
    else:
        cursor.execute(query, (store_id,))
    return cursor.fetchall()

def fetch_orders(cursor, store_id, limit=None):
    query = """
    SELECT o.order_id, o.user_id, o.total_cost, o.tax, o.discount, o.final_price, o.status, o.creation_date
    FROM orders o
    WHERE o.store_id = %s
    ORDER BY o.creation_date DESC
    """
    if limit:
        query += " LIMIT %s"
        cursor.execute(query, (store_id, limit))
    else:
        cursor.execute(query, (store_id,))
    return cursor.fetchall()

def fetch_payments(cursor, store_id, limit=None):
    query = """
    SELECT p.payment_id, p.order_id, p.user_id, p.payment_type, p.payment_status, p.amount, p.payment_date
    FROM payments p
    JOIN orders o ON p.order_id = o.order_id
    WHERE o.store_id = %s
    ORDER BY p.payment_date DESC
    """
    if limit:
        query += " LIMIT %s"
        cursor.execute(query, (store_id, limit))
    else:
        cursor.execute(query, (store_id,))
    return cursor.fetchall()
