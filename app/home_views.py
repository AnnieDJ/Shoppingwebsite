
print ("imported home view")

from flask import current_app as app
from mysql.connector import Error as MySQLError
from flask import Blueprint,render_template, request, redirect, url_for, session, flash
from app import utils
import re
from datetime import datetime
from .utils import db_cursor
from flask_hashing  import Hashing


hashing = Hashing()

home_bp = Blueprint('home', __name__, template_folder='templates')

@home_bp.route('/')
@home_bp.route('/home')
def home():
    
    return render_template('index.html')
@home_bp.route('/register', methods=['GET', 'POST'])
def register():
    msg = session.pop('msg', None) if 'msg' in session else None
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        family_name = request.form.get('family_name')
        username = request.form.get('user_name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        address = request.form.get('address')
        date_of_birth = request.form.get('date_of_birth')
        title = request.form.get('title')
        password = request.form.get('confirm_password')

        if date_of_birth:
            date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d')

        today = datetime.now()
        age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))

        if not all([username, first_name, family_name, phone, email, address, date_of_birth, title, password]):
            msg = 'Please fill out all the fields!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not age > 18:  # Assume this function exists and is correct
            msg = 'Customer should be over 18 years old!'
        else:
            try:
                with utils.db_cursor() as cursor:
                    # Check if user already exists
                    cursor.execute('SELECT * FROM customer WHERE username = %s', (username,))
                    if cursor.fetchone():
                        flash('Account already exists!', 'error')
                        return redirect(url_for('home.register'))
                    else:
                        # Insert into user table
                        hashed_password = hashing.hash_value(password, salt='ava')  # Assuming a hashing function

                        cursor.execute('INSERT INTO customer (title, first_name, family_name, phone_number, email, address, date_of_birth, username,password_hash) VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s)',
                                       ( title, first_name, family_name, phone, email, address, date_of_birth, username,hashed_password))
                        
                        
                        flash('Registration successful!', 'success')
                        return redirect(url_for('home.login'))
            except Exception as e:
                msg = f"Registration failed: {str(e)}"
                flash('Registration failed!', 'error')

    return render_template('index.html', msg=msg)



