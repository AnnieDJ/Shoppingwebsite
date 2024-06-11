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
        cursor.execute("SELECT * FROM equipment JOIN stores ON equipment.store_id = stores.store_id WHERE stores.store_name = %s AND equipment.status = 'Available'", (name,))
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


@customer_bp.route('/order_list')
def order_list():
    if 'loggedin' in session and session['role'] == 'customer':
        status = request.args.get('status')
        conn, cursor = db_cursor()
        if status:
            cursor.execute(f"SELECT * FROM orders WHERE user_id = {session['userid']} AND status = '{status}'")
        else:
            cursor.execute(f"SELECT * FROM orders WHERE user_id = {session['userid']}")
        orders = cursor.fetchall()
        for order in orders:
            cursor.execute(f"SELECT store_name FROM stores WHERE store_id = {order['store_id']}")
            order['store_name'] = cursor.fetchone()['store_name']
        cursor.close()
        return render_template('customer_order_list.html', orders=orders)
    return redirect(url_for('home.login'))


@customer_bp.route('/order_detail/<int:order_id>')
def order_detail(order_id):
    if 'loggedin' in session and session['role'] == 'customer':
        conn, cursor = db_cursor()
        cursor.execute(f"SELECT * FROM order_items WHERE order_id = {order_id}")
        items = cursor.fetchall()
        cursor.execute(f"SELECT status FROM orders WHERE order_id = {order_id}")
        status = cursor.fetchone()['status']
        for item in items:
            cursor.execute(f"SELECT name, store_id, Image FROM equipment WHERE equipment_id = {item['equipment_id']}")
            data = cursor.fetchone()
            item['name'] = data['name']
            item['store_id'] = data['store_id']
            item['Image'] = data['Image']
            cursor.execute(f"SELECT store_name, address FROM stores WHERE store_id = {data['store_id']}")
            data = cursor.fetchone()
            item['store_name'] = data['store_name']
            item['address'] = data['address']
        cursor.close()
        return render_template('customer_order_detail.html', items=items, status=status)
    return redirect(url_for('home.login'))


@customer_bp.route('/order_detail/cancel/<int:order_id>')
def cancel_order(order_id):
    if 'loggedin' in session and session['role'] == 'customer':
        conn, cursor = db_cursor()
        cursor.execute(f"UPDATE orders SET status = 'Canceled' WHERE order_id = {order_id}")
        conn.commit()
        cursor.execute(f"SELECT equipment_id FROM order_items WHERE order_id = {order_id}")
        for entry in cursor.fetchall():
            cursor.execute(f"UPDATE equipment SET status = 'Available' WHERE equipment_id = {entry['equipment_id']}")
            conn.commit()
        cursor.execute(f"UPDATE payments SET payment_status = 'Refunded' WHERE order_id = {order_id}")
        conn.commit()
        cursor.close()
        return jsonify({
            'code': 200,
            'message': 'Success',
            'data': True
        })
    return jsonify({
        'code': 401,
        'message': 'Not Authorized'
    })


@customer_bp.route('/equipment', methods=['POST'])
def equipment():
    if 'loggedin' in session and session['role'] == 'customer':
        session.get('')
        ids = request.form.get('ids') or '999999999999999999'
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


@customer_bp.route('/search')
def search():
    if 'loggedin' in session and session['role'] == 'customer':
        query = request.args.get('query')
        conn, cursor = db_cursor()
        cursor.execute(f"SELECT * FROM equipment WHERE name LIKE '%{query}%'")
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


@customer_bp.route('/payment', methods=['POST'])
def payment():
    if 'loggedin' in session and session['role'] == 'customer':
        order = eval(request.form.get('order'))
        order_items = eval(request.form.get('order_items'))
        payment = eval(request.form.get('payment'))
        conn, cursor = db_cursor()
        cursor.execute(f"INSERT INTO orders (user_id, store_id, total_cost, tax, discount, final_price, status, creation_date) VALUES ('{session['userid']}', '{order['store_id']}', '{order['total_cost']}', '{order['tax']}', '{order['discount']}', '{order['final_price']}', '{order['status']}', '{order['creation_date']}')")
        conn.commit()
        cursor.execute(f"SELECT order_id FROM orders WHERE user_id = '{session['userid']}' AND store_id = '{order['store_id']}' AND total_cost = '{order['total_cost']}' AND tax = '{order['tax']}' AND discount = '{order['discount']}' AND final_price = '{order['final_price']}' AND status = '{order['status']}' AND creation_date = '{order['creation_date']}'")
        order_id = cursor.fetchone()['order_id']
        for item in order_items:
            cursor.execute(f"INSERT INTO order_items (order_id, equipment_id, quantity, price, start_time, end_time) VALUES ('{order_id}', '{item['equipment_id']}', '{item['quantity']}', '{item['price']}', '{item['start_time']}', '{item['end_time']}')")
            cursor.execute(f"UPDATE equipment SET status = 'Rented' WHERE equipment_id = '{item['equipment_id']}'")
            conn.commit()
        cursor.execute(f"INSERT INTO payments (order_id, user_id, payment_type, payment_status, amount, payment_date) VALUES ('{order_id}', '{session['userid']}', '{payment['payment_type']}', '{payment['payment_status']}', '{payment['amount']}', '{payment['payment_date']}')")
        conn.commit()
        cursor.close()
        return jsonify({
            'code': 200,
            'message': 'Success',
            'data': ''
        })
    return jsonify({
        'code': 401,
        'message': 'Not Authorized'
    })


@customer_bp.route('/discount')
def discount():
    if 'loggedin' in session and session['role'] == 'customer':
        conn, cursor = db_cursor()
        cursor.execute("SELECT * FROM discount")
        discounts = cursor.fetchall()
        cursor.close()
        return jsonify({
            'code': 200,
            'message': 'Success',
            'data': discounts
        })
    return jsonify({
        'code': 401,
        'message': 'Not Authorized'
    })


@customer_bp.route('/is_available', methods=['POST'])
def is_available():
    if 'loggedin' in session and session['role'] == 'customer':
        previous_id = request.form['previous_id']
        id = request.form['id']
        conn, cursor = db_cursor()
        cursor.execute(f"SELECT store_id FROM equipment WHERE equipment_id in {( previous_id, id )}")
        store_ids = cursor.fetchall()
        cursor.close()
        return jsonify({
            'code': 200,
            'message': 'Success',
            'data': True if store_ids[0]['store_id'] == store_ids[1]['store_id'] else False
        })
    return jsonify({
        'code': 401,
        'message': 'Not Authorized'
    })

@customer_bp.route('/view_news')
@login_required
def view_news():
    if 'loggedin' in session and session['role'] in ['customer']:
        conn, cursor = db_cursor()
        cursor.execute("""
            SELECT news_id, title, content, publish_date, creator_id, store_id
            FROM news
            ORDER BY publish_date DESC
        """)
        news_items = cursor.fetchall()
        cursor.close()
        return render_template('customer_view_news.html', news_items=news_items)
    else:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('home.login'))