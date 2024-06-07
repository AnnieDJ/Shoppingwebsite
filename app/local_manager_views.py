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
