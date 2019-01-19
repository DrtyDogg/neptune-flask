from app import app, db
from flask import render_template, flash, request, redirect, url_for
from app.forms import LoginForm, RegistrationForm, NewFeedingForm, NewWaterChangeForm, NewTemperaturReadingForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, WaterChange, Feeding, Temperature
from werkzeug.urls import url_parse
from datetime import datetime


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/')
@app.route('/index')
def index():
    water = WaterChange.query.order_by(WaterChange.timestamp.desc()).first()
    feed = Feeding.query.order_by(Feeding.timestamp.desc()).first()
    temp = Temperature.query.order_by(Temperature.timestamp.desc()).first()
    return render_template(
        'index.html', title='Home', water=water, feed=feed, temp=temp)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid login information.  Try again!')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(url_for('index'))
    return render_template('login.html', title='Log in', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, name=form.name.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations you are now registered')
        return redirect(url_for('index'))
    return render_template('register.html', title='New User Registration', form=form)


@app.route('/user/<id>')
@login_required
def user(id):
    user = User.query.get(id)
    wchanges = WaterChange.query.filter_by(user_id=user.id)
    feedings = Feeding.query.filter_by(user_id=user.id)
    return render_template(
        'user.html', title='{}\'s profile'.format(user.name),
        user=user, waterChanges=wchanges, feedings=feedings)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/feeding', methods=['GET', 'POST'])
@login_required
def feeding():
    form = NewFeedingForm()
    feedings = Feeding.query.order_by(Feeding.timestamp.desc()).all()
    users = User.query.all()
    if request.method == 'POST':
        feeding = Feeding(user_id=current_user.id)
        db.session.add(feeding)
        db.session.commit()
        flash('Feeding successfully recorded')
        return redirect(url_for('feeding'))
    return render_template(
        'feeding.html',
        title='Feeding',
        form=form,
        feedings=feedings,
        users=users)


@app.route('/waterchange', methods=['POST', 'GET'])
@login_required
def waterchange():
    form = NewWaterChangeForm()
    waterchanges = WaterChange.query.order_by(WaterChange.timestamp.desc()).all()
    users = User.query.all()
    total = 0
    count = 0
    average = 'N/A'
    if len(waterchanges) > 0:
        for wc in waterchanges:
            total += wc.amount
            count = count + 1
        average = int(round(total/count, 0))
    if request.method == 'POST':
        wc = WaterChange(user_id=current_user.id, amount=form.amount.data)
        db.session.add(wc)
        db.session.commit()
        flash('Water change successfully recorded')
        return redirect(url_for('waterchange'))
    return render_template(
        'waterchange.html',
        title='Water Change',
        form=form,
        waterchanges=waterchanges,
        users=users,
        average=average)


@app.route('/temperature', methods=['POST', 'GET'])
@login_required
def temperature():
    form = NewTemperaturReadingForm()
    temps = Temperature.query.order_by(Temperature.timestamp.desc()).all()
    total = 0
    count = 0
    average = 0
    if len(temps) > 0:
        for t in temps:
            total += t.temp
            count = count + 1
            average = int(round(total/count))
    if request.method == 'POST':
        t = Temperature(temp=form.temp.data)
        db.session.add(t)
        db.session.commit()
        return redirect(url_for('temperature'))
    return render_template(
        'temperature.html', title='Temperature', form=form, average=average, temps=temps)
