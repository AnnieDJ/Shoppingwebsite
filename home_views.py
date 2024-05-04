from app import app
from flask import Flask, render_template, flash
from flask import session,request, redirect,url_for
from app import utils
import re
from datetime import datetime




## View All Instuctor Images on HomePage##
def get_all_instructors():
    cursor = utils.getCursor()
    
    # Fetch all instructor details
    cursor.execute("SELECT user_name, first_name, last_name FROM instructor")
    instructors = cursor.fetchall()
    cursor.close()
    
    # Append the path to the instructor's image URL
    for instructor in instructors:
        first_name = instructor['user_name'].split('_')[0].lower()
        image_filename = f"instr_{first_name}.jpg"
        instructor['image_src'] = url_for('static', filename=f'img/instructors/{image_filename}')
        
    return instructors




## Subscribe ## 
@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form['email']
    cursor = utils.getCursor()
    msg = ""

    cursor.execute("INSERT INTO subscriptions (email) VALUES (%s)", (email,))
    utils.connection.commit()

    # cursor.rowcount returns the number of rows affected by the last execute() operation
    if cursor.rowcount > 0:
        msg = "Subscribed successfully!"
    else:
        # This else part will not typically execute for an SQL error, only if no rows are affected
        msg = "Subscription failed. No changes made."

    cursor.close()
    return redirect(url_for('home', msg=msg))




## Home Page ##
@app.route('/')
@app.route('/home')
def home():
    
    ## Showing the subscribe msg ##
    msg = request.args.get('msg', '')
    # Showing instructor images on HomePage ##
    instructor_data = get_all_instructors()
    return render_template('index.html', instructors=instructor_data, message=msg)



@app.route('/login', methods=['GET', 'POST'])
def login():
    # Check if the message exists in the session
    msg = session.pop('msg', None)

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        user_password = request.form['password']

        cursor = utils.getCursor()
        cursor.execute("SELECT * FROM user WHERE user_name = %s", (username,))
        user = cursor.fetchone()

        user_id = ''
        if user is not None:
            role = user['role']
            if role == 'Member':
                cursor.execute("SELECT member_id FROM member WHERE user_name = %s", (username,))
                result = cursor.fetchone()
                user_id = result['member_id']
            elif role == 'Manager':
                cursor.execute("SELECT manager_id FROM manager WHERE user_name = %s", (username,))
                result = cursor.fetchone()
                user_id = result['manager_id']
            elif role == 'Instructor':
                cursor.execute("SELECT instructor_id FROM instructor WHERE user_name = %s", (username,))
                result = cursor.fetchone()
                user_id = result['instructor_id']
            else:
                msg = 'Invalid User'
                return render_template('login.html', msg=msg)

            #user_id = cursor.fetchone()['user_id']
            #account = user[:4] + (user_id,)
            #password = account[2]

           # user = cursor.fetchone()
            password = user['password']

            if utils.hashing.check_value(password, user_password, salt='schwifty'):
                session['loggedin'] = True
                session['id'] = user_id
                session['username'] = user['user_name']
                session['role'] = user['role']

                if role == 'Member':
                    return redirect(url_for('member_dashboard'))
                elif role == 'Instructor':
                    return redirect(url_for('instructor_dashboard'))
                elif role == 'Manager':
                    return redirect(url_for('manager_dashboard'))
            else:
                msg ='Invalid Password!'
        else:
            msg ='Invalid Username!'
    
    return render_template('login.html', msg=msg)


## Register ##
@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = session.pop('msg', None)
    if request.method == 'POST':
        # Form submitted, process the data
        username  = request.form['user_name']
        date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d')
    
        # Validation checks
        if not all(request.form.values()):
            msg = 'Please fill out all the fields!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', request.form['email']):
            msg = 'Invalid email address!'
        elif not re.match(r'^\d{9,12}$', request.form['phone']):
            msg = 'Invalid phone number!'
        elif utils.register_age_validation(date_of_birth):
            msg = 'member should be over 16 years old!'
        # Additional validation checks...

        elif not msg:
            # Data is valid, proceed with registration
            cursor = utils.getCursor()
            cursor.execute('SELECT * FROM member WHERE user_name = %s', (username,))
            account = cursor.fetchone()
            if account:
                msg = 'Account already exists!'
            else:
                session.clear()
                session['user_name'] = request.form['user_name']
                session['title'] = request.form['title']
                session['firstname'] = request.form['first_name']
                session['lastname'] = request.form['last_name']
                session['phone'] = request.form['phone']
                session['email'] = request.form['email']
                session['address'] = request.form['address']
                session['date_of_birth'] = request.form['date_of_birth']
                
                password = request.form['confirm_password']
                hashed = utils.hashing.hash_value(password, salt='schwifty')
                session['confirm_password'] = hashed
            
                return redirect(url_for('bank_info'))

        elif request.method == 'POST':
             # Form is empty... (no POST data)
             msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('/register/register.html', msg=msg) 