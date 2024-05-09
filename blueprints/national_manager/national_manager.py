from flask import  render_template
from flask import session,request
from flask import Blueprint
import db.national_managerSql as national_managerSql


national_manager_bp = Blueprint('national_manager', __name__, template_folder='templates')

@national_manager_bp.route("/national_manager_profile", methods=["GET", "POST"])
def national_manager_profile():
    msg = None
    if request.method == "POST":
        title = request.form.get('title')
        first_name = request.form.get('first_name')
        family_name = request.form.get('last_name')
        position = request.form.get('position')
        phone_number= request.form.get('phone_number')
        national_manager = national_managerSql.Update_National_Manager_PROFILE.format(title, first_name, family_name, position, phone_number, session['id'])
        db.query(national_manager)
        msg = 'Your profile has been successfully updated!'
        resultsMemberInfo = db.query(national_managerSql.queryNationalManagerInfoByUserId.format(session['id']))
        return render_template('national_manager_profile.html', msg=msg, data=resultsMemberInfo[0])
    elif session['loggedin']:
        resultsMemberInfo = db.query(national_managerSql.queryNationalManagerInfoByUserId.format(session['id']))
        return render_template('national_manager_profile.html', data=resultsMemberInfo[0])
        # User is not logged in, redirect to login page
    msg = 'Please login first.'
    return render_template("national_manager_profile.html", msg=msg, user=None)