from flask import current_app as app
from mysql.connector import Error as MySQLError
from flask import Blueprint,render_template, request, redirect, url_for, session, flash
from app import utils
import re
from datetime import datetime
from .utils import db_cursor
from flask_hashing  import Hashing

national_manager_bp = Blueprint('national_manager', __name__, template_folder='templates/national_manager')


@national_manager_bp.route('/dashboard')
def dashboard():
    if 'loggedin' in session and session['role'] == 'national_manager':
        return render_template('national_manager_dashboard.html')
    return redirect(url_for('home.login'))

@national_manager_bp.route('/national_manager_profile')
def national_manager_profile():
    if 'loggedin' in session and session['loggedin']:
        with db_cursor() as cursor:
            cursor.execute("SELECT * FROM admin_national_manager WHERE user_name = %s", (session['username'],))
        national_manager_profile = cursor.fetchone()

        if national_manager_profile:
            encoded_national_manager_profile = [(national_manager_profile['admin_national_manager_id'], national_manager_profile['user_name'],
                                        national_manager_profile['title'], national_manager_profile['first_name'],
                                        national_manager_profile['family_name'], national_manager_profile['phone_number'], national_manager_profile['email'])]

            return render_template('/national_manager_profile.html', national_manager_profile=encoded_national_manager_profile,
                                   role=session['role'])
        else:
            flash('Manager profile not found', 'error')
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))

@national_manager_bp.route('/national_manager_edit_profile', methods=['GET', 'POST'])
def national_manager_edit_profile():
    if 'loggedin' in session and session['loggedin']:
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
                    WHERE user_name = %s", (
            title, first_name, family_name, phone_number, email, session['username'],))

            flash('Profile updated successfully!')
            return redirect(url_for('national_manager_profile'))
        else:
            with db_cursor() as cursor:
                cursor.execute("SELECT * FROM admin_national_manager WHERE user_name = %s", (session['username'],))
                national_manager_profile = cursor.fetchone()
                return render_template('/national_manager_profile.html', national_manager_profile=national_manager_profile, role=session['role'])
    else:
        return redirect(url_for('login'))