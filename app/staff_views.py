from flask import current_app as app
from mysql.connector import Error as MySQLError
from flask import Blueprint,render_template, request, redirect, url_for, session, flash
from app import utils
import re
from datetime import datetime
from .utils import db_cursor
from flask_hashing  import Hashing

staff_bp = Blueprint('staff', __name__, template_folder='templates/staff')


# staff dashboard
@staff_bp.route('/dashboard')
def dashboard():
    if 'loggedin' in session and session['role'] == 'staff':
        return render_template('staff_dashboard.html')
    return redirect(url_for('home.login'))


