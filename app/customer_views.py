from flask import current_app as app
from mysql.connector import Error as MySQLError
from flask import Blueprint,render_template, request, redirect, url_for, session, flash
from app import utils
import re
from datetime import datetime
from .utils import db_cursor
from flask_hashing  import Hashing

customer_bp = Blueprint('customer', __name__, template_folder='templates/customer')

@customer_bp.route('/customer_dashboard', methods=['GET', 'POST'])
def customer_dashboard():
    return render_template('customer_dashboard.html')