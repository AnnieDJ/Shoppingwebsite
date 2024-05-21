from flask import current_app as app
from mysql.connector import Error as MySQLError
from flask import Blueprint,render_template, request, redirect, url_for, session, flash
from app import utils
import re
from datetime import datetime
from .utils import db_cursor
from flask_hashing  import Hashing

staff_bp = Blueprint('staff', __name__, template_folder='templates/staff')


# staff dashboard
@staff_bp.route('/dashboard')
def dashboard():
    if 'loggedin' in session and session['role'] == 'staff':
        conn, cursor = db_cursor()
        try:
                   
            ## view rental list ## 
            cursor.execute("""
                SELECT r.*, u.username, e.name as equipment_name
                FROM rentals r
                JOIN user u ON r.user_id = u.user_id
                JOIN equipment e ON r.equipment_id = e.equipment_id
                ORDER BY r.rental_id DESC
                LIMIT 5 
            """)
            rentals = cursor.fetchall()
            
            ## view order list ##
            cursor.execute("""
                SELECT order_id, user_id, store_id, total_cost, tax, discount, final_price, status, creation_date
                FROM orders
                ORDER BY creation_date DESC
                LIMIT 5  
            """)
            orders = cursor.fetchall()
            
            ## view payment list ##
            cursor.execute("""
                SELECT payment_id, order_id, user_id, payment_type, amount, payment_status, payment_date
                FROM payments
                ORDER BY payment_date DESC
                LIMIT 5  
            """)
            payments = cursor.fetchall()
            
            ## view news list ##
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
            
        return render_template('staff_dashboard.html', rentals=rentals, orders=orders, payments=payments, promotions=promotions)
    else:
        return redirect(url_for('home.login'))


## Staff Profile ## - still working in progress
@staff_bp.route('/profile')
def view_profile():
    if 'loggedin' in session and session['role'] == 'staff':
        conn, cursor = db_cursor()
        try:
            cursor.execute("""
                SELECT s.*, u.username 
                FROM staff s 
                JOIN user u ON s.user_id = u.user_id 
                WHERE u.username = %s
            """, (session['username'],))
            staff_profile = cursor.fetchone()
        
        except Exception as e:
            print("An error occurred:", e)
            flash("A database error occurred. Please try again.")
            return redirect(url_for('home.login'))
        finally:
            cursor.close()
            conn.close()

        if staff_profile:
            return render_template('staff_profile.html', staff_profile=staff_profile, role=session['role'])
        else:
            flash('Profile not found', 'error')
            return redirect(url_for('staff.dashboard'))
        
    else:
        return redirect(url_for('home'))

## view Rentals ##
@staff_bp.route('/rentals')
def view_rentals():
    if 'loggedin' in session and session['role'] == 'staff':
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
        return redirect(url_for('staff.dashboard'))


## View Orders ##
@staff_bp.route('/orders')
def view_orders():
    if 'loggedin' in session and session['role'] == 'staff':
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
        return redirect(url_for('staff.dashboard'))


## View Payments ##
@staff_bp.route('/payment')
def view_payments():
    if 'loggedin' in session and session['role'] == 'staff':
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
        return redirect(url_for('staff.dashboard'))


## View Promotions (News) ##
@staff_bp.route('/promotions')
def view_promotions(): #news
    if 'loggedin' in session and session['role'] == 'staff':
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
        return redirect(url_for('staff.dashboard'))