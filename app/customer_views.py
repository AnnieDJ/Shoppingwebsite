from flask import current_app as app
from mysql.connector import Error as MySQLError
from flask import Blueprint,render_template, request, redirect, url_for, session, flash,jsonify,Flask
from app import utils
import re
from datetime import datetime
from .utils import db_cursor
from flask_hashing  import Hashing
from . import hashing
from .utils import db_cursor, login_required


customer_bp = Blueprint('customer', __name__, template_folder='templates/customer')


# customer dashboard
@customer_bp.route('/dashboard')
def dashboard():
    if 'loggedin' in session and session['role'] == 'customer':
        conn, cursor = db_cursor()
        cursor.execute("SELECT * FROM stores")
        stores = cursor.fetchall()
        cursor.close()
        return render_template('customer_dashboard.html', stores=stores)
    return redirect(url_for('home.login'))


@customer_bp.route('/customer_profile', methods=['GET', 'POST'])
@login_required
def customer_profile():
    conn, cursor = db_cursor()
    if 'userid' not in session:
        flash("User ID not found in session. Please log in again.", 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form.get('title')
        first_name = request.form.get('first_name')
        family_name = request.form.get('last_name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        address = request.form.get('address')

        try:
            cursor.execute(
                'UPDATE customer SET title = %s, first_name = %s, family_name = %s, phone_number = %s, address = %s WHERE user_id = %s',
                (title, first_name, family_name, phone, address, session['userid'])
            )
            cursor.execute(
                'UPDATE user SET email = %s WHERE user_id = %s',
                (email, session['userid'])
            )
            flash('Your profile has been successfully updated!', 'success')
        except MySQLError as e:
            flash(f"An error occurred: {e}", 'danger')

    cursor.execute(
        'SELECT u.username, u.email, u.password_hash, u.role, c.title, c.first_name, c.family_name, c.phone_number, c.address '
        'FROM user u '
        'JOIN customer c ON u.user_id = c.user_id '
        'WHERE u.user_id = %s',
        (session['userid'],)
    )
    data = cursor.fetchone()

    return render_template('customer_profile.html', data=data)


# allow customer to change password
@customer_bp.route('/change_password', methods=['POST'])
@login_required
def change_password():
    if 'userid' not in session:
        flash("User ID not found in session. Please log in again.", 'danger')
        return redirect(url_for('login'))

    password = request.form['password']

    if re.search('[a-zA-Z]', password) is None or re.search('[0-9]', password) is None:
        flash("Password must contain at least one letter and one digit.", 'warning')
        return redirect(url_for('customer.customer_profile'))

    hashed_password = hashing.hash_value(password, salt='ava')
    conn, cursor = db_cursor()

    try:
        cursor.execute(
            'UPDATE user SET password_hash = %s WHERE user_id = %s',
            (hashed_password, session['userid'])
        )
        conn.commit()
        flash("Your password has been successfully updated.", 'success')
    except MySQLError as e:
        flash(f"An error occurred: {e}", 'danger')

    return redirect(url_for('customer.customer_profile'))


@customer_bp.route('/store/<name>')
def store(name):
    if 'loggedin' in session and session['role'] == 'customer':
        conn, cursor = db_cursor()
        cursor.execute("SELECT * FROM equipment JOIN stores ON equipment.store_id = stores.store_id WHERE stores.store_name = %s", (name,))
        equipments = cursor.fetchall()
        cursor.close()
        return jsonify({
            'code': 200,
            'message': 'Success',
            'data': equipments
        })
    return jsonify({
        'code': 401,
        'message': 'Not Authorized'
    })

@customer_bp.route('/cart')
def cart():
    if 'loggedin' in session and session['role'] == 'customer':
        return render_template('customer_cart.html')
    return redirect(url_for('home.login'))


@customer_bp.route('/equipment', methods=['POST'])
def equipment():
    if 'loggedin' in session and session['role'] == 'customer':
        session.get('')
        ids = request.form.get('ids')
        conn, cursor = db_cursor()
        cursor.execute(f"SELECT * FROM equipment WHERE equipment_id in ({ids})")
        equipments = cursor.fetchall()
        cursor.close()
        return jsonify({
            'code': 200,
            'message': 'Success',
            'data': equipments
        })
    return jsonify({
        'code': 401,
        'message': 'Not Authorized'
    })
