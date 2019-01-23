from app import app, db
from flask import render_template, flash, request, redirect, url_for
from app.forms import AquariumForm, LoginForm, RegistrationForm, NewFeedingForm, NewWaterChangeForm, NewTemperaturReadingForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, WaterChange, Feeding, Temperature, Aquarium, Dashboard
from werkzeug.urls import url_parse
from datetime import datetime


@app.before_first_request
def before_first_request():
    if len(Aquarium.query.all()) == 0:
        a = Aquarium(name='Home Aquarium')
        db.session.add(a)
        db.session.commit()


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/aquarium/create', methods=['GET', 'POST'])
@login_required
def new_aquarium():
    form = AquariumForm()
    aquariums = Aquarium.query.all()
    if form.validate_on_submit():
        aquarium = Aquarium(name=form.name.data, location=form.location.data)
        db.session.add(aquarium)
        db.session.commit()
        next_page = request.args.get('next')
        flash('Aquarium was created successfully')
        if not next_page or url_parse(next_page.netloc) != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template(
        'aquarium.html',
        title='Aquarium',
        head='Create a new aquarium',
        form=form,
        aquariums=aquariums)


@app.route('/aquarium/edit/<name>', methods=['GET', 'POST'])
@login_required
def edit_aquarium(name):
    form = AquariumForm()
    aquarium = Aquarium.query.filter_by(name=name).first()
    if aquarium is not None:
        if form.validate_on_submit():
            aquarium.name = form.name.data
            aquarium.location = form.location.data
            db.session.commit()
        else:
            form.name.data = aquarium.name
            form.location.data = aquarium.location
    return render_template(
        'aquarium.html',
        title='Edit an aquarium',
        head='Edit the {} aquarium'.format(aquarium.name),
        form=form)


@app.route('/aquarium/set/<aquarium_id>', methods=['GET'])
@login_required
def set_aquarium(aquarium_id):
    current_user.current_aquarium = aquarium_id
    db.session.commit()
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page.netloc) != '':
        next_page = url_for('index')
    return redirect(next_page)


@app.route('/feeding', methods=['GET', 'POST'])
@login_required
def feeding():
    form = NewFeedingForm()
    aquariums = Aquarium.query.all()
    feedings = Feeding.query.filter_by(
        aquarium_id=current_user.current_aquarium).order_by(
            Feeding.timestamp.desc()).all()
    counts = []
    myusers = set([x.user.name for x in feedings])
    for user in myusers:
        count = len([x for x in feedings if x.user.name == user])
        counts.append({'name': user, 'count': count})
    return render_template(
        'feeding.html',
        title='Feeding',
        form=form,
        feedings=feedings,
        counts=counts,
        aquariums=aquariums)


@app.route('/feeding/new', methods=['POST'])
@login_required
def new_feeding():
    feeding = Feeding(
        user_id=current_user.id,
        timestamp=datetime.utcnow(),
        aquarium_id=current_user.current_aquarium)
    db.session.add(feeding)
    db.session.commit()
    return redirect(url_for('feeding'))


@app.route('/')
@app.route('/index')
def index():
    aquariums = Aquarium.query.all()
    dash = []
    for aquarium in aquariums:
        if Temperature.query.filter_by(aquarium_id=aquarium.id).count() > 0:
            temp = Temperature.query.filter_by(
                aquarium_id=aquarium.id).order_by(
                Temperature.timestamp.desc()).first().temp
        else:
            temp = 'N/A'

        if Feeding.query.filter_by(aquarium_id=aquarium.id).count() > 0:
            feeding = Feeding.query.filter_by(
                aquarium_id=aquarium.id).order_by(
                    Feeding.timestamp.desc()).first().timestamp
        else:
            feeding = None

        if WaterChange.query.filter_by(aquarium_id=aquarium.id).count() > 0:
            waterchange = WaterChange.query.filter_by(
                aquarium_id=aquarium.id).order_by(
                    WaterChange.timestamp.desc()).first().timestamp
        else:
            waterchange = None

        dash.append(Dashboard(
            aquarium.name,
            temp,
            feeding,
            waterchange))

    return render_template(
        'index.html', title='Home', dash=dash, aquariums=aquariums)


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


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


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


@app.route('/temperature', methods=['POST', 'GET'])
@login_required
def temperature():
    form = NewTemperaturReadingForm()
    temps = Temperature.query.filter_by(
        aquarium_id=current_user.current_aquarium).order_by(
            Temperature.timestamp.desc()).all()
    aquariums = Aquarium.query.all()
    average = 0
    if len(temps) > 0:
        average = sum([x.temp for x in temps]) / len(temps)

    return render_template(
        'temperature.html',
        title='Temperature',
        form=form,
        average=average,
        temps=temps,
        aquariums=aquariums)


@app.route('/temperature/new', methods=['POST'])
@login_required
def new_temperature():
    t = Temperature(
        temp=request.form['temp'],
        timestamp=datetime.utcnow(),
        aquarium_id=current_user.current_aquarium)
    db.session.add(t)
    db.session.commit()
    return redirect(url_for('temperature'))


@app.route('/user/<id>')
@login_required
def user(id):
    user = User.query.get(id)
    wchanges = WaterChange.query.filter_by(user_id=user.id)
    feedings = Feeding.query.filter_by(user_id=user.id)
    return render_template(
        'user.html', title='{}\'s profile'.format(user.name),
        user=user, waterChanges=wchanges, feedings=feedings)


@app.route('/waterchange', methods=['GET'])
@login_required
def waterchange():
    form = NewWaterChangeForm()
    aquariums = Aquarium.query.all()
    waterchanges = WaterChange.query.filter_by(
        aquarium_id=current_user.current_aquarium).order_by(
            WaterChange.timestamp.desc()).all()
    users = User.query.all()
    counts = []
    for u in users:
        if len(waterchanges) > 0:
            count = len([x for x in waterchanges if x.user_id == u.id])
            counts.append({'name': u.name, 'count': count})

    average = 'N/A'
    if len(waterchanges) > 0:
        average = int(sum([x.amount for x in waterchanges]) / len(waterchanges))

    return render_template(
        'waterchange.html',
        title='Water Change',
        form=form,
        waterchanges=waterchanges,
        average=average,
        counts=counts,
        aquariums=aquariums)


@app.route('/waterchange/new', methods=['POST'])
@login_required
def new_waterchange():
    wc = WaterChange(
        user_id=current_user.id,
        amount=request.form['amount'],
        timestamp=datetime.utcnow(),
        aquarium_id=current_user.current_aquarium)
    db.session.add(wc)
    db.session.commit()
    return redirect(url_for('waterchange'))
