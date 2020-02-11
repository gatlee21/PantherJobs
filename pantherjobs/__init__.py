# Author: Graham Atlee
# This file initiates all of our import packages 

from flask import Flask
from flask import render_template, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

#flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'jku56hwaHiTHcaJt0MstlHDWCknKxL0x'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

#flask_sqlchemy
db = SQLAlchemy(app)

#flask_bycript
bcrypt = Bcrypt(app)

#flask_login
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

#Configure mail settings
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'atleegraham16@gmail.com'
app.config['MAIL_PASSWORD'] = 'gimbal_lock360'
mail = Mail(app)

from pantherjobs import routes