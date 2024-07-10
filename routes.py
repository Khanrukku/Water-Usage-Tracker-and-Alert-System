from flask import render_template, url_for, flash, redirect, request
from app import app, db, bcrypt
from app.models import User, WaterRecord
from app.forms import RegistrationForm, LoginForm, RecordForm
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/")
@app.route("/home")
def home():
    if current_user.is_authenticated:
        records = WaterRecord.query.filter_by(user_id=current_user.id).order_by(WaterRecord.date.desc()).all()
        return render_template('index.html', records=records)
    else:
        return render_template('index.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/profile")
@login_required
def profile():
    return render_template('profile.html', title='Profile')

@app.route("/record", methods=['GET', 'POST'])
@login_required
def record():
    form = RecordForm()
    if form.validate_on_submit():
        record = WaterRecord(amount=form.amount.data, user_id=current_user.id)
        db.session.add(record)
        db.session.commit()
        flash('Water record has been added!', 'success')
        return redirect(url_for('home'))
    return render_template('record.html', title='Record', form=form)
