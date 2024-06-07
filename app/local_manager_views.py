from flask import current_app as app
from mysql.connector import Error as MySQLError
from flask import Blueprint,render_template, request, redirect, url_for, session, flash, jsonify,Flask
from app import utils
import re
from datetime import datetime, date
from .utils import db_cursor
from flask_hashing  import Hashing
from . import hashing
from .utils import db_cursor, login_required

local_manager_bp = Blueprint('local_manager', __name__, template_folder='templates/local_manager')


# local manager dashboard
@local_manager_bp.route('/dashboard')
def dashboard():
    if 'loggedin' in session and (session ['role'] == 'local_manager' or session['role'] == 'admin'):
        conn, cursor = db_cursor()
        user_id = session['userid']
        
        try:
            
            # Fetch the store_id and store name for the logged-in local manager
            cursor.execute("""
                SELECT s.store_id, st.store_name
                FROM local_manager s
                JOIN stores st ON s.store_id = st.store_id
                WHERE s.user_id = %s
            """, (user_id,))
            store_info = cursor.fetchone()
            store_name = store_info['store_name'] if store_info else 'Not Assigned'

         
            
        except Exception as e:
            print("An error occurred:", e)
            flash("A database error occurred. Please try again.")
            return redirect(url_for('home.login'))
        finally:
            cursor.close()
            conn.close()  

        return render_template('local_manager_dashboard.html', store_name=store_name)
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
        user_id = session['userid']
        
        try:
            
            # Fetch the store_id and store name for the logged-in local manager
            cursor.execute("""
                SELECT s.store_id, st.store_name
                FROM local_manager l
                JOIN stores st ON l.store_id = st.store_id
                WHERE l.user_id = %s
            """, (user_id,))
            store_info = cursor.fetchone()
            store_name = store_info['store_name'] if store_info else 'Not Assigned'
            store_id = store_info['store_id'] if store_info else None
            
            cursor.execute("""
                SELECT r.*, c.first_name, c.family_name, e.name as equipment_name, 
                r.start_date, r.end_date, r.status
                FROM rentals r
                JOIN customer c ON r.user_id = c.user_id
                JOIN equipment e ON r.equipment_id = e.equipment_id
                WHERE e.store_id = %s
            """, (store_id,))
            rentals = cursor.fetchall()
            
        except Exception as e:
            print("An error occurred:", e)
            flash("A database error occurred. Please try again.")
            return redirect(url_for('home.login'))
        finally:
            cursor.close()
            conn.close()
            
        return render_template('rentals_list.html', rentals=rentals, store_name=store_name)
    else:
        return redirect(url_for('local_manager.dashboard'))


## View Orders ##
@local_manager_bp.route('/orders')
def view_orders():
    if 'loggedin' in session and session['role'] == 'local_manager':
        conn, cursor = db_cursor()  
        user_id = session['userid']
        
        try:
            
            # Fetch the store_id and store name for the logged-in local manager
            cursor.execute("""
                SELECT s.store_id, st.store_name
                FROM local_manager s
                JOIN stores st ON s.store_id = st.store_id
                WHERE s.user_id = %s
            """, (user_id,))
            store_info = cursor.fetchone()
            store_name = store_info['store_name'] if store_info else 'Not Assigned'
            store_id = store_info['store_id'] if store_info else None
            
            cursor.execute("""
                SELECT o.order_id, c.first_name, c.family_name, o.store_id, o.total_cost, 
                       o.tax, o.discount, o.final_price, o.status, o.creation_date
                FROM orders o
                JOIN customer c ON o.user_id = c.user_id
                WHERE o.store_id = %s
            """, (store_id,))
            orders = cursor.fetchall()
            
        except Exception as e:
            print("An error occurred:", e)
            flash("A database error occurred. Please try again.")
            return redirect(url_for('home.login'))
        finally:
            cursor.close()
            conn.close()  
            
        return render_template('order_list.html', orders=orders, store_name=store_name)
    else:
        return redirect(url_for('local_manager.dashboard'))


## View Payments ##
@local_manager_bp.route('/payment')
def view_payments():
    if 'loggedin' in session and session['role'] == 'local_manager':
        conn, cursor = db_cursor()  
        user_id = session['userid']
        
        try:
        
            # Fetch the store_id and store name for the logged-in local manager
            cursor.execute("""
                SELECT s.store_id, st.store_name
                FROM local_manager s
                JOIN stores st ON s.store_id = st.store_id
                WHERE s.user_id = %s
            """, (user_id,))
            store_info = cursor.fetchone()
            store_name = store_info['store_name'] if store_info else 'Not Assigned'
            store_id = store_info['store_id'] if store_info else None
            
            cursor.execute("""
                SELECT p.payment_id, p.order_id, p.user_id, p.payment_type, p.payment_status, p.amount, p.payment_date
                FROM payments p
                JOIN orders o ON p.order_id = o.order_id
                WHERE o.store_id = %s
                ORDER BY p.payment_date DESC
            """, (store_id,))
            payments = cursor.fetchall()
        
        except Exception as e:
            print("An error occurred:", e)
            flash("A database error occurred. Please try again.")
            return redirect(url_for('home.login'))
        finally:
            cursor.close()
            conn.close()  
        
        return render_template('payments.html', payments=payments, store_name=store_name)
    else:
        return redirect(url_for('local_manager.dashboard'))


## View Promotions ##
@local_manager_bp.route('/promotions')
def view_promotions(): #news
    if 'loggedin' in session and session['role'] == 'local_manager':
        conn, cursor = db_cursor() 
        user_id = session['userid']
         
        try:
            
            # Fetch the store_id and store name for the logged-in local manager
            cursor.execute("""
                SELECT s.store_id, st.store_name
                FROM local_manager s
                JOIN stores st ON s.store_id = st.store_id
                WHERE s.user_id = %s
            """, (user_id,))
            store_info = cursor.fetchone()
            store_name = store_info['store_name'] if store_info else 'Not Assigned'
            store_id = store_info['store_id'] if store_info else None
            
            cursor.execute("""
                SELECT promotion_id, title, description, start_date, end_date, creator_id, store_id
                FROM promotions
                WHERE store_id = %s
                ORDER BY start_date DESC
            """, (store_id,))
            promotions = cursor.fetchall()
        
        except Exception as e:
            print("An error occurred:", e)
            flash("A database error occurred. Please try again.")
            return redirect(url_for('home.login'))
        finally:
            cursor.close()
            conn.close()  
            
        return render_template('promotions.html', promotions=promotions, store_name=store_name)
    else:
        return redirect(url_for('local_manager.dashboard'))
    



## Inventory ##
@local_manager_bp.route('/equipment')
def view_inventory():
    if 'loggedin' in session and session['role'] == 'local_manager':
        conn, cursor = db_cursor()  
        user_id = session['userid']
        
        try:
            
            # Fetch the store_id and store name for the logged-in local manager
            cursor.execute("""
                SELECT s.store_id, st.store_name
                FROM local_manager s
                JOIN stores st ON s.store_id = st.store_id
                WHERE s.user_id = %s
            """, (user_id,))
            store_info = cursor.fetchone()
            store_name = store_info['store_name'] if store_info else 'Not Assigned'
            store_id = store_info['store_id'] if store_info else None
            
            cursor.execute("""
                SELECT equipment_id, name, category, purchase_date, cost, 
                serial_number, status, store_id, maximum_date, minimum_date 
                FROM equipment
                WHERE store_id = %s
            """, (store_id,))
            equipment = cursor.fetchall()
            
        except Exception as e:
            print("An error occurred:", e)
            flash("A database error occurred. Please try again.")
            return redirect(url_for('local_manager.dashboard'))
        finally:
            cursor.close()
            conn.close()  
            
        return render_template('equipment.html', equipment=equipment, store_name=store_name)
    else:
        return redirect(url_for('local_manager.dashboard'))


## Daily Checklist ## 
@local_manager_bp.route('/daily_checklist')
@login_required
def daily_checklist():
    if 'loggedin' in session and session['role'] == 'local_manager':
        today = date.today().strftime('%Y-%m-%d')
        print("Today's date:", today)
        
        conn, cursor = db_cursor()
        try:
            # Query today's bookings
            sql_query = """
               SELECT r.rental_id, r.user_id, r.equipment_id, e.name AS equipment_name, 
                    r.start_date, r.end_date, r.status, u.username
                FROM rentals r
                JOIN equipment e ON r.equipment_id = e.equipment_id
                JOIN user u ON r.user_id = u.user_id
                WHERE r.start_date = %s AND r.status IN ('Completed', 'Pending', 'Canceled');
            """
            print("Date for query:", today)
            cursor.execute(sql_query, (today,))
            bookings = cursor.fetchall()
            print("Number of bookings fetched:", len(bookings))
        except Exception as e:
            print("An error occurred:", e)
            flash("A database error occurred. Please try again.")
            return redirect(url_for('local_manager.dashboard'))
        finally:
            cursor.close()
            conn.close()
        
        return render_template('local_manager_daily_checklist.html', bookings=bookings)
    else:
        flash("You are not authorized to view this page.")
        return redirect(url_for('local_manager.dashboard'))





## Local Manager View Reports ##
@local_manager_bp.route('/view_reports', methods=['GET'])
@login_required
def view_reports():
    if 'loggedin' in session and session['role'] == 'local_manager':
        conn, cursor = db_cursor()
        user_id = session['userid']
        
        try:
            # Fetch the store_id and store name for the logged-in local manager
            cursor.execute("""
                SELECT s.store_id, st.store_name
                FROM local_manager s
                JOIN stores st ON s.store_id = st.store_id
                WHERE s.user_id = %s
            """, (user_id,))
            store_info = cursor.fetchone()
            store_name = store_info['store_name'] if store_info else 'Not Assigned'
            store_id = store_info['store_id'] if store_info else None
            
            cursor.execute("""
                SELECT r.report_id, r.title, r.content, r.creation_date, r.store_id, r.document_link
                FROM reports r
                WHERE r.store_id = %s
            """, (store_id,))
            reports = cursor.fetchall()
        
        except Exception as e:
            print("An error occurred:", e)
            flash("A database error occurred. Please try again.")
            return redirect(url_for('local_manager.dashboard'))
        finally:
            cursor.close()
            conn.close()
            
        return render_template('local_manager_view_reports.html', reports=reports, store_name=store_name)
    else:
        return redirect(url_for('local_manager_dashboard'))



## View Report Details ##
@local_manager_bp.route('/view_report/<int:report_id>', methods=['GET'])
@login_required
def view_report(report_id):
    if 'loggedin' in session and session['role'] == 'local_manager':
        conn, cursor = db_cursor()
        
        try:
            cursor.execute("""
                SELECT r.report_id, r.title, r.content, r.creation_date, r.document_link, s.store_name
                FROM reports r
                JOIN stores s ON r.store_id = s.store_id
                WHERE r.report_id = %s
            """, (report_id,))
            report = cursor.fetchone()
            
            if not report:
                flash("Report not found.", 'danger')
                return redirect(url_for('local_manager.view_reports'))
        
        except Exception as e:
            print("An error occurred:", e)
            flash("A database error occurred. Please try again.")
            return redirect(url_for('local_manager.view_reports'))
        finally:
            cursor.close()
            conn.close()
        
        return render_template('local_manager_report_details.html', report=report)
    else:
        return redirect(url_for('local_manager.dashboard'))



## View Staff ##
@local_manager_bp.route('/staff')
def view_staff():
    if 'loggedin' in session and session['role'] in ['local_manager', 'national_manager']:
        conn, cursor = db_cursor()
        user_id = session['userid']
        
        try:
            # Fetch the store_id and store name for the logged-in local manager or national manager
            if session['role'] == 'local_manager':
                cursor.execute("""
                    SELECT s.store_id, st.store_name
                    FROM local_manager s
                    JOIN stores st ON s.store_id = st.store_id
                    WHERE s.user_id = %s
                """, (user_id,))
                store_info = cursor.fetchone()
                store_name = store_info['store_name'] if store_info else 'Not Assigned'
                store_id = store_info['store_id'] if store_info else None
                
                cursor.execute("""
                    SELECT s.staff_id, s.user_id, s.store_id, s.title, s.first_name, s.family_name, s.phone_number, s.status, u.email
                    FROM staff s
                    JOIN user u ON s.user_id = u.user_id
                    WHERE s.store_id = %s
                """, (store_id,))
                staff = cursor.fetchall()
                
            else:
                # National Manager: Fetch all staff from all stores
                cursor.execute("""
                    SELECT s.staff_id, s.user_id, s.store_id, s.title, s.first_name, s.family_name, s.phone_number, s.status, u.email, st.store_name
                    FROM staff s
                    JOIN user u ON s.user_id = u.user_id
                    JOIN stores st ON s.store_id = st.store_id
                """)
                staff = cursor.fetchall()
                store_name = 'All Stores'
        
        except Exception as e:
            print("An error occurred:", e)
            flash("A database error occurred. Please try again.")
            return redirect(url_for('local_manager.dashboard'))
        finally:
            cursor.close()
            conn.close()
            
        return render_template('local_manager_view_staff.html', staff=staff, store_name=store_name)
    else:
        return redirect(url_for('local_manager.dashboard'))


## Update Staff ##
@local_manager_bp.route('/update_staff/<int:staff_id>', methods=['GET', 'POST'])
def update_staff(staff_id):
    if 'loggedin' in session and session['role'] in ['local_manager', 'national_manager']:
        conn, cursor = db_cursor()
        
        if request.method == 'POST':
            title = request.form['title']
            first_name = request.form['first_name']
            family_name = request.form['family_name']
            phone_number = request.form['phone_number']
            status = request.form['status']
            
            try:
                cursor.execute("""
                    UPDATE staff s
                    JOIN user u ON s.user_id = u.user_id
                    SET s.title = %s, s.first_name = %s, s.family_name = %s, s.phone_number = %s, s.status = %s
                    WHERE s.staff_id = %s
                """, (title, first_name, family_name, phone_number, status, staff_id))
                conn.commit()
                flash('Staff updated successfully!', 'success')
                return redirect(url_for('local_manager.view_staff'))
            except MySQLError as e:
                print("An error occurred:", e)
                flash("A database error occurred. Please try again.")
            finally:
                cursor.close()
                conn.close()
        
        else:
            cursor.execute("""
                SELECT s.staff_id, s.user_id, s.title, s.first_name, s.family_name, s.phone_number, u.email, s.status
                FROM staff s
                JOIN user u ON s.user_id = u.user_id
                WHERE s.staff_id = %s
            """, (staff_id,))
            staff = cursor.fetchone()
            
            if not staff:
                flash("Staff not found.", 'danger')
                return redirect(url_for('local_manager.view_staff'))
            
            return render_template('local_manager_update_staff.html', staff=staff)
    else:
        return redirect(url_for('home.login'))

@local_manager_bp.route('/view_news')
@login_required
def view_news():
    if 'loggedin' in session and session['role'] in ['local_manager']:
        conn, cursor = db_cursor()
        cursor.execute("""
            SELECT news_id, title, content, publish_date, creator_id, store_id
            FROM news
            ORDER BY publish_date DESC
        """)
        news_items = cursor.fetchall()
        cursor.close()
        return render_template('local_manager_view_news.html', news_items=news_items)
    else:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('home.login'))

@local_manager_bp.route('/edit_news/<int:news_id>', methods=['GET'])
@login_required
def edit_news(news_id):
    if 'loggedin' in session and session['role'] in ['local_manager', 'admin']:
        conn, cursor = db_cursor()
        cursor.execute("SELECT news_id, title, content FROM news WHERE news_id = %s", (news_id,))
        news_item = cursor.fetchone()
        cursor.close()
        if news_item:
            return render_template('local_manager_edit_news.html', news_item=news_item)
        else:
            flash('News item not found.', 'warning')
            return redirect(url_for('local_manager.view_news'))
    else:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('home.login'))

@local_manager_bp.route('/update_news/<int:news_id>', methods=['POST'])
@login_required
def update_news(news_id):
    if 'loggedin' in session and session['role'] in ['local_manager', 'admin']:
        title = request.form['title']
        content = request.form['content']
        
        conn, cursor = db_cursor()
        try:
            cursor.execute("UPDATE news SET title = %s, content = %s WHERE news_id = %s",
                           (title, content, news_id))
            conn.commit()
            flash('News updated successfully.', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Failed to update news: {str(e)}', 'danger')
        finally:
            cursor.close()
        return redirect(url_for('local_manager.view_news'))
    else:
        flash('Unauthorized to perform this action.', 'danger')
        return redirect(url_for('home.login'))

@local_manager_bp.route('/delete_news/<int:news_id>', methods=['POST'])
@login_required
def delete_news(news_id):
    if 'loggedin' in session and session['role'] in ['local_manager', 'admin']:
        conn, cursor = db_cursor()
        try:
            cursor.execute("DELETE FROM news WHERE news_id = %s", (news_id,))
            conn.commit()
            flash('News deleted successfully.', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Failed to delete news: {str(e)}', 'danger')
        finally:
            cursor.close()
        return redirect(url_for('local_manager.view_news'))
    else:
        flash('Unauthorized to perform this action.', 'danger')
        return redirect(url_for('home.login'))



from datetime import datetime

@local_manager_bp.route('/add_news', methods=['GET'])
@login_required
def add_news_form():
    if 'loggedin' in session and session['role'] == 'local_manager':
        
        today = datetime.today().strftime('%Y-%m-%d')  
        return render_template('local_manager_add_news.html', today=today)
    else:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('home.login'))

@local_manager_bp.route('/add_news', methods=['POST'])
@login_required
def add_news():
    if 'loggedin' in session and session['role'] == 'local_manager':
        title = request.form['title']
        content = request.form['content']
        publish_date = request.form['publish_date']
        creator_id = request.form['creator_id']
        store_id = request.form['store_id']

        conn, cursor = db_cursor()
        try:
            # 包括 publish_date、creator_id 和 store_id
            cursor.execute("INSERT INTO news (title, content, publish_date, creator_id, store_id) VALUES (%s, %s, %s, %s, %s)", 
                           (title, content, publish_date, creator_id, store_id))
            conn.commit()
            flash('News added successfully.', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Failed to add news: {str(e)}', 'danger')
        finally:
            cursor.close()
        return redirect(url_for('local_manager.view_news'))
    else:
        flash('Unauthorized to perform this action.', 'danger')
        return redirect(url_for('home.login'))


@local_manager_bp.route('/view_discount')
@login_required
def view_discount():
    if 'loggedin' in session and session['role'] in ['local_manager']:
        conn, cursor = db_cursor()
        # Update the SQL query to include ORDER BY
        cursor.execute("SELECT * FROM discount ORDER BY days ASC")
        discounts = cursor.fetchall()
        cursor.close()
        return render_template('local_manager/local_manager_discount.html', discounts=discounts)
    return redirect(url_for('home.login'))

 # Redirect if the user is not logged in or not authorized
@local_manager_bp.route('/edit_discount/<int:discount_id>')
@login_required
def edit_discount(discount_id):
    if 'loggedin' in session and session['role'] == 'local_manager':
        conn, cursor = db_cursor()
        cursor.execute("SELECT * FROM discount WHERE discount_id = %s", (discount_id,))
        discount = cursor.fetchone()
        cursor.close()
        if discount:
            return render_template('local_manager_edit_discount.html', discount=discount)
        else:
            flash("Discount not found.")
            return redirect(url_for('local_manager.view_discount'))
    return redirect(url_for('home.login'))

@local_manager_bp.route('/update_discount/<int:discount_id>', methods=['POST'])
@login_required
def update_discount(discount_id):
    if 'loggedin' in session and session['role'] == 'local_manager':
        days = request.form['days']
        discount_pricing = float(request.form['discount_pricing']) / 100  # Convert percentage to decimal

        conn, cursor = db_cursor()
        cursor.execute("UPDATE discount SET days = %s, discount_pricing = %s WHERE discount_id = %s",
                       (days, discount_pricing, discount_id))
        conn.commit()
        cursor.close()
        
        flash('Discount updated successfully.', 'success')
        return redirect(url_for('local_manager.view_discount'))
    return redirect(url_for('home.login'))

@local_manager_bp.route('/delete_discount/<int:discount_id>', methods=['POST'])
@login_required
def delete_discount(discount_id):
    if 'loggedin' in session and session['role'] == 'local_manager':
        conn, cursor = db_cursor()  # Ensure you obtain a connection and a cursor
        try:
            cursor.execute("DELETE FROM discount WHERE discount_id = %s", (discount_id,))
            conn.commit()
            flash('Discount deleted successfully.', 'success')
        except Exception as e:
            conn.rollback()  # Important to rollback if there's an error
            flash(f'Failed to delete discount due to: {str(e)}', 'danger')
        finally:
            cursor.close()
        return redirect(url_for('local_manager.view_discount'))
    else:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('home.login'))
   
@local_manager_bp.route('/add_discount', methods=['GET'])
@login_required
def add_discount_form():
    if 'loggedin' in session and session['role'] == 'local_manager':
        # Render a form to input new discount details
        return render_template('local_manager_add_discount.html')
    else:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('home.login'))


@local_manager_bp.route('/add_discount', methods=['POST'])
@login_required
def add_discount():
    if 'loggedin' in session and session['role'] == 'local_manager':
        days = request.form['days']
        # Convert percentage input to a decimal for storage
        discount_pricing = float(request.form['discount_pricing']) / 100
        
        conn, cursor = db_cursor()
        try:
            cursor.execute("INSERT INTO discount (days, discount_pricing) VALUES (%s, %s)", (days, discount_pricing))
            conn.commit()
            flash('Discount added successfully.', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Failed to add discount: {str(e)}', 'danger')
        finally:
            cursor.close()
        
        return redirect(url_for('local_manager.view_discount'))
    else:
        flash('Unauthorized to perform this action.', 'danger')
        return redirect(url_for('home.login'))
