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


# View equipment details
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


# Update equipment details
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


# Add a new equipment
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


# Upload equipment image
@staff_bp.route('/equipment/upload', methods=['POST'])
def equipment_upload():
    if 'loggedin' in session and session['role'] == 'staff':
        file = request.files['file']
        file_name = uuid.uuid1().__str__() + '.' + file.filename.rsplit('.')[1]
        file.save(os.path.join('app/static', file_name))
        return jsonify({
            "code": 200,
            "message": "Success",
            "data": file_name
        })
    return jsonify({
        'code': 401,
        'message': 'Not Authorized'
    })


# View all orders
@staff_bp.route('/order_list')
def order_list():
    if 'loggedin' in session and session['role'] == 'staff':
        status = request.args.get('status')
        search = request.args.get('search')
        conn, cursor = db_cursor()
        cursor.execute(f"SELECT store_id FROM staff WHERE user_id = {session['userid']}")
        store_id = cursor.fetchone()['store_id']
        if status and search:
            cursor.execute(f"SELECT * FROM orders WHERE status = '{status}' AND store_id = {store_id} AND order_id = {search} ORDER BY creation_date DESC")
        elif status:
            cursor.execute(f"SELECT * FROM orders WHERE status = '{status}' AND store_id = {store_id} ORDER BY creation_date DESC")
        elif search:
            cursor.execute(f"SELECT * FROM orders WHERE store_id = {store_id} AND order_id = {search} ORDER BY creation_date DESC")
        else:
            cursor.execute(f"SELECT * FROM orders WHERE store_id = {store_id} ORDER BY creation_date DESC")
        orders = cursor.fetchall()
        for order in orders:
            cursor.execute(f"SELECT store_name FROM stores WHERE store_id = {order['store_id']}")
            order['store_name'] = cursor.fetchone()['store_name']
            cursor.execute(f"SELECT username, email, date_of_birth FROM user WHERE user_id = {order['user_id']}")
            order['user_info'] = cursor.fetchone()
        cursor.close()
        return render_template('staff_order_list.html', orders=orders)
    return redirect(url_for('home.login'))


# View order details
@staff_bp.route('/order_detail/<int:order_id>')
def order_detail(order_id):
    if 'loggedin' in session and session['role'] == 'staff':
        conn, cursor = db_cursor()
        cursor.execute(f"SELECT * FROM order_items WHERE order_id = {order_id}")
        items = cursor.fetchall()
        for item in items:
            cursor.execute(f"SELECT name, status, Image FROM equipment WHERE equipment_id = {item['equipment_id']}")
            data = cursor.fetchone()
            item['name'] = data['name']
            item['status'] = data['status']
            item['Image'] = data['Image']
        cursor.close()
        return render_template('staff_order_detail.html', items=items, order_id=order_id)
    return redirect(url_for('home.login'))


# Return equipment
@staff_bp.route('/equipment/return', methods=['POST'])
def return_equipment():
    if 'loggedin' in session and session['role'] == 'staff':
        order_id = request.form['order_id']
        equipment_id = request.form['equipment_id']
        conn, cursor = db_cursor()
        cursor.execute(f"UPDATE equipment SET status = 'Available' WHERE equipment_id = {equipment_id}")
        conn.commit()
        cursor.execute(f"SELECT equipment_id FROM order_items WHERE order_id = {order_id}")
        ids = cursor.fetchall()
        all_return = True
        for id in ids:
            cursor.execute(f"SELECT status FROM equipment WHERE equipment_id = {id['equipment_id']}")
            if cursor.fetchone()['status'] == 'Rented':
                all_return = False
                break
        if all_return:
            cursor.execute(f"UPDATE orders SET status = 'Completed' WHERE order_id = {order_id}")
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


@staff_bp.route('/fetch_order/<int:order_id>')
def fetch_order(order_id):
    if 'loggedin' in session and session['role'] == 'staff':
        conn, cursor = db_cursor()
        cursor.execute(f"UPDATE orders SET status = 'Ongoing' WHERE order_id = {order_id}")
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


# Cancel order and refund
@staff_bp.route('/refund_order/<int:order_id>')
def refund_order(order_id):
    if 'loggedin' in session and session['role'] == 'staff':
        conn, cursor = db_cursor()
        cursor.execute(f"UPDATE orders SET status = 'Canceled' WHERE order_id = {order_id}")
        conn.commit()
        cursor.execute(f"UPDATE payments SET payment_status = 'Refunded' WHERE order_id = {order_id}")
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


# Equipment repair history
@staff_bp.route('/equipment_repair')
def equipment_repair():
    if 'loggedin' in session and session['role'] == 'staff':
        # conn, cursor = db_cursor()
        # cursor.execute("SELECT * FROM equipment WHERE status = 'Damaged'")
        # equipments = cursor.fetchall()
        # cursor.close()
        return render_template('staff_equipment_repair.html')
    return redirect(url_for('auth_bp.login'))


# Equipment rental history
@staff_bp.route('/equipment_rent')
def equipment_rent():
    if 'loggedin' in session and session['role'] == 'staff':
        # conn, cursor = db_cursor()
        # cursor.execute("SELECT * FROM equipment WHERE status = 'Damaged'")
        # equipments = cursor.fetchall()
        # cursor.close()
        return render_template('staff_equipment_rent.html')
    return redirect(url_for('auth_bp.login'))


# View all equipment category
def all_category():
    conn, cursor = db_cursor()
    cursor.execute("SELECT category FROM equipment GROUP BY category")
    categories = cursor.fetchall()
    cursor.close()
    return categories

    