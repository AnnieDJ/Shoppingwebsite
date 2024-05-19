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

@customer_bp.route('/products/<store>')
def get_products(store):
    products = {
        'store1': [
            {
                'image': url_for('static', filename='tractor1.jpg'),
                'name': 'Deutz Fahr/Tractor',
                'description': 'This 2019 Deutz Fahr 6185 RC shift professional series tractor has only done 2,670 hours and is in great condition and ready to go to work . 50kph front suspension, front linkage and pto, this tractor is a serious contracting machine and with the loader would add incredible versitility to any fleet.',
                'price': '$369',
            },
            # 其他产品
        ],
        'store2': [
            # 其他产品
        ],
        'store3': [
            # 其他产品
        ],
    }
    return jsonify(products.get(store, []))

