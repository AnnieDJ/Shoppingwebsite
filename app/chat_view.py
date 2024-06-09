from flask import current_app as app
from mysql.connector import Error as MySQLError
from flask import Blueprint,render_template, request, redirect, url_for, session, flash, jsonify
from app import utils
import re
from datetime import datetime, date
from .utils import db_cursor
from flask_hashing import Hashing
from . import hashing
from .utils import db_cursor, login_required
from .utils import db_cursor

chat_bp = Blueprint('chat', __name__, template_folder='templates/chat')
# Assuming you have a chat blueprint setup
@chat_bp.route('/chat')
def index():
    username = session.get('username', 'Guest')  
    role = session.get('role', 'NoRole')         
    return render_template('chatview.html',username=username,role=role)
