from flask import current_app as app
from mysql.connector import Error as MySQLError
from flask import Blueprint,render_template, request, redirect, url_for, session, flash, jsonify,Flask
from app import utils
import re
from datetime import datetime
from .utils import db_cursor
from flask_hashing  import Hashing
from . import hashing
from .utils import db_cursor, login_required

local_manager_bp = Blueprint('local_manager', __name__, template_folder='templates/local_manager')


# local manager dashboard
@local_manager_bp.route('/dashboard')
def dashboard():
    if 'loggedin' in session and session ['role'] == 'local_manager':
        conn, cursor = db_cursor()
        try:
            cursor.execute("""
                SELECT r.*, u.username, e.name as equipment_name
                FROM rentals r
                JOIN user u ON r.user_id = u.user_id
                JOIN equipment e ON r.equipment_id = e.equipment_id
                ORDER BY r.rental_id DESC
                LIMIT 5 
            """)
            rentals = cursor.fetchall()

            cursor.execute("""
                SELECT order_id, user_id, store_id, total_cost, tax, discount, final_price, status, creation_date
                FROM orders
                ORDER BY creation_date DESC
                LIMIT 5  
            """)
            orders = cursor.fetchall()

            cursor.execute("""
                SELECT payment_id, order_id, user_id, payment_type, amount, payment_status, payment_date
                FROM payments
                ORDER BY payment_date DESC
                LIMIT 5  
            """)
            payments = cursor.fetchall()

            cursor.execute("""
                SELECT news_id, title, content, publish_date, creator_id, store_id
                FROM news
                ORDER BY publish_date DESC
                LIMIT 5  
            """)
            promotions = cursor.fetchall()
            
        except Exception as e:
            print("An error occurred:", e)
            flash("A database error occurred. Please try again.")
            return redirect(url_for('home.login'))
        finally:
            cursor.close()
            conn.close()  

        return render_template('local_manager_dashboard.html', rentals=rentals, orders=orders, payments=payments, promotions=promotions)
    else:
        return redirect(url_for('home.login'))
    
    
    

##Local Manager Profile ## 
@local_manager_bp.route('/local_manager_profile', methods=['GET', 'POST'])
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
                'UPDATE local_manager SET title = %s, first_name = %s, family_name = %s, phone_number = %s, store_id = %s WHERE user_id = %s',
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
        'SELECT u.username, u.email, u.password_hash, u.role, l.title, l.first_name, l.family_name, l.phone_number, l.store_id '
        'FROM user u '
        'JOIN local_manager l ON u.user_id = l.user_id '
        'WHERE u.user_id = %s',
        (session['userid'],)
    )
    data = cursor.fetchone()

    return render_template('local_manager_profile.html', data=data)    

 


## Local Manager Change Password ##
@local_manager_bp.route('/change_password', methods=['POST'])
@login_required
def change_password():
    if 'userid' not in session:
        flash("User ID not found in session. Please log in again.", 'danger')
        return redirect(url_for('login'))

    password = request.form['password']

    if re.search('[a-zA-Z]', password) is None or re.search('[0-9]', password) is None:
        flash("Password must contain at least one letter and one digit.", 'warning')
        return redirect(url_for('local_manager.local_manager_profile'))

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

    return redirect(url_for('local_manager.local_manager_profile'))





## view Rentals ##
@local_manager_bp.route('/rentals')
def view_rentals():
    if 'loggedin' in session and session['role'] == 'local_manager':
        conn, cursor = db_cursor()
        try:
            cursor.execute("""
                SELECT r.*, u.username, e.name as equipment_name
                FROM rentals r
                JOIN user u ON r.user_id = u.user_id
                JOIN equipment e ON r.equipment_id = e.equipment_id
            """)
            rentals = cursor.fetchall()
            
        except Exception as e:
            print("An error occurred:", e)
            flash("A database error occurred. Please try again.")
            return redirect(url_for('home.login'))
        finally:
            cursor.close()
            conn.close()
            
        return render_template('rentals_list.html', rentals=rentals)
    else:
        return redirect(url_for('local_manager.dashboard'))


## View Orders ##
@local_manager_bp.route('/orders')
def view_orders():
    if 'loggedin' in session and session['role'] == 'local_manager':
        conn, cursor = db_cursor()  
        try:
            cursor.execute("""
                SELECT order_id, user_id, store_id, total_cost, tax, discount, final_price, status, creation_date
                FROM orders
            """)
            orders = cursor.fetchall()
            
        except Exception as e:
            print("An error occurred:", e)
            flash("A database error occurred. Please try again.")
            return redirect(url_for('home.login'))
        finally:
            cursor.close()
            conn.close()  
            
        return render_template('order_list.html', orders=orders)
    else:
        return redirect(url_for('local_manager.dashboard'))


## View Payments ##
@local_manager_bp.route('/payment')
def view_payments():
    if 'loggedin' in session and session['role'] == 'local_manager':
        conn, cursor = db_cursor()  
        try:
        
            cursor.execute("""
                SELECT payment_id, order_id, user_id, payment_type, payment_status, amount, payment_date
                FROM payments
            """)
            payments = cursor.fetchall()
        
        except Exception as e:
            print("An error occurred:", e)
            flash("A database error occurred. Please try again.")
            return redirect(url_for('home.login'))
        finally:
            cursor.close()
            conn.close()  
        
        return render_template('payments.html', payments=payments)
    else:
        return redirect(url_for('local_manager.dashboard'))


## View Promotions (News) ##
@local_manager_bp.route('/promotions')
def view_promotions(): #news
    if 'loggedin' in session and session['role'] == 'local_manager':
        conn, cursor = db_cursor()  
        try:
            cursor.execute("""
                SELECT news_id, title, content, publish_date, creator_id, store_id
                FROM news
            """)
            promotions = cursor.fetchall()
        
        except Exception as e:
            print("An error occurred:", e)
            flash("A database error occurred. Please try again.")
            return redirect(url_for('home.login'))
        finally:
            cursor.close()
            conn.close()  
            
        return render_template('promotions.html', promotions=promotions)
    else:
        return redirect(url_for('local_manager.dashboard'))
    
    

## Local Manager View Reports ##
@local_manager_bp.route('/view_reports', methods=['POST'])
@login_required
def view_reports():
    return redirect(url_for('local_manager.local_manager_dashboard'))