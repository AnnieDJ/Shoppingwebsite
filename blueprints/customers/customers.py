from app import app
from flask import render_template,redirect,url_for, g
from flask import session,request,jsonify,flash
from werkzeug.utils import secure_filename
import base64
import re
from datetime import datetime
import mysql.connector
import os
from werkzeug.utils import secure_filename
def some_function():
    from app import utils