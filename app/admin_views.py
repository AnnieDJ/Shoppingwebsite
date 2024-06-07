from flask import current_app as app
from mysql.connector import Error as MySQLError
from flask import Blueprint,render_template, request, redirect, url_for, session, flash
import re
from . import hashing
from .utils import db_cursor, login_required
from datetime import datetime, date
import uuid

admin_bp = Blueprint('admin', __name__, template_folder='templates/admin')


# admin dashboard
@admin_bp.route('/dashboard')
@login_required
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
                SELECT u.user_id, u.username, u.email, u.role, 
                       COALESCE(s.title, l.title, a.title) AS title, 
                       COALESCE(s.first_name, l.first_name, a.first_name) AS first_name, 
                       COALESCE(s.family_name, l.family_name, a.family_name) AS family_name, 
                       COALESCE(s.phone_number, l.phone_number, a.phone_number) AS phone_number, 
                       COALESCE(s.status, l.status, 'active') AS status, 
                       COALESCE(st.store_name, 'N/A') AS store_name
                FROM user u
                LEFT JOIN staff s ON u.user_id = s.user_id
                LEFT JOIN local_manager l ON u.user_id = l.user_id
                LEFT JOIN admin_national_manager a ON u.user_id = a.user_id
                LEFT JOIN stores st ON u.store_id = st.store_id
                WHERE u.role IN ('staff', 'local_manager', 'national_manager')
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
    
    
# Update Staff and Location Managers ##
@admin_bp.route('/update_staff/<int:user_id>/<string:role>', methods=['GET', 'POST'])
@login_required
def update_staff(user_id, role):
    if 'loggedin' in session and session['role'] == 'admin':
        conn, cursor = db_cursor()
        
        if request.method == 'POST':
            title = request.form['title']
            first_name = request.form['first_name']
            family_name = request.form['family_name']
            email = request.form['email']
            phone_number = request.form['phone_number']
            status = request.form['status']
            store_id = request.form['store_id']
            role = request.form['role']
            
            try:
                cursor.execute("""
                    UPDATE user
                    SET email = %s, role = %s, store_id = %s
                    WHERE user_id = %s
                """, (email, role, store_id, user_id))
                
                if role == 'staff':
                    cursor.execute("""
                        UPDATE staff s
                        JOIN user u ON s.user_id = u.user_id
                        SET s.title = %s, s.first_name = %s, s.family_name = %s, s.phone_number = %s, s.status = %s, s.store_id = %s
                        WHERE u.user_id = %s
                    """, (title, first_name, family_name, phone_number, status, store_id, user_id))
                elif role == 'local_manager':
                    cursor.execute("""
                        UPDATE local_manager l
                        JOIN user u ON l.user_id = u.user_id
                        SET l.title = %s, l.first_name = %s, l.family_name = %s, l.phone_number = %s, l.status = %s, l.store_id = %s
                        WHERE u.user_id = %s
                    """, (title, first_name, family_name, phone_number, status, store_id, user_id))
                else:
                    cursor.execute("""
                        UPDATE admin_national_manager a
                        JOIN user u ON a.user_id = u.user_id
                        SET a.title = %s, a.first_name = %s, a.family_name = %s, a.phone_number = %s
                        WHERE u.user_id = %s
                    """, (title, first_name, family_name, phone_number, user_id))   
                conn.commit()
                flash('Updated successfully!', 'success')
                return redirect(url_for('admin.staff_management'))
            except MySQLError as e:
                print("An error occurred:", e)
                flash("A database error occurred. Please try again.")
            finally:
                cursor.close()
                conn.close()
        
        else:
            if role == 'staff':
                cursor.execute("""
                    SELECT u.user_id, u.username, u.email, u.role, s.title, s.first_name, s.family_name, s.phone_number, 
                    s.status, st.store_name, s.store_id
                    FROM user u
                    JOIN staff s ON u.user_id = s.user_id
                    LEFT JOIN stores st ON s.store_id = st.store_id
                    WHERE u.user_id = %s
                """, (user_id,))
            elif role == 'local_manager':
                cursor.execute("""
                    SELECT u.user_id, u.username, u.email, u.role, l.title, l.first_name, l.family_name, l.phone_number, 
                    l.status, st.store_name, l.store_id
                    FROM user u
                    JOIN local_manager l ON u.user_id = l.user_id
                    LEFT JOIN stores st ON l.store_id = st.store_id
                    WHERE u.user_id = %s
                """, (user_id,))
            else:
                cursor.execute("""
                    SELECT u.user_id, u.username, u.email, u.role, a.title, a.first_name, a.family_name, a.phone_number, 
                    'active' as status, 'N/A' as store_name, NULL as store_id
                    FROM user u
                    JOIN admin_national_manager a ON u.user_id = a.user_id
                    WHERE u.user_id = %s
                """, (user_id,))
            
            staff = cursor.fetchone()
            
            if not staff:
                flash("Not found.", 'danger')
                return redirect(url_for('admin.staff_management'))
            
            cursor.execute('SELECT store_id, store_name FROM stores')
            stores = cursor.fetchall()
            cursor.close()
            conn.close()
            
            return render_template('admin_update_staff.html', staff=staff, role=role, stores=stores)
    else:
        return redirect(url_for('home.login'))
    

## Delete Staff and Local Managers ##
@admin_bp.route('/delete_staff/<int:user_id>/<string:role>', methods=['GET', 'POST'])
@login_required
def delete_staff(user_id, role):
    if 'loggedin' in session and session['role'] == 'admin':
        conn, cursor = db_cursor()
        
        if request.method == 'POST':
            try:
                if role == 'staff':
                    cursor.execute("DELETE FROM staff WHERE user_id = %s", (user_id,))
                elif role == 'local_manager':
                    cursor.execute("DELETE FROM local_manager WHERE user_id = %s", (user_id,))
                elif role == 'national_manager':
                    cursor.execute("DELETE FROM admin_national_manager WHERE user_id = %s", (user_id,))
                    
                cursor.execute("DELETE FROM user WHERE user_id = %s", (user_id,))
                
                conn.commit()
                flash("Deleted successfully.", 'success')
                return redirect(url_for('admin.staff_management'))
            except MySQLError as e:
                conn.rollback()
                print("An error occurred:", e)
                flash("A database error occurred. Please try again.", 'danger')
            finally:
                cursor.close()
                conn.close()
        
        else:
            try:
                if role == 'staff':
                    cursor.execute("""
                        SELECT u.user_id, s.first_name, s.family_name
                        FROM user u
                        JOIN staff s ON u.user_id = s.user_id
                        WHERE u.user_id = %s
                    """, (user_id,))
                elif role == 'local_manager':
                    cursor.execute("""
                        SELECT u.user_id, l.first_name, l.family_name
                        FROM user u
                        JOIN local_manager l ON u.user_id = l.user_id
                        WHERE u.user_id = %s
                    """, (user_id,))
                elif role == 'national_manager':
                    cursor.execute("""
                        SELECT u.user_id, a.first_name, a.family_name
                        FROM user u
                        JOIN admin_national_manager a ON u.user_id = a.user_id
                        WHERE u.user_id = %s
                    """, (user_id,))
                    
                staff = cursor.fetchone()
                
                if not staff:
                    flash("Not found.", 'danger')
                    return redirect(url_for('admin.staff_management'))
                
                return render_template('admin_delete_staff.html', staff=staff, role=role)
            
            except MySQLError as e:
                print("An error occurred:", e)
                flash("A database error occurred. Please try again.", 'danger')
                cursor.close()
                conn.close()
                return redirect(url_for('admin.staff_management'))
            finally:
                cursor.close()
                conn.close()    
    else:
        return redirect(url_for('home.login'))
    
    
@admin_bp.route('/add_staff', methods=['GET', 'POST'])
@login_required
def add_staff():
    if 'loggedin' in session and session['role'] == 'admin':
        if request.method == 'POST':
            title = request.form['title']
            first_name = request.form['first_name']
            family_name = request.form['family_name']
            email = request.form['email']
            phone_number = request.form['phone_number']
            date_of_birth = request.form['date_of_birth']
            status = request.form['status']
            store_id = request.form['store_id']
            role = request.form['role']
            
            username = email.split('@')[0]
            default_password = 'default_password123'  # Change this to a secure default password
            salt = uuid.uuid4().hex
            hashed_password = hashing.hash_value(default_password, salt=salt)

            conn, cursor = db_cursor()
            
            try:
                cursor.execute(
                    'INSERT INTO user (username, email, date_of_birth, password_hash, salt, role) VALUES (%s, %s, %s, %s, %s, %s)',
                    (username, email, date_of_birth, hashed_password, salt, role.lower())
                )
                user_id = cursor.lastrowid
                
                if role == 'Staff':
                    cursor.execute(
                        'INSERT INTO staff (user_id, store_id, title, first_name, family_name, phone_number, status) '
                        'VALUES (%s, %s, %s, %s, %s, %s, %s)',
                        (user_id, store_id, title, first_name, family_name, phone_number, status)
                    )
                else:
                    cursor.execute(
                        'INSERT INTO local_manager (user_id, store_id, title, first_name, family_name, phone_number, status) '
                        'VALUES (%s, %s, %s, %s, %s, %s, %s)',
                        (user_id, store_id, title, first_name, family_name, phone_number, status)
                    )
                conn.commit()
                flash('New staff member added successfully! Default password is: ' + default_password, 'success')
                return redirect(url_for('admin.staff_management'))
            except MySQLError as e:
                conn.rollback()
                flash(f"An error occurred: {e}", 'danger')
            finally:
                cursor.close()
                conn.close()
        
        conn, cursor = db_cursor()
        cursor.execute('SELECT store_id, store_name FROM stores')
        stores = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return render_template('admin_add_staff.html', stores=stores)
    else:
        return redirect(url_for('home.login'))
