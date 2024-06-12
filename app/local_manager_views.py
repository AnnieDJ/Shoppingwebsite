import json, os
import sys
import uuid
from flask import current_app as app
from mysql.connector import Error as MySQLError
from flask import Blueprint,render_template, request, redirect, url_for, session, flash, jsonify
from app import utils
import re
from datetime import datetime, date
from .utils import db_cursor, login_required
from flask_hashing  import Hashing


local_manager_bp = Blueprint('local_manager', __name__, template_folder='templates/local_manager')


# local manager dashboard
@local_manager_bp.route('/dashboard')
def dashboard():
    if 'loggedin' in session and session['role'] == 'local_manager':
        today = date.today().isoformat()
        conn, cursor = db_cursor()
        cursor.execute(f'SELECT store_id FROM local_manager WHERE user_id = {session["userid"]}')
        store_id = cursor.fetchone()['store_id']
        cursor.execute('''
                       SELECT oi.order_id, oi.equipment_id, e.name as equipment_name, oi.start_time, o.user_id
                       FROM order_items oi
                       JOIN equipment e ON oi.equipment_id = e.equipment_id
                       JOIN orders o ON oi.order_id = o.order_id
                       JOIN user u ON o.user_id = u.user_id
                       WHERE oi.start_time = %s AND e.store_id = %s AND o.status = 'Pending'
                       ''', (today, store_id))
        start_today = cursor.fetchall()
            
        cursor.execute('''
                       SELECT oi.order_id, oi.equipment_id, e.name as equipment_name, oi.end_time, u.user_id
                       FROM order_items oi
                       JOIN equipment e ON oi.equipment_id = e.equipment_id
                       JOIN orders o ON oi.order_id = o.order_id
                       JOIN user u ON o.user_id = u.user_id
                       WHERE oi.end_time = %s AND e.store_id = %s AND o.status = 'Ongoing'
                       ''', (today, store_id))
        end_today = cursor.fetchall()
        conn.close()
        return render_template('local_manager_dashboard.html', start_today=start_today, end_today=end_today)
    return redirect(url_for('home.login'))
    

##Local Manager Profile ## 
@local_manager_bp.route('/local_manager_profile', methods=['GET', 'POST'])
def view_profile():
    if 'loggedin' in session and session['role'] == 'local_manager':
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

    # Check for at least one letter, one digit, one uppercase and lowercase letter, and minimum 8 characters
    pattern = re.compile(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$')

    if not pattern.match(password):
        flash("Password must contain at least one number and one uppercase and lowercase letter, and at least 8 or more characters.", 'warning')
        return redirect(url_for('national_manager.national_manager_profile'))

    hashed_password = hashing.hash_value(password, salt='ava')
    conn, cursor = db_cursor()

    try:
        cursor.execute(
            'UPDATE user SET password_hash = %s WHERE user_id = %s',
            (hashed_password, session['userid'])
        )
        conn.commit()  # Ensure the changes are committed to the database
        flash("Your password has been successfully updated.", 'success')
    except MySQLError as e:
        flash(f"An error occurred: {e}", 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('local_manager.local_manager_profile'))


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
@local_manager_bp.route('/view_staff')
@login_required
def view_staff():
    if 'loggedin' in session and session['role'] in ['local_manager']:
        conn, cursor = db_cursor()
        cursor.execute("""
            SELECT
                u.user_id,
                u.username,
                u.email,
                s.title,
                CONCAT(s.first_name, ' ', s.family_name) AS full_name,
                s.phone_number,
                s.store_id
            FROM
                user u
            JOIN
                staff s ON u.user_id = s.user_id
            WHERE
                u.role = 'staff'
            ORDER BY
                s.first_name, s.family_name
        """)
        staff_members = cursor.fetchall()
        cursor.close()
        return render_template('local_manager_view_staff.html', staff_members=staff_members)
    else:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('home.login'))


@local_manager_bp.route('/edit_staff/<int:user_id>', methods=['GET'])
@login_required
def edit_staff(user_id):
    if 'loggedin' in session and session['role'] in ['local_manager']:
        conn, cursor = db_cursor()
        cursor.execute("""
            SELECT u.user_id, s.title, s.phone_number, u.email, s.store_id
            FROM user u
            JOIN staff s ON u.user_id = s.user_id
            WHERE u.user_id = %s
        """, (user_id,))
        staff_member = cursor.fetchone()
        cursor.close()
        if staff_member:
            return render_template('local_manager_edit_staff.html', staff_member=staff_member)
        else:
            flash('Staff member not found.', 'warning')
            return redirect(url_for('local_manager.local_manager_view_staff'))
    else:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('home.login'))


@local_manager_bp.route('/update_staff/<int:user_id>', methods=['POST'])
@login_required
def update_staff(user_id):
    if 'loggedin' in session and session['role'] in ['local_manager']:
        title = request.form['title']
        phone_number = request.form['phone_number']
        email = request.form['email']
        store_id = request.form['store_id']

        conn, cursor = db_cursor()
        try:
            cursor.execute("""
                UPDATE staff s JOIN user u ON s.user_id = u.user_id
                SET s.title = %s, s.phone_number = %s, u.email = %s, s.store_id = %s
                WHERE s.user_id = %s
            """, (title, phone_number, email, store_id, user_id))
            conn.commit()
            flash('Staff member updated successfully.', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Failed to update staff member: {str(e)}', 'danger')
        finally:
            cursor.close()
        return redirect(url_for('local_manager.view_staff'))
    else:
        flash('Unauthorized to perform this action.', 'danger')
        return redirect(url_for('home.login'))


@local_manager_bp.route('/delete_staff/<int:user_id>', methods=['POST'])
@login_required
def delete_staff(user_id):
    if 'loggedin' in session and session['role'] in ['local_manager']:
        conn, cursor = db_cursor()
        try:
            cursor.execute("DELETE FROM staff WHERE user_id = %s", (user_id,))
            conn.commit()
            flash('Staff member deleted successfully.', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Failed to delete staff member: {str(e)}', 'danger')
        finally:
            cursor.close()
        return redirect(url_for('local_manager.view_staff'))
    else:
        flash('Unauthorized to perform this action.', 'danger')
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


# Add discount
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


# View store financial report
@local_manager_bp.route('/financial_report')
@login_required
def financial_report():
    if 'loggedin' in session:
        conn, cursor = db_cursor()
        try:
            cursor.execute(f"""
                SELECT
                  CASE
                    WHEN MONTH(creation_date) BETWEEN 1 AND 3 THEN 'January-March'
                    WHEN MONTH(creation_date) BETWEEN 1 AND 6 THEN 'April-June'
                    WHEN MONTH(creation_date) BETWEEN 1 AND 9 THEN 'Junly-September'
                    WHEN MONTH(creation_date) BETWEEN 1 AND 12 THEN 'October-December'
                  END AS quarter,
                  SUM(total_cost) AS total_sales
                FROM orders
                WHERE status = 'Completed' AND YEAR(creation_date) = 2024 AND 
                store_id = (SELECT store_id FROM local_manager WHERE user_id = {session['userid']})
                GROUP BY quarter
            """)
            results = cursor.fetchall()
            data = [{'quarter': result['quarter'], 'total_sales': float(result['total_sales'])} for result in results]
        except Exception as e:
            flash(f'Failed to retrieve data: {str(e)}', 'danger')
            data = []
        finally:
            cursor.close()
            conn.close()

        return render_template('local_manager_report.html', data=data)
    else:
        flash('Please log in to view this page.', 'info')
        return redirect(url_for('home.login'))


# Inventory management
@local_manager_bp.route('/inventory_management')
def inventory_management():
    if 'loggedin' in session and session['role'] == 'local_manager':
        conn, cursor = db_cursor()
        category = []
        cursor.execute(f'SELECT store_id FROM local_manager WHERE user_id = {session["userid"]}')
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
        return render_template('local_manager_inventory_management.html', category=category)
    return redirect(url_for('home.login'))


# View equipment details
@local_manager_bp.route('/equipment/detail')
def equipment_detail():
    if 'loggedin' in session and session['role'] == 'local_manager':
        category = request.args.get('category')
        conn, cursor = db_cursor()
        cursor.execute(f"SELECT * FROM equipment WHERE category = '{category}'")
        equipment = cursor.fetchall()
        cursor.close()
        return render_template('local_manager_equipment_detail.html', equipment=equipment, categories=all_category())
    return redirect(url_for('home.login'))


# Update equipment details
@local_manager_bp.route('/equipment/update', methods=['POST'])
def equipment_update():
    if 'loggedin' in session and session['role'] == 'local_manager':
        serial_number = request.form['serial_number']
        Image = request.form['Image']
        purchase_date = request.form['purchase_date']
        cost = request.form['cost']
        category = request.form['category']
        status = request.form['status']
        conn, cursor = db_cursor()
        cursor.execute(F"SELECT status, equipment_id FROM equipment WHERE serial_number = '{serial_number}'")
        data = cursor.fetchone()
        old_status = data['status']
        equipment_id = data['equipment_id']
        cursor.execute(f"SELECT store_id FROM local_manager WHERE user_id = '{session['userid']}'")
        store_id = cursor.fetchone()['store_id']
        if old_status == 'Available' and status == 'Under Repair':
            cursor.execute(f"INSERT INTO equipment_repair_history (equipment_id, store_id, status_from, status_to, change_date) VALUES ('{equipment_id}', '{store_id}', 'Available', 'Under Repair', '{datetime.strftime(datetime.now(), '%Y-%m-%d')}')")
            conn.commit()
        elif old_status == 'Under Repair' and status == 'Available':
            cursor.execute(f"INSERT INTO equipment_repair_history (equipment_id, store_id, status_from, status_to, change_date) VALUES ('{equipment_id}', '{store_id}', 'Under Repair', 'Available', '{datetime.strftime(datetime.now(), '%Y-%m-%d')}')")
            conn.commit()
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
@local_manager_bp.route('/equipment/add', methods=['POST'])
def equipment_add():
    if 'loggedin' in session and session['role'] == 'local_manager':
        serial_number = request.form['serial_number']
        name = request.form['name']
        description = request.form['description']
        Image = request.form['Image']
        purchase_date = request.form['purchase_date']
        cost = request.form['cost']
        category = request.form['category']
        status = request.form['status']
        conn, cursor = db_cursor()
        cursor.execute(f'SELECT store_id FROM local_manager WHERE user_id = {session["userid"]}')
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
@local_manager_bp.route('/equipment/upload', methods=['POST'])
def equipment_upload():
    if 'loggedin' in session and session['role'] == 'local_manager':
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


# View all orders at store
@local_manager_bp.route('/order_list')
def order_list():
    if 'loggedin' in session and session['role'] == 'local_manager':
        status = request.args.get('status')
        search = request.args.get('search')
        conn, cursor = db_cursor()
        cursor.execute(f"SELECT store_id FROM local_manager WHERE user_id = {session['userid']}")
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
            cursor.execute(f"SELECT username, email, date_of_birth, first_name, family_name FROM user JOIN customer ON user.user_id = customer.user_id WHERE user.user_id = {order['user_id']}")
            order['user_info'] = cursor.fetchone()
        cursor.close()
        return render_template('local_manager_order_list.html', orders=orders)
    return redirect(url_for('home.login'))


# View order details
@local_manager_bp.route('/order_detail/<int:order_id>')
def order_detail(order_id):
    if 'loggedin' in session and session['role'] == 'local_manager':
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
        return render_template('local_manager_order_detail.html', items=items, order_id=order_id)
    return redirect(url_for('home.login'))


# Return equipment
@local_manager_bp.route('/equipment/return', methods=['POST'])
def return_equipment():
    if 'loggedin' in session and session['role'] == 'local_manager':
        order_id = request.form['order_id']
        equipment_id = request.form['equipment_id']
        conn, cursor = db_cursor()
        cursor.execute(f"SELECT store_id FROM orders WHERE order_id = {order_id}")
        store_id = cursor.fetchone()['store_id']
        cursor.execute(f"UPDATE equipment SET status = 'Available' WHERE equipment_id = {equipment_id}")
        conn.commit()
        cursor.execute(f"INSERT INTO equipment_rental_history (equipment_id, store_id, status_from, status_to, change_date) VALUES ({equipment_id}, {store_id}, 'Rented', 'Available', '{datetime.strftime(datetime.now(), '%Y-%m-%d')}')")
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


@local_manager_bp.route('/fetch_order/<int:order_id>')
def fetch_order(order_id):
    if 'loggedin' in session and session['role'] == 'local_manager':
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


# Cancel and refund order
@local_manager_bp.route('/refund_order/<int:order_id>')
def refund_order(order_id):
    if 'loggedin' in session and session['role'] == 'local_manager':
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


# Send reminder
@local_manager_bp.route('/send_reminder', methods=['POST'])
def send_reminder():
    data = request.json
    order_id = data.get('order_id')
    user_id = data.get('user_id')
    equipment_name = data.get('equipment_name')
    message = data.get('message')
    sender_id = session['userid']

    content = message

    conn, cursor = db_cursor()
    cursor.execute('INSERT INTO reminders (user_id, sender_id, content) VALUES (%s, %s, %s)', (user_id, sender_id, content))
    conn.close()

    return jsonify({'message': 'Reminder sent successfully.'}), 200


@local_manager_bp.route('/damage_report')
def damage_report():
    if 'loggedin' in session and session['role'] == 'local_manager':
        conn, cursor = db_cursor()
        cursor.execute("SELECT count(*) FROM equipment_repair_history WHERE status_from = 'Available' AND status_to = 'Under Repair'")
        atou = cursor.fetchone()['count(*)']
        cursor.execute("SELECT count(*) FROM equipment_repair_history WHERE status_from = 'Under Repair' AND status_to = 'Available'")
        utoa = cursor.fetchone()['count(*)']
        cursor.execute("SELECT count(*) FROM equipment_rental_history WHERE status_from = 'Available' AND status_to = 'Rented'")
        ator = cursor.fetchone()['count(*)']
        cursor.execute("SELECT count(*) FROM equipment_rental_history WHERE status_from = 'Rented' AND status_to = 'Available'")
        rtoa = cursor.fetchone()['count(*)']
        cursor.close()
        repair = atou if atou < utoa else utoa
        rental = ator if ator < rtoa else rtoa

        try:
            percent = f"{round(repair / rental * 100, 2)}%"
        except ZeroDivisionError:
            percent = '0%'

        report = {
            'repair': repair,
            'rental': rental,
            'percent': percent
        }
        return render_template('local_manager_report.html', report=report)
    return redirect(url_for('auth_bp.login'))


def all_category():
    conn, cursor = db_cursor()
    cursor.execute("SELECT category FROM equipment GROUP BY category")
    categories = cursor.fetchall()
    cursor.close()
    return categories