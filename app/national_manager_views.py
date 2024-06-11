from flask import current_app as app
from mysql.connector import Error as MySQLError
from flask import Blueprint,render_template, request, redirect, url_for, session, flash
import re
from . import hashing
from .utils import db_cursor, login_required
import uuid


national_manager_bp = Blueprint('national_manager', __name__, template_folder='templates/national_manager')


# national manager dashboard
@national_manager_bp.route('/dashboard')
@login_required
def dashboard():
    if 'loggedin' in session and session['role'] == 'national_manager':
        
        return render_template('national_manager_dashboard.html')
    return redirect(url_for('home.login'))


# allow national manager to view and edit profile
@national_manager_bp.route('/national_manager_profile', methods=['GET', 'POST'])
@login_required
def national_manager_profile():
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

    return render_template('national_manager_profile.html', data=data)


# allow national manager to change password
@national_manager_bp.route('/change_password', methods=['POST'])
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

    return redirect(url_for('national_manager.national_manager_profile'))

@national_manager_bp.route('/view_staff')
@login_required
def view_staff():
    if 'loggedin' in session and session['role'] == 'national_manager':
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

        except Exception as e:
            print("An error occurred:", e)
            flash("A database error occurred. Please try again.")
            return redirect(url_for('national_manager.dashboard'))
        finally:
            cursor.close()
            conn.close()
            
        return render_template('national_manager_view_staff.html', staff_members=staff_members, local_managers=local_managers)
    else:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('home.login'))
    
@national_manager_bp.route('/edit_staff/<int:user_id>', methods=['GET'])
@login_required
def edit_staff(user_id):
    if 'loggedin' in session and session['role'] == 'national_manager':
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
            return render_template('national_manager_edit_staff.html', staff_member=staff_member)
        else:
            flash('Staff member not found.', 'warning')
            return redirect(url_for('national_manager.view_staff'))
    else:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('home.login'))

@national_manager_bp.route('/update_staff/<int:user_id>', methods=['POST'])
@login_required
def update_staff(user_id):
    if 'loggedin' in session and session['role'] == 'national_manager':
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
        return redirect(url_for('national_manager.view_staff'))
    else:
        flash('Unauthorized to perform this action.', 'danger')
        return redirect(url_for('home.login'))

@national_manager_bp.route('/edit_local_manager/<int:user_id>', methods=['GET'])
@login_required
def edit_local_manager(user_id):
    if 'loggedin' in session and session['role'] == 'national_manager':
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
            return render_template('national_manager_edit_local_manager.html', local_manager=local_manager)
        else:
            flash('Local manager not found.', 'warning')
            return redirect(url_for('national_manager.view_staff'))
    else:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('home.login'))

@national_manager_bp.route('/update_local_manager/<int:user_id>', methods=['POST'])
@login_required
def update_local_manager(user_id):
    if 'loggedin' in session and session['role'] == 'national_manager':
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
        return redirect(url_for('national_manager.view_staff'))
    else:
        flash('Unauthorized to perform this action.', 'danger')
        return redirect(url_for('home.login'))

@national_manager_bp.route('/delete_staff/<int:user_id>', methods=['POST'])
@login_required
def delete_staff(user_id):
    if 'loggedin' in session and session['role'] == 'national_manager':
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
        return redirect(url_for('national_manager.view_staff'))
    else:
        flash('Unauthorized to perform this action.', 'danger')
        return redirect(url_for('home.login'))

@national_manager_bp.route('/delete_local_manager/<int:user_id>', methods=['POST'])
@login_required
def delete_local_manager(user_id):
    if 'loggedin' in session and session['role'] == 'national_manager':
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
        return redirect(url_for('national_manager.view_staff'))
    else:
        flash('Unauthorized to perform this action.', 'danger')
        return redirect(url_for('home.login')) 


@national_manager_bp.route('/view_news')
@login_required
def view_news():
    if 'loggedin' in session and session['role'] in ['national_manager']:
        conn, cursor = db_cursor()
        cursor.execute("""
            SELECT news_id, title, content, publish_date, creator_id, store_id
            FROM news
            ORDER BY publish_date DESC
        """)
        news_items = cursor.fetchall()
        cursor.close()
        return render_template('national_manager_view_news.html', news_items=news_items)
    else:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('home.login'))

@national_manager_bp.route('/edit_news/<int:news_id>', methods=['GET'])
@login_required
def edit_news(news_id):
    if 'loggedin' in session and session['role'] in ['national_manager']:
        conn, cursor = db_cursor()
        cursor.execute("SELECT news_id, title, content FROM news WHERE news_id = %s", (news_id,))
        news_item = cursor.fetchone()
        cursor.close()
        if news_item:
            return render_template('national_manager_edit_news.html', news_item=news_item)
        else:
            flash('News item not found.', 'warning')
            return redirect(url_for('national_manager.view_news'))
    else:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('home.login'))

@national_manager_bp.route('/update_news/<int:news_id>', methods=['POST'])
@login_required
def update_news(news_id):
    if 'loggedin' in session and session['role'] in ['national_manager']:
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
        return redirect(url_for('national_manager.view_news'))
    else:
        flash('Unauthorized to perform this action.', 'danger')
        return redirect(url_for('home.login'))

@national_manager_bp.route('/delete_news/<int:news_id>', methods=['POST'])
@login_required
def delete_news(news_id):
    if 'loggedin' in session and session['role'] in ['national_manager']:
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
        return redirect(url_for('national_manager.view_news'))
    else:
        flash('Unauthorized to perform this action.', 'danger')
        return redirect(url_for('home.login'))



from datetime import datetime

@national_manager_bp.route('/add_news', methods=['GET'])
@login_required
def add_news_form():
    if 'loggedin' in session and session['role'] == 'national_manager':
        
        today = datetime.today().strftime('%Y-%m-%d')  
        return render_template('national_manager_add_news.html', today=today)
    else:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('home.login'))

@national_manager_bp.route('/add_news', methods=['POST'])
@login_required
def add_news():
    if 'loggedin' in session and session['role'] == 'national_manager':
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
        return redirect(url_for('national_manager.view_news'))
    else:
        flash('Unauthorized to perform this action.', 'danger')
        return redirect(url_for('home.login'))


@national_manager_bp.route('/view_discount')
@login_required
def view_discount():
    if 'loggedin' in session and session['role'] in ['national_manager']:
        conn, cursor = db_cursor()
        # Update the SQL query to include ORDER BY
        cursor.execute("SELECT * FROM discount ORDER BY days ASC")
        discounts = cursor.fetchall()
        cursor.close()
        return render_template('national_manager/national_manager_discount.html', discounts=discounts)
    return redirect(url_for('home.login'))

 # Redirect if the user is not logged in or not authorized
@national_manager_bp.route('/edit_discount/<int:discount_id>')
@login_required
def edit_discount(discount_id):
    if 'loggedin' in session and session['role'] == 'national_manager':
        conn, cursor = db_cursor()
        cursor.execute("SELECT * FROM discount WHERE discount_id = %s", (discount_id,))
        discount = cursor.fetchone()
        cursor.close()
        if discount:
            return render_template('national_manager_edit_discount.html', discount=discount)
        else:
            flash("Discount not found.")
            return redirect(url_for('national_manager.view_discount'))
    return redirect(url_for('home.login'))

@national_manager_bp.route('/update_discount/<int:discount_id>', methods=['POST'])
@login_required
def update_discount(discount_id):
    if 'loggedin' in session and session['role'] == 'national_manager':
        days = request.form['days']
        discount_pricing = float(request.form['discount_pricing']) / 100  # Convert percentage to decimal

        conn, cursor = db_cursor()
        cursor.execute("UPDATE discount SET days = %s, discount_pricing = %s WHERE discount_id = %s",
                       (days, discount_pricing, discount_id))
        conn.commit()
        cursor.close()
        
        flash('Discount updated successfully.', 'success')
        return redirect(url_for('national_manager.view_discount'))
    return redirect(url_for('home.login'))

@national_manager_bp.route('/delete_discount/<int:discount_id>', methods=['POST'])
@login_required
def delete_discount(discount_id):
    if 'loggedin' in session and session['role'] == 'national_manager':
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
        return redirect(url_for('national_manager.view_discount'))
    else:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('home.login'))
   
@national_manager_bp.route('/add_discount', methods=['GET'])
@login_required
def add_discount_form():
    if 'loggedin' in session and session['role'] == 'national_manager':
        # Render a form to input new discount details
        return render_template('national_manager_add_discount.html')
    else:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('home.login'))


@national_manager_bp.route('/add_discount', methods=['POST'])
@login_required
def add_discount():
    if 'loggedin' in session and session['role'] == 'national_manager':
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
        
        return redirect(url_for('national_manager.view_discount'))
    else:
        flash('Unauthorized to perform this action.', 'danger')
        return redirect(url_for('home.login'))
    
@national_manager_bp.route('/financial_report')
@login_required
def financial_report():
    if 'loggedin' in session:
        conn, cursor = db_cursor()
        try:
            cursor.execute("""
                SELECT
                  CASE
                    WHEN MONTH(creation_date) BETWEEN 1 AND 3 THEN 'Q1'
                    WHEN MONTH(creation_date) BETWEEN 1 AND 6 THEN 'Q2'
                    WHEN MONTH(creation_date) BETWEEN 1 AND 9 THEN 'Q3'
                    WHEN MONTH(creation_date) BETWEEN 1 AND 12 THEN 'Q4'
                  END AS quarter,
                  SUM(total_cost) AS total_sales
                FROM orders
                WHERE status = 'Completed' AND YEAR(creation_date) = 2024
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

        return render_template('national_manager_financial_report.html', data=data)
    else:
        flash('Please log in to view this page.', 'info')
        return redirect(url_for('home.login'))
