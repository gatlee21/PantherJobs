from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from pantherjobs.models import User 

class RegisterForm(FlaskForm):
    fullname = StringField('Full Name', 
    validators=[DataRequired(), Length(min=2, max=40) ])

    email = StringField('Email', validators=[DataRequired(), Email()])

    password = PasswordField('Password', validators=[DataRequired()])

    confirm_password = PasswordField('Confirm Password', 
    validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Sign Up')

    #check if full name is in database already
    def validate_fullname(self, fullname):
        user = User.query.filter_by(fullname=fullname.data).first()
        if user:
            raise ValidationError('That name already exists. Please enter another.')

    #check if this email already exists 
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email address already exists. Please enter another.')
    

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In') 

class UpdateProfileForm(FlaskForm):
    fullname = StringField('Full Name', 
    validators=[DataRequired(), Length(min=2, max=40) ])
    email = StringField('Email', validators=[DataRequired(), Email()])
    profile_pic = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Save')

    def validate_fullname(self, fullname):
        if fullname.data != current_user.fullname:
            user = User.query.filter_by(fullname=fullname.data).first()
            if user:
                raise ValidationError('That name already exists. Please enter another.')

    #check if this email already exists
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email address already exists. Please enter another.')

    
class PostForm(FlaskForm):
    title = StringField('Job Title', validators=[DataRequired()])
    content = TextAreaField('Description of Job', validators=[DataRequired()])
    job_timeframe = StringField('Job Time Frame', validators=[DataRequired()])
    payment = StringField('Payment', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone (optional)')
    # other = StringField('Other (optional)')


    submit = SubmitField('Post')


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    #check if email doesnt exist
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])

    confirm_password = PasswordField('Confirm Password', 
    validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')