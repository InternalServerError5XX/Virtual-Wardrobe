from flask import Blueprint, render_template, redirect, request, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db
from .validation import rate_password
from .token import *
from flask_login import login_required, login_user, logout_user, current_user
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message

auth = Blueprint('auth', __name__)



@auth.route('/sign_up/', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'GET':
        return render_template('sign_up.html')
    else:
        username = request.form.get('username')
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        confirmed = False
        user = User.query.filter_by(email=email).first()

        if user:
            flash("User with this email is already exists!", category='error')
        elif password1 != password2:
            flash("Passwords are different.", category='error')
        elif rate_password(password1) < 5:
            flash("Your Password is too weak!", category='error')

        else:
            password = password1

            new_user = User(email=email, username=username, password=generate_password_hash(password, method='sha256'), confirmed=confirmed) # type: ignore
            db.session.add(new_user)
            db.session.commit()

            # token = generate_confirmation_token(user.email)
            # confirm_url = url_for('user.confirm_email', token=token, _external=True)
            # html = render_template('activate.html', confirm_url=confirm_url)
            # subject = "Please confirm your email"
            # send_email(new_user.email, subject, html)
            login_user(new_user, remember=request.form.get('remember_me'))

            flash("Congrats, you're succesfully Signed Up!", category='success')
            return redirect(url_for('views.home')) 
    return render_template('sign_up.html', user=current_user)


# @auth.route("/confirm_email/<token>", methods=['GET','POST'])
# def confirm_email(token):
#     if request.method == 'GET':
#         render_template('confirm_email.html')
#     else:
#         try:
#             email = confirm_token(token)
#         except:
#             flash('The confirmation link is invalid or has expired.', 'danger')
#             user = User.query.filter_by(email=email).first_or_404()
#         if user.confirmed:
#             flash('Account already confirmed. Please login.', 'success')
#         else:
#             user.confirmed = True
#             db.session.add(user)
#             db.session.commit()
#             flash('You have confirmed your account. Thanks!', 'success')
#         return redirect(url_for('views.home'))



@auth.route('/log-in/', methods=['GET', 'POST'])
def log_in():
    if request.method == 'GET':
        return render_template('log_in.html')
    else:
        email = request.form.get('email')
        password = request.form.get('password')
        message = ''

        user = User.query.filter_by(email=email).first()
        if user:

            if check_password_hash(user.password, password):
                flash("Congrats, you're succesfully Logged In!", category='success')
                login_user(user, remember=request.form.get('remember_me'))
                return redirect(url_for('views.home')) 

            else:
                flash("Incorrect Password!", category='error')

        else:
            flash("User isn`t exists!", category='error')
    return render_template('log_in.html')


@auth.route('/log-out/')
@login_required
def log_out():
    logout_user()
    return render_template('main.html')


@auth.route('/')
def start():
    return render_template('main.html')




