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

staff_bp = Blueprint('staff', __name__, template_folder='templates/staff')


## Staff dashboard ##
@staff_bp.route('/dashboard')
@login_required
def dashboard():
    if 'loggedin' in session and session['role'] in ['staff', 'local_manager']:
        conn, cursor = db_cursor()
        user_id = session['userid']  # Assuming 'userid' is stored in session upon login
        
        # Fetch the store_id and store name for the logged-in staff member
        cursor.execute("""
            SELECT s.store_id, st.store_name
            FROM staff s
            JOIN stores st ON s.store_id = st.store_id
            WHERE s.user_id = %s
        """, (user_id,))
        store_info = cursor.fetchone()
        store_name = store_info['store_name'] if store_info else 'Not Assigned'
        store_id = store_info['store_id'] if store_info else None
        
        if store_id:
        # Fetch top 5 daily checklist entries
            cursor.execute("""
                SELECT r.*, u.username, e.name as equipment_name
                FROM rentals r
                JOIN user u ON r.user_id = u.user_id
                JOIN equipment e ON r.equipment_id = e.equipment_id
                WHERE e.store_id = %s
                ORDER BY r.start_date DESC
                LIMIT 5
            """, (store_id,))
            top_bookings = cursor.fetchall()
            
            # Fetch top 5 returns
            today = date.today().strftime('%Y-%m-%d')
            cursor.execute("""
                SELECT r.rental_id, c.first_name, c.family_name, e.name as equipment_name, r.end_date, r.status, c.first_name, c.family_name
                FROM rentals r
                JOIN user u ON r.user_id = u.user_id
                JOIN equipment e ON r.equipment_id = e.equipment_id
                JOIN customer c ON u.user_id = c.user_id
                WHERE r.end_date = %s AND e.store_id = %s
                ORDER BY r.end_date DESC
                LIMIT 5
            """, (today, store_id))
            top_returns = cursor.fetchall()

            # Fetch top 5 rentals
            cursor.execute("""
                SELECT r.*, u.username, e.name as equipment_name
                FROM rentals r
                JOIN user u ON r.user_id = u.user_id
                JOIN equipment e ON r.equipment_id = e.equipment_id
                WHERE e.store_id = %s
                ORDER BY r.start_date DESC
                LIMIT 5
            """, (store_id,))
            top_rentals = cursor.fetchall()
            
            # Fetch top 5 orders
            cursor.execute("""
                SELECT o.order_id, o.user_id, o.total_cost, o.tax, o.discount, o.final_price, o.status, o.creation_date
                FROM orders o
                WHERE o.store_id = %s
                ORDER BY o.creation_date DESC
                LIMIT 5
            """, (store_id,))
            top_orders = cursor.fetchall()
            
        
            # Fetch top 5 payments
            cursor.execute("""
                SELECT p.payment_id, p.order_id, p.user_id, p.payment_type, p.payment_status, p.amount, p.payment_date
                    FROM payments p
                    JOIN orders o ON p.order_id = o.order_id
                    WHERE o.store_id = %s
                    ORDER BY p.payment_date DESC
                    LIMIT 5
            """, (store_id,))
            top_payments = cursor.fetchall()
        
        else:
            top_bookings, top_returns, top_rentals, top_orders, top_payments = [], [], [], [], []

        cursor.close()
        conn.close()
        
       # Choose the right template based on the role
        template_name = 'local_manager_dashboard.html' if session['role'] == 'local_manager' else 'staff_dashboard.html'
        return render_template(template_name, top_bookings=top_bookings, top_returns=top_returns, top_rentals=top_rentals, 
                               top_orders=top_orders, top_payments=top_payments, store_name=store_name)
    else:
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


## View Customers ##
@staff_bp.route('/customers')
def view_customers():
    if 'loggedin' in session and session['role'] == 'staff':
        conn, cursor = db_cursor()
        
        try:
            cursor.execute("""
            SELECT c.customer_id, c.user_id, c.title, c.first_name, c.family_name, c.phone_number, c.address, u.username
            FROM customer c
            JOIN user u ON c.user_id = u.user_id
            """)
            customers = cursor.fetchall()
        
        except Exception as e:
            print("An error occurred:", e)
            flash("A database error occurred. Please try again.")
            return redirect(url_for('home.login'))
        finally:
            cursor.close()
            conn.close()
            
        return render_template('staff_view_customers.html', customers=customers)
    else:
        return redirect(url_for('staff.dashboard'))


## view Rentals ##
@staff_bp.route('/rentals')
def view_rentals():
    if 'loggedin' in session and session['role'] == 'staff':
        conn, cursor = db_cursor()
        user_id = session['userid']
        
        try:
            
            # Fetch the store_id and store name for the logged-in staff member
            cursor.execute("""
                SELECT s.store_id, st.store_name
                FROM staff s
                JOIN stores st ON s.store_id = st.store_id
                WHERE s.user_id = %s
            """, (user_id,))
            store_info = cursor.fetchone()
            store_name = store_info['store_name'] if store_info else 'Not Assigned'
            store_id = store_info['store_id'] if store_info else None
            
            if store_id:
                cursor.execute("""
                    SELECT r.rental_id, c.first_name, c.family_name, e.name as equipment_name, r.start_date, r.end_date, r.status
                    FROM rentals r
                    JOIN customer c ON r.user_id = c.user_id
                    JOIN equipment e ON r.equipment_id = e.equipment_id
                """)
                rentals = cursor.fetchall()
            else:
                rentals = []
                
        except Exception as e:
            print("An error occurred:", e)
            flash("A database error occurred. Please try again.")
            return redirect(url_for('home.login'))
        finally:
            cursor.close()
            conn.close()
            
        return render_template('rentals_list.html', rentals=rentals, store_name=store_name)
    else:
        return redirect(url_for('staff.dashboard'))


## View Orders ##
@staff_bp.route('/orders')
def view_orders():
    if 'loggedin' in session and session['role'] == 'staff':
        conn, cursor = db_cursor()  
        user_id = session['userid']
        
        try:
            # Fetch the store_id and store name for the logged-in staff member
            cursor.execute("""
                SELECT s.store_id, st.store_name
                FROM staff s
                JOIN stores st ON s.store_id = st.store_id
                WHERE s.user_id = %s
            """, (user_id,))
            store_info = cursor.fetchone()
            store_name = store_info['store_name'] if store_info else 'Not Assigned'
            store_id = store_info['store_id'] if store_info else None
            
            if store_id:
                cursor.execute("""
                    SELECT o.order_id, c.first_name, c.family_name, o.store_id, o.total_cost, 
                    o.tax, o.discount, o.final_price, o.status, o.creation_date
                    FROM orders o
                    JOIN customer c ON o.user_id = c.user_id
                    WHERE o.store_id = %s
                """, (store_id,))
                orders = cursor.fetchall()
            else: 
                orders = []
            
        except Exception as e:
            print("An error occurred:", e)
            flash("A database error occurred. Please try again.")
            return redirect(url_for('home.login'))
        finally:
            cursor.close()
            conn.close()  
            
        return render_template('order_list.html', orders=orders, store_name=store_name)
    else:
        return redirect(url_for('staff.dashboard'))


## View Payments ##
@staff_bp.route('/payment')
def view_payments():
    if 'loggedin' in session and session['role'] == 'staff':
        conn, cursor = db_cursor()  
        user_id = session['userid']
        
        try:
            # Fetch the store_id and store name for the logged-in staff member
            cursor.execute("""
                SELECT s.store_id, st.store_name
                FROM staff s
                JOIN stores st ON s.store_id = st.store_id
                WHERE s.user_id = %s
            """, (user_id,))
            store_info = cursor.fetchone()
            store_name = store_info['store_name'] if store_info else 'Not Assigned'
            store_id = store_info['store_id'] if store_info else None
            
            if store_id:
                cursor.execute("""
                    SELECT p.payment_id, p.order_id, p.user_id, p.payment_type, p.payment_status, p.amount, p.payment_date
                    FROM payments p
                    JOIN orders o ON p.order_id = o.order_id
                    WHERE o.store_id = %s
                    ORDER BY p.payment_date DESC
                """, (store_id,))
                payments = cursor.fetchall()
            else:
                payments = []   
        
        except Exception as e:
            print("An error occurred:", e)
            flash("A database error occurred. Please try again.")
            return redirect(url_for('home.login'))
        finally:
            cursor.close()
            conn.close()  
        
        return render_template('payments.html', payments=payments, store_name=store_name)
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
    return redirect(url_for('staff.dashboard'))


# View machinery's details
@staff_bp.route('/equipment/detail')
def equipment_detail():
    if 'loggedin' in session and session['role'] == 'staff':
        category = request.args.get('category')
        conn, cursor = db_cursor()
        cursor.execute(f"SELECT * FROM equipment WHERE category = '{category}'")
        equipment = cursor.fetchall()
        cursor.close()
        return render_template('staff_equipment_detail.html', equipment=equipment)
    return redirect(url_for('staff.dashboard'))

# Update a machinery's details
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


# Add a new machinery
@staff_bp.route('/equipment/add', methods=['POST'])
def equipment_add():
    if 'loggedin' in session and session['role'] == 'staff':
        serial_number = request.form['serial_number']
        Image = request.form['Image']
        purchase_date = request.form['purchase_date']
        cost = request.form['cost']
        category = request.form['category']
        status = request.form['status']
        conn, cursor = db_cursor()
        cursor.execute(f"INSERT INTO equipment (serial_number, Image, purchase_date, cost, category, status) VALUES ('{serial_number}', '{Image}', '{purchase_date}', '{cost}', '{category}', '{status}')")
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


## Today's checklist ##
@staff_bp.route('/daily_checklist')
@login_required
def daily_checklist():
    if 'loggedin' in session and session['role'] in ['staff', 'local_manager']:
        today = date.today().strftime('%Y-%m-%d')
        conn, cursor = db_cursor()
        user_id = session['userid']
        
        try:
            # Fetch the store_id and store name for the logged-in staff member or local manager
            cursor.execute("""
                SELECT s.store_id, st.store_name
                FROM staff s
                JOIN stores st ON s.store_id = st.store_id
                WHERE s.user_id = %s
                UNION
                SELECT l.store_id, st.store_name
                FROM local_manager l
                JOIN stores st ON l.store_id = st.store_id
                WHERE l.user_id = %s
            """, (user_id, user_id))
            store_info = cursor.fetchone()
            store_name = store_info['store_name'] if store_info else 'Not Assigned'
            store_id = store_info['store_id'] if store_info else None
            
            if store_id:
                # Query today's bookings
                sql_query = """
                SELECT r.rental_id, r.equipment_id, e.name AS equipment_name, 
                        r.start_date, r.end_date, r.status, r.id_verified, co.first_name, co.family_name
                    FROM rentals r
                    JOIN equipment e ON r.equipment_id = e.equipment_id
                    JOIN user u ON r.user_id = u.user_id
                    LEFT JOIN customer co ON u.user_id = co.user_id
                    WHERE r.start_date = %s AND r.status IN ('Completed', 'Pending', 'Canceled');
                """
                print("Date for query:", today)
                cursor.execute(sql_query, (today,))  
                bookings = cursor.fetchall()
            else:
                bookings = []
            
        finally:
            cursor.close()
            conn.close()
        
        return render_template('daily_checklist.html', bookings=bookings, store_name=store_name, today=today)
    else:
        flash("You are not authorized to view this page.")
        return redirect(url_for('staff.dashboard'))
    
    
    
## Update Rental Status ##
@staff_bp.route('/update_rental_status', methods=['POST'])
@login_required
def update_rental_status():
        rental_id = request.form.get('rental_id')
        new_status = request.form.get('new_status')

        if not rental_id or not new_status:
            return jsonify({'error': 'Missing rental ID or status'}), 400

        conn, cursor = db_cursor()
        try:
            
            # Verify ID first before changing status to 'Completed'
            if new_status == 'Completed':
                cursor.execute("SELECT id_verified FROM rentals WHERE rental_id = %s", (rental_id,))
                result = cursor.fetchone()
                if not result or not result['id_verified']:
                    return jsonify({'error': 'ID verification is required before checkout.'}), 403
                
            cursor.execute("""
                UPDATE rentals
                SET status = %s
                WHERE rental_id = %s
            """, (new_status, rental_id))
            conn.commit()
            return jsonify({'success': True, 'message': 'Status updated successfully.'})
        except Exception as e:
            conn.rollback()
            return jsonify({'error': str(e), 'message': 'Failed to update status.'}), 500
        finally:
            cursor.close()
            conn.close()

## Verify ID ##
@staff_bp.route('/verify_id', methods=['POST'])
@login_required
def verify_id():
    rental_id = request.form.get('rental_id')
    id_verified = request.form.get('id_verified') == 'true'
    print("Rental ID:", rental_id, "ID Verified:", id_verified)  

    if not rental_id:
        return jsonify({'error': 'Missing rental ID'}), 400

    conn, cursor = db_cursor()
    try:
        cursor.execute("""
            UPDATE rentals
            SET id_verified = %s
            WHERE rental_id = %s
        """, (id_verified, rental_id))
        conn.commit()
        print("Update successful")  # Confirm successful commit
        return jsonify({'success': True, 'message': 'ID verification status updated successfully.'}), 200
    except Exception as e:
        print("Error:", e)  # Print any errors encountered
        conn.rollback()
        return jsonify({'error': str(e), 'message': 'Failed to update ID verification status.'}), 500
    finally:
        cursor.close()
        conn.close()
        

## Today's returns ##
@staff_bp.route('/daily_returns')
@login_required
def daily_returns():
    if 'loggedin' in session and session['role'] in ['staff', 'local_manager']:
        today = date.today().strftime('%Y-%m-%d')
        conn, cursor = db_cursor()
        user_id = session['userid']
        
        try:
            # Fetch the store_id and store name for the logged-in staff member
            cursor.execute("""
                SELECT s.store_id, st.store_name
                FROM staff s
                JOIN stores st ON s.store_id = st.store_id
                WHERE s.user_id = %s
                UNION
                SELECT l.store_id, st.store_name
                FROM local_manager l
                JOIN stores st ON l.store_id = st.store_id
                WHERE l.user_id = %s
            """, (user_id, user_id))
            store_info = cursor.fetchone()
            store_name = store_info['store_name'] if store_info else 'Not Assigned'
            store_id = store_info['store_id'] if store_info else None
            
            if store_id:
                # Query today's returns
                sql_query = """
                SELECT r.rental_id, r.equipment_id, e.name AS equipment_name, 
                        r.start_date, r.end_date, r.status, co.first_name, co.family_name
                    FROM rentals r
                    JOIN equipment e ON r.equipment_id = e.equipment_id
                    JOIN user u ON r.user_id = u.user_id
                    LEFT JOIN customer co ON u.user_id = co.user_id
                    WHERE r.end_date = %s AND r.status IN ('Completed', 'Pending', 'Canceled');
                """
                cursor.execute(sql_query, (today,))  
                returns = cursor.fetchall()
            else:
                returns = []
            
        finally:
            cursor.close()
            conn.close()
        
        return render_template('staff_equipment_return.html', returns=returns, store_name=store_name, today=today)
    else:
        flash("You are not authorized to view this page.")
        return redirect(url_for('staff.dashboard'))
    

## Update Daily Returns ##
@staff_bp.route('/update_return_status', methods=['POST'])
@login_required
def update_return_status():
    rental_id = request.form.get('rental_id')
    new_status = request.form.get('new_status')

    if not rental_id or not new_status:
        return jsonify({'error': 'Missing rental ID or status'}), 400

    conn, cursor = db_cursor()
    try:
        cursor.execute("""
            UPDATE rentals
            SET status = %s
            WHERE rental_id = %s
        """, (new_status, rental_id))
        conn.commit()
        return jsonify({'success': True, 'message': 'Status updated successfully.'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e), 'message': 'Failed to update status.'}), 500
    finally:
        cursor.close()
        conn.close()
