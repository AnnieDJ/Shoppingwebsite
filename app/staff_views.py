from flask import current_app as app
from mysql.connector import Error as MySQLError
from flask import Blueprint,render_template, request, redirect, url_for, session, flash, jsonify
from app import utils
import re
from datetime import datetime, date
from .utils import db_cursor
from flask_hashing import Hashing
from . import hashing
from .utils import db_cursor, login_required
from .utils import db_cursor

staff_bp = Blueprint('staff', __name__, template_folder='templates/staff')


## Staff dashboard ##
@staff_bp.route('/dashboard')
def dashboard():
    if 'loggedin' in session and session['role'] == 'staff':
        return render_template('staff_dashboard.html')
    return redirect(url_for('home.login'))

    

## Staff Profile ## 
@staff_bp.route('/staff_profile', methods=['GET', 'POST'])
@login_required
def view_profile():
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
        store_id = request.form.get('store_id')

        try:
            cursor.execute(
                'UPDATE staff SET title = %s, first_name = %s, family_name = %s, phone_number = %s, store_id = %s WHERE user_id = %s',
                (title, first_name, family_name, phone, store_id, session['userid'])
            )
            cursor.execute(
                'UPDATE user SET email = %s WHERE user_id = %s',
                (email, session['userid'])
            )
            flash('Your profile has been successfully updated!', 'success')
        except MySQLError as e:
            flash(f"An error occurred: {e}", 'danger')

    cursor.execute(
        'SELECT u.username, u.email, u.password_hash, u.role, s.title, s.first_name, s.family_name, s.phone_number, s.store_id '
        'FROM user u '
        'JOIN staff s ON u.user_id = s.user_id '
        'WHERE u.user_id = %s',
        (session['userid'],)
    )
    data = cursor.fetchone()

    return render_template('staff_profile.html', data=data)    




## Staff Change Password ##
@staff_bp.route('/change_password', methods=['POST'])
@login_required
def change_password():
    if 'userid' not in session:
        flash("User ID not found in session. Please log in again.", 'danger')
        return redirect(url_for('login'))

    password = request.form['password']

    if re.search('[a-zA-Z]', password) is None or re.search('[0-9]', password) is None:
        flash("Password must contain at least one letter and one digit.", 'warning')
        return redirect(url_for('staff.staff_profile'))

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

    return redirect(url_for('staff.staff_profile'))




# Inventory management
@staff_bp.route('/inventory_management')
def inventory_management():
    if 'loggedin' in session and session['role'] == 'staff':
        conn, cursor = db_cursor()
        category = []
        cursor.execute(f'SELECT store_id FROM staff WHERE user_id = {session["userid"]}')
        store_id = cursor.fetchone()['store_id']
        if store_id:
            cursor.execute(f"""
                        SELECT category,
                            SUM(CASE WHEN status = 'Available' THEN 1 ELSE 0 END) AS AvailableCount,
                            SUM(CASE WHEN status = 'Rented' THEN 1 ELSE 0 END) AS RentedCount,
                            SUM(CASE WHEN status = 'Under Repair' THEN 1 ELSE 0 END) AS UnderRepairCount,
                            SUM(CASE WHEN status = 'Retired' THEN 1 ELSE 0 END) AS RetiredCount
                        FROM
                            equipment
                        WHERE store_id = {store_id}
                        GROUP BY
                            category;
                        """)
            category = cursor.fetchall()
        cursor.close()
        return render_template('staff_inventory_management.html', category=category)
    return redirect(url_for('home.login'))


# View machinery's details
@staff_bp.route('/equipment/detail')
def equipment_detail():
    if 'loggedin' in session and session['role'] == 'staff':
        category = request.args.get('category')
        conn, cursor = db_cursor()
        cursor.execute(f"SELECT * FROM equipment WHERE category = '{category}'")
        equipment = cursor.fetchall()
        cursor.close()
        return render_template('staff_equipment_detail.html', equipment=equipment, categories=all_category())
    return redirect(url_for('home.login'))


@staff_bp.route('/equipment/update', methods=['POST'])
def equipment_update():
    if 'loggedin' in session and session['role'] == 'staff':
        serial_number = request.form['serial_number']
        Image = request.form['Image']
        purchase_date = request.form['purchase_date']
        cost = request.form['cost']
        category = request.form['category']
        status = request.form['status']
        conn, cursor = db_cursor()
        cursor.execute(f"UPDATE equipment SET Image = '{Image}', purchase_date = '{purchase_date}', cost = '{cost}', category = '{category}', status = '{status}' WHERE serial_number = '{serial_number}'")
        conn.commit()
        cursor.close()
        return jsonify({
            "code": 200,
            "message": "Success",
            "data": True
        })
    return jsonify({
        'code': 401,
        'message': 'Not Authorized'
    })


@staff_bp.route('/equipment/add', methods=['POST'])
def equipment_add():
    if 'loggedin' in session and session['role'] == 'staff':
        serial_number = request.form['serial_number']
        name = request.form['name']
        description = request.form['description']
        Image = request.form['Image']
        purchase_date = request.form['purchase_date']
        cost = request.form['cost']
        category = request.form['category']
        status = request.form['status']
        conn, cursor = db_cursor()
        cursor.execute(f'SELECT store_id FROM staff WHERE user_id = {session["userid"]}')
        store_id = cursor.fetchone()['store_id']
        cursor.execute(f"INSERT INTO equipment (serial_number, name, description, Image, purchase_date, cost, category, status, maximum_date, minimum_date, store_id) VALUES ('{serial_number}', '{name}', '{description}', '{Image}', '{purchase_date}', '{cost}', '{category}', '{status}', '360', '1', '{store_id}')")
        conn.commit()
        cursor.close()
        return jsonify({
            "code": 200,
            "message": "Success",
            "data": True
        })
    return jsonify({
        'code': 401,
        'message': 'Not Authorized'
    })


def all_category():
    conn, cursor = db_cursor()
    cursor.execute("SELECT category FROM equipment GROUP BY category")
    categories = cursor.fetchall()
    cursor.close()
    return categories

    