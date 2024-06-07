from flask import current_app as app
from mysql.connector import Error as MySQLError
from flask import Blueprint,render_template, request, redirect, url_for, session, flash
import re
from . import hashing
from .utils import db_cursor, login_required
from datetime import datetime, date

admin_bp = Blueprint('admin', __name__, template_folder='templates/admin')


# admin dashboard
@admin_bp.route('/dashboard')
def dashboard():
    if 'loggedin' in session and session['role'] == 'admin':
        return render_template('admin_dashboard.html')
    return redirect(url_for('home.login'))


# to allow admin to view and edit profile
@admin_bp.route('/admin_profile', methods=['GET', 'POST'])
@login_required
def admin_profile():
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

        try:
            cursor.execute(
                'UPDATE admin_national_manager SET title = %s, first_name = %s, family_name = %s, phone_number = %s WHERE user_id = %s',
                (title, first_name, family_name, phone, session['userid'])
            )
            cursor.execute(
                'UPDATE user SET email = %s WHERE user_id = %s',
                (email, session['userid'])
            )
            flash('Your profile has been successfully updated!', 'success')
        except MySQLError as e:
            flash(f"An error occurred: {e}", 'danger')

    cursor.execute(
        'SELECT u.username, u.email, u.password_hash, u.role, a.title, a.first_name, a.family_name, a.phone_number '
        'FROM user u '
        'JOIN admin_national_manager a ON u.user_id = a.user_id '
        'WHERE u.user_id = %s',
        (session['userid'],)
    )
    data = cursor.fetchone()

    return render_template('admin_profile.html', data=data)


# to allow admin to change password
@admin_bp.route('/change_password', methods=['POST'])
@login_required
def change_password():
    if 'userid' not in session:
        flash("User ID not found in session. Please log in again.", 'danger')
        return redirect(url_for('login'))

    password = request.form['password']

    if re.search('[a-zA-Z]', password) is None or re.search('[0-9]', password) is None:
        flash("Password must contain at least one letter and one digit.", 'warning')
        return redirect(url_for('admin.admin_profile'))

    hashed_password = hashing.hash_value(password, salt='ava')
    conn, cursor = db_cursor()

    try:
        cursor.execute(
            'UPDATE user SET password_hash = %s WHERE user_id = %s',
            (hashed_password, session['userid'])
        )
        flash("Your password has been successfully updated.", 'success')
    except MySQLError as e:
        flash(f"An error occurred: {e}", 'danger')

    return redirect(url_for('admin.admin_profile'))


## Admin View All Staff and Managers ##
@admin_bp.route('/staff_management')
@login_required
def staff_management():
    if 'loggedin' in session and session['role'] == 'admin':
        conn, cursor = db_cursor()
        
        try:
            cursor.execute("""
                SELECT s.staff_id, s.user_id, s.store_id, s.title, s.first_name, s.family_name, s.phone_number, 
                u.email, s.status, 'Staff' as role, st.store_name
                FROM staff s
                JOIN user u ON s.user_id = u.user_id
                JOIN stores st ON s.store_id = st.store_id
                UNION ALL
                SELECT l.local_manager_id as staff_id, l.user_id, l.store_id, l.title, l.first_name, l.family_name, 
                l.phone_number, u.email, l.status, 'Local Manager' as role, st.store_name
                FROM local_manager l
                JOIN user u ON l.user_id = u.user_id
                JOIN stores st ON l.store_id = st.store_id
                UNION ALL
                SELECT a.admin_manager_id as staff_id, a.user_id, NULL as store_id, a.title, a.first_name, a.family_name, 
                a.phone_number, u.email, a.status, a.role as role, 'N/A' as store_name
                FROM admin_national_manager a
                JOIN user u ON a.user_id = u.user_id
            """)
            staff = cursor.fetchall()
        
        except Exception as e:
            print("An error occurred:", e)
            flash("A database error occurred. Please try again.")
            return redirect(url_for('admin.dashboard'))
        finally:
            cursor.close()
            conn.close()
            
        return render_template('admin_view_staff.html', staff=staff)
    else:
        return redirect(url_for('home.login'))
    

