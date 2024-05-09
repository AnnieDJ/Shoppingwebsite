from flask import Flask, render_template, flash
from flask import session, request, redirect, url_for
import db.db as db
from datetime import datetime

import re

from flask import Blueprint

home_bp = Blueprint('home', __name__, template_folder='templates')


@home_bp.route("/")
def home():
    return render_template("home.html")

