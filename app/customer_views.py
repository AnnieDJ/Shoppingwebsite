from flask import current_app as app
from mysql.connector import Error as MySQLError
from flask import Blueprint,render_template, request, redirect, url_for, session, flash,jsonify,Flask
from app import utils
import re
from datetime import datetime
from .utils import db_cursor
from flask_hashing  import Hashing


customer_bp = Blueprint('customer', __name__, template_folder='templates/customer')


# customer dashboard
@customer_bp.route('/dashboard')
def dashboard():
    if 'loggedin' in session and session['role'] == 'customer':
        return render_template('customer_dashboard.html')
    return redirect(url_for('home.login'))


