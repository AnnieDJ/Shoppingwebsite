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
@admin_bp.route('/view_all')
@login_required
def view_all():
    if 'loggedin' in session and session['role'] == 'admin':
        conn, cursor = db_cursor()
        
        try:
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

            cursor.execute("""
                SELECT
                    u.user_id,
                    u.username,
                    u.email,
                    l.title,
                    CONCAT(l.first_name, ' ', l.family_name) AS full_name,
                    l.phone_number,
                    l.store_id
                FROM
                    user u
                JOIN
                    local_manager l ON u.user_id = l.user_id
                WHERE
                    u.role = 'local_manager'
                ORDER BY
                    l.first_name, l.family_name
            """)
            local_managers = cursor.fetchall()

            cursor.execute("""
                SELECT
                    u.user_id,
                    u.username,
                    u.email,
                    n.title,
                    CONCAT(n.first_name, ' ', n.family_name) AS full_name,
                    n.phone_number
                FROM
                    user u
                JOIN
                    admin_national_manager n ON u.user_id = n.user_id
                WHERE
                    u.role = 'national_manager'
                ORDER BY
                    n.first_name, n.family_name
            """)
            national_managers = cursor.fetchall()

        except Exception as e:
            print("An error occurred:", e)
            flash("A database error occurred. Please try again.")
            return redirect(url_for('admin.dashboard'))
        finally:
            cursor.close()
            conn.close()
            
        return render_template('admin_view_all.html', staff_members=staff_members, local_managers=local_managers, national_managers=national_managers)
    else:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('home.login'))
    
@admin_bp.route('/edit_staff/<int:user_id>', methods=['GET'])
@login_required
def edit_staff(user_id):
    if 'loggedin' in session and session['role'] == 'admin':
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
            return render_template('admin_edit_staff.html', staff_member=staff_member)
        else:
            flash('Staff member not found.', 'warning')
            return redirect(url_for('admin.view_all'))
    else:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('home.login'))

@admin_bp.route('/edit_local_manager/<int:user_id>', methods=['GET'])
@login_required
def edit_local_manager(user_id):
    if 'loggedin' in session and session['role'] == 'admin':
        conn, cursor = db_cursor()
        cursor.execute("""
            SELECT u.user_id, l.title, l.phone_number, u.email, l.store_id
            FROM user u
            JOIN local_manager l ON u.user_id = l.user_id
            WHERE u.user_id = %s
        """, (user_id,))
        local_manager = cursor.fetchone()
        cursor.close()
        if local_manager:
            return render_template('admin_edit_local_manager.html', local_manager=local_manager)
        else:
            flash('Local manager not found.', 'warning')
            return redirect(url_for('admin.view_all'))
    else:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('home.login'))

@admin_bp.route('/edit_national_manager/<int:user_id>', methods=['GET'])
@login_required
def edit_national_manager(user_id):
    if 'loggedin' in session and session['role'] == 'admin':
        conn, cursor = db_cursor()
        cursor.execute("""
            SELECT u.user_id, n.title, n.phone_number, u.email
            FROM user u
            JOIN admin_national_manager n ON u.user_id = n.user_id
            WHERE u.user_id = %s
        """, (user_id,))
        national_manager = cursor.fetchone()
        cursor.close()
        if national_manager:
            return render_template('admin_edit_national_manager.html', national_manager=national_manager)
        else:
            flash('National manager not found.', 'warning')
            return redirect(url_for('admin.view_all'))
    else:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('home.login'))

@admin_bp.route('/update_staff/<int:user_id>', methods=['POST'])
@login_required
def update_staff(user_id):
    if 'loggedin' in session and session['role'] == 'admin':
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
        return redirect(url_for('admin.view_all'))
    else:
        flash('Unauthorized to perform this action.', 'danger')
        return redirect(url_for('home.login'))

@admin_bp.route('/update_local_manager/<int:user_id>', methods=['POST'])
@login_required
def update_local_manager(user_id):
    if 'loggedin' in session and session['role'] == 'admin':
        title = request.form['title']
        phone_number = request.form['phone_number']
        email = request.form['email']
        store_id = request.form['store_id']

        conn, cursor = db_cursor()
        try:
            cursor.execute("""
                UPDATE local_manager l JOIN user u ON l.user_id = u.user_id
                SET l.title = %s, l.phone_number = %s, u.email = %s, l.store_id = %s
                WHERE l.user_id = %s
            """, (title, phone_number, email, store_id, user_id))
            conn.commit()
            flash('Local manager updated successfully.', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Failed to update local manager: {str(e)}', 'danger')
        finally:
            cursor.close()
        return redirect(url_for('admin.view_all'))
    else:
        flash('Unauthorized to perform this action.', 'danger')
        return redirect(url_for('home.login'))

@admin_bp.route('/update_national_manager/<int:user_id>', methods=['POST'])
@login_required
def update_national_manager(user_id):
    if 'loggedin' in session and session['role'] == 'admin':
        title = request.form['title']
        phone_number = request.form['phone_number']
        email = request.form['email']

        conn, cursor = db_cursor()
        try:
            cursor.execute("""
                UPDATE admin_national_manager n JOIN user u ON n.user_id = u.user_id
                SET n.title = %s, n.phone_number = %s, u.email = %s
                WHERE n.user_id = %s
            """, (title, phone_number, email, user_id))
            conn.commit()
            flash('National manager updated successfully.', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Failed to update national manager: {str(e)}', 'danger')
        finally:
            cursor.close()
        return redirect(url_for('admin.view_all'))
    else:
        flash('Unauthorized to perform this action.', 'danger')
        return redirect(url_for('home.login'))
    

@admin_bp.route('/delete_staff/<int:user_id>', methods=['POST'])
@login_required
def delete_staff(user_id):
    if 'loggedin' in session and session['role'] == 'admin':
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
        return redirect(url_for('admin.view_all'))
    else:
        flash('Unauthorized to perform this action.', 'danger')
        return redirect(url_for('home.login'))

@admin_bp.route('/delete_local_manager/<int:user_id>', methods=['POST'])
@login_required
def delete_local_manager(user_id):
    if 'loggedin' in session and session['role'] == 'admin':
        conn, cursor = db_cursor()
        try:
            cursor.execute("DELETE FROM local_manager WHERE user_id = %s", (user_id,))
            conn.commit()
            flash('Local manager deleted successfully.', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Failed to delete local manager: {str(e)}', 'danger')
        finally:
            cursor.close()
        return redirect(url_for('admin.view_all'))
    else:
        flash('Unauthorized to perform this action.', 'danger')
        return redirect(url_for('home.login'))

@admin_bp.route('/delete_national_manager/<int:user_id>', methods=['POST'])
@login_required
def delete_national_manager(user_id):
    if 'loggedin' in session and session['role'] == 'admin':
        conn, cursor = db_cursor()
        try:
            cursor.execute("DELETE FROM admin_national_manager WHERE user_id = %s", (user_id,))
            conn.commit()
            flash('National manager deleted successfully.', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Failed to delete national manager: {str(e)}', 'danger')
        finally:
            cursor.close()
        return redirect(url_for('admin.view_all'))
    else:
        flash('Unauthorized to perform this action.', 'danger')
        return redirect(url_for('home.login'))
    
