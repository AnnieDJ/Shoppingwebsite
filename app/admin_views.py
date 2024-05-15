from flask import current_app as app
from mysql.connector import Error as MySQLError
from flask import Blueprint,render_template, request, redirect, url_for, session, flash
from app import utils
import re
from datetime import datetime
from .utils import db_cursor
from flask_hashing  import Hashing

admin_bp = Blueprint('admin', __name__, template_folder='templates/admin')

@admin_bp.route('/dashboard')
def dashboard():
    if 'loggedin' in session and session['role'] == 'admin':
        return render_template('admin_dashboard.html')
    return redirect(url_for('home.login'))

@admin_bp.route('/admin_profile')
def admin_profile():
    if 'loggedin' in session and session['role'] == 'admin':
        with db_cursor() as cursor:
            cursor.execute("SELECT * FROM admin_national_manager WHERE username = %s", (session['username']))
        admin_profile = cursor.fetchone()

        if admin_profile:
            encoded_admin_profile = [(admin_profile['admin_national_manager_id'], admin_profile['user_name'],
                                        admin_profile['title'], admin_profile['first_name'],
                                        admin_profile['family_name'], admin_profile['phone_number'], admin_profile['email'])]

            return render_template('/admin_profile.html', admin_profile=encoded_admin_profile,
                                   role=session['role'])
        else:
            flash('Admin profile not found', 'error')
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))

@admin_bp.route('/admin_edit_profile', methods=['GET', 'POST'])
def admin_edit_profile():
    if 'loggedin' in session and session['role'] == 'admin':
        if request.method == 'POST':
            title = request.form.get('title')
            first_name = request.form.get('first_name')
            family_name = request.form.get('family_name')
            phone_number = request.form.get('phone_number')
            email = request.form.get('email')

            redirect_route = {
                'customer': 'customer_profile',
                'staff': 'staff_profile',
                'local_manager': 'local_manager_profile',
                'national_manager': 'national_manager_profile',
                'admin': 'admin_profile'
            }.get(session.get('role'), 'login')

            # Input validation is maintained
            if len(phone_number) != 10 or not phone_number.isdigit():
                flash('Phone number must be 10 digits', 'danger')
                return redirect(url_for(redirect_route))

            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                flash('Invalid email address', 'danger')
                return redirect(url_for(redirect_route))

            with db_cursor() as cursor:
                cursor.execute("UPDATE admin_national_manager SET title = %s, first_name = %s, last_name = %s, phone_number = %s, email = %s \
                    WHERE username = %s", (
            title, first_name, family_name, phone_number, email, session['username'],))
            flash('Profile updated successfully!')
            return redirect(url_for('admin_profile'))
        else:
            with db_cursor() as cursor:
                cursor.execute("SELECT * FROM admin_national_manager WHERE user_name = %s", (session['username'],))
                admin_profile = cursor.fetchone()
                return render_template('/admin_profile.html', admin_profile=admin_profile, role=session['role'])
    else:
        return redirect(url_for('login'))