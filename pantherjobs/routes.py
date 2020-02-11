# Author: Graham Atlee
# This file handles all the URL routes and backend traffic

#flask related imports 
from flask import render_template, url_for, flash, redirect, request, abort
from pantherjobs import app, db, bcrypt, mail
from pantherjobs.forms import RegisterForm, LoginForm, UpdateProfileForm, PostForm, RequestResetForm, ResetPasswordForm
from pantherjobs.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message 

#general imports 
import secrets
import os 
from PIL import Image 
from datetime import datetime


@app.route('/')
def index():
    #fetch all posts to be loaded into home page 
    page = request.args.get('page',1,type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5) 
    return render_template('index.html', posts=posts)

@app.route('/about')
def about():
    return render_template('about.html', title='About')

@app.route('/register', methods=['POST', 'GET'])
def register():
    
    #check if the user is logged in.
    #if they are they can't access this page 
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form=RegisterForm()
    if form.validate_on_submit():

        #get all the data submitted through the form 
        fullname = form.fullname.data 
        email = form.email.data
        password = form.password.data
        hash_password = bcrypt.generate_password_hash(password).decode('utf-8')

        #now add this user into the database
        new_user = User(fullname=fullname, email=email, password=hash_password)
        db.session.add(new_user)
        db.session.commit()
        print(f'Success! {fullname} has been added to db')

        flash(f'Hi {form.fullname.data}, welcome to Panther Jobs! Your account is now officially setup and you may now login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register',form=form)

@app.route('/login', methods=['POST', 'GET'])
def login():
    #check if the user is logged in.
    #if they are they can't access this page 
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form=LoginForm()
    if form.validate_on_submit():
        #get the user from the database 
        user = User.query.filter_by(email=form.email.data).first()
        #if password matches the hash then login them in
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            #redirect user back to page they were trying to access 
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('index'))     #if not just send them to main page 
          
        else:
             flash(f'Login unsuccessful please try again', 'danger')

    return render_template('login.html', title='Login',form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/account')
@login_required
def account():
    #grab the users image profile from the db
    #THIS MAY CAUSE ERROR BELOW - come back to this
    image_file = url_for('static', filename='/profile_pics/' + current_user.image_file) 
    return render_template('account.html', title='Account', image_file=image_file)


def save_picture(form_picture):
    random_hex_name = secrets.token_hex(8) #generate 8 byte hex name 
    f_name, f_extension = os.path.splitext(form_picture.filename) #get file extension
    pic_filename = random_hex_name + f_extension # join the hex and the file extension
    picture_path = os.path.join(app.root_path, 'static/profile_pics', pic_filename) #create image to path

    #we need to resize image to prevent super large file sizes 
    outputsize = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(outputsize)

    i.save(picture_path) # save image to path
    return pic_filename

@app.route('/account-settings', methods=['GET','POST'])
@login_required
def settings():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        if form.profile_pic.data:
            new_f_name = save_picture(form.profile_pic.data)
            current_user.image_file = new_f_name 
            #TO-DO delete old image from server after uploading new one

        current_user.fullname = form.fullname.data
        current_user.email = form.email.data
        db.session.commit()
        flash('your account has been updated', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.fullname.data = current_user.fullname
        form.email.data = current_user.email

    return render_template('settings.html', form=form, title='Account Settings')


@app.route('/post/new', methods=['POST', 'GET'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        
        #grab all information coming in from post form
        title = form.title.data
        date_posted = datetime.utcnow()
        content = form.content.data
        job_timeframe = form.job_timeframe.data
        payment = form.payment.data
        email = form.email.data
        phone = form.phone.data

        #now add and save to database
        post = Post(title=title, date_posted=date_posted, content=content, job_timeframe=job_timeframe, payment=payment, email=email ,phone=phone, author=current_user)
        db.session.add(post)
        db.session.commit()

        #flash success message and return to home page
        flash('Your post has been created!', 'success')
        return redirect(url_for('index'))

    return render_template('newpost.html', title='New Job Post', 
                            form=form, legend='Post a Student Job')


@app.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post, title=post.title)

@app.route('/post/<int:post_id>/edit', methods=['POST', 'GET'])
@login_required
def update_post(post_id):

    #retrieve post from the db 
    post = Post.query.get_or_404(post_id)
    
    #check if the user trying to edit is permitted
    if post.author != current_user:
        abort(403)
    
    form = PostForm()

    #now add the updated post back into the db 
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.job_timeframe = form.job_timeframe.data
        post.payment = form.payment.data
        post.email = form.email.data
        post.phone = form.phone.data
        db.session.commit()
        flash('Your post has been updated', 'success')
        return redirect(url_for('post', post_id=post.id))
    
    #This will make all the current post data show up in the forms
    elif request.method == 'GET':
        form.title.data = post.title 
        form.content.data = post.content
        form.job_timeframe.data = post.job_timeframe
        form.payment.data = post.payment
        form.email.data = post.email
        form.phone.data = post.phone


    return render_template('newpost.html', title='Edit Post', 
                            form=form, legend='Update Job Post')


@app.route('/post/<int:post_id>/delete', methods=['POST', 'GET'])
@login_required
def delete_post(post_id):
    #retrieve post from the db 
    post = Post.query.get_or_404(post_id)
    
    #check if the user trying to edit is permitted
    if post.author != current_user:
        abort(403)
    
    db.session.delete(post)
    db.session.commit() 
    flash('Your post has been deleted!', 'success')

    return redirect(url_for('index'))


@app.route('/user/<string:fullname>')
def user_posts(fullname):
    #fetch all posts to be loaded into home page 
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(fullname=fullname).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)

@app.route('/user/<string:fullname>/delete', methods=['GET', 'POST'])
def delete_user(fullname):
    print(fullname)

########
# CODE BELOW NEEDS TESTING - CURRENTLY DOESNT WORK WITH SMTP ACCOUNT
#######

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='atleegraham16@gmail.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

