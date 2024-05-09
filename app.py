from flask import Flask
from flask_hashing import Hashing

from blueprints.home.home import home_bp
from blueprints.customer.customer import customer_bp
from blueprints.staff.staff import staff_bp
from blueprints.local_manager.local_manager import local_manager_bp
from blueprints.national_manager.national_manager import national_manager_bp
from blueprints.admin.admin import admin_bp

# Initializing Flask application
app = Flask(__name__)
hashing = Hashing(app)
app.secret_key = 'AVA'
app.register_blueprint(home_bp)
app.register_blueprint(customer_bp)
app.register_blueprint(staff_bp)
app.register_blueprint(local_manager_bp)
app.register_blueprint(national_manager_bp)
app.register_blueprint(admin_bp)


if __name__ == '__main__':
    app.run(debug=True)