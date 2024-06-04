# home_views.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, json,jsonify
import re
from datetime import datetime
from .utils import db_cursor
from . import hashing
from app import utils

home_bp = Blueprint('home', __name__, template_folder='templates')


# home page
@home_bp.route('/')
@home_bp.route('/home')
def home():
    return render_template('index.html')


# allow users to register
@home_bp.route('/register', methods=['GET', 'POST'])
def register():
    msg = session.pop('msg', None) if 'msg' in session else None
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        date_of_birth = request.form.get('date_of_birth')
        password = request.form.get('confirm_password')
        role = request.form.get('role')
        if date_of_birth:
            date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d')

        today = datetime.now()
        age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))

        if not all([username, role, email, date_of_birth, password]):
            msg = 'Please fill out all the fields!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not age > 18:  # Assume this function exists and is correct
            msg = 'Customer should be over 18 years old!'
        else:
            conn, cursor = db_cursor()

            cursor.execute('SELECT * FROM user WHERE username = %s', (username,))
            if cursor.fetchone():
                flash('Account already exists!', 'danger')
                #return redirect(url_for('home.register'))
                return render_template('index.html', msg=msg, modal='modal')  # Render the same registration page with a flash message

            else:
                # Insert into user table
                from . import hashing
                hashed_password = hashing.hash_value(password, salt='ava')  # Assuming a hashing function

                cursor.execute(
                    'INSERT INTO user (role, email, date_of_birth, username, password_hash, salt) VALUES (%s, %s, %s, %s, %s, %s)',
                    (role, email, date_of_birth, username, password, hashed_password))

                conn.commit()  # Make sure to commit the transaction

                flash('Registration successful!', 'success')#这个没有
                return redirect(url_for('home.home',msg=msg, modal='none'))  # modal='none' indicates not to open any modal

    return render_template('index.html', msg=msg)


# allow users to login
@home_bp.route('/login', methods=['GET', 'POST'])
def login():
    msg = session.pop('msg', None)

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        user_originpassword = request.form['password']

        # try:
        conn, cursor = db_cursor()

        cursor.execute("SELECT * FROM user WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user is not None:
            role = user['role']
            user_id = user['user_id']
            password_salt = user['password_hash']

            from . import hashing
            if hashing.check_value(password_salt, user_originpassword, salt='ava'):
                session['loggedin'] = True
                session['userid'] = user_id
                session['username'] = user['username']
                session['role'] = user['role']

                if role == 'customer':
                    return redirect(url_for('customer.dashboard'))
                elif role == 'staff':
                    return redirect(url_for('staff.dashboard'))
                elif role == 'local_manager':
                    return redirect(url_for('local_manager.dashboard'))
                elif role == 'national_manager':
                    return redirect(url_for('national_manager.dashboard'))
                elif role == 'admin':
                    return redirect(url_for('admin.dashboard'))
            else:
                flash('Invalid password!', 'error')
        else:
            flash('Invalid username!', 'error')

    return redirect(url_for('home.home'))  # Redirect back to home or appropriate page with modal


# allow users to log out
@home_bp.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('role', None)
    # Redirect to login page
    return render_template('index.html')


# users are required to login before using other features on the web app
@utils.login_required
@home_bp.route("/browse", methods=["GET", "POST"])
def get_store():
    cursor = utils.get_cursor()
    stores = cursor.execute("SELECT * FROM stores")
    stores = stores.fetchall()
    stores = json.dumps(stores)
    return render_template("chose.html", stores=stores)

@home_bp.route("/user")
def get_user():
    conn, cursor = db_cursor()
    user_id = session['userid']
    cursor.execute(f"SELECT * FROM user WHERE user_id = {user_id}")
    user = cursor.fetchone()
    return jsonify({
        "code": 200,
        "message": "Success",
        "data": user
    })
