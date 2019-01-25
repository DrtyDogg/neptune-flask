from app import app, db
from flask import render_template, flash, request, redirect, url_for
from app.forms import AquariumForm, LoginForm, RegistrationForm, NewFeedingForm, NewWaterChangeForm, NewTemperaturReadingForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, WaterChange, Feeding, Temperature, Aquarium, Dashboard, Pager
from werkzeug.urls import url_parse
from datetime import datetime


@app.before_request
def before_request():
    # check if it is a new installation
    if User.query.first() is None:
        if request.path != url_for('register'):
            flash('No users exist, please create an admin user', category='warning')
            return redirect(url_for('register'))
    else:
        if Aquarium.query.first() is None:
            if request.path != url_for('new_aquarium'):
                flash('There are not any aquariums, please create one to continue', category='warning')
                return redirect(url_for('new_aquarium'))

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
        if not next_page or url_parse(next_page.netloc) != '':
            next_page = url_for('index')
        flash('The aquarium has been created', 'success')
        return redirect(next_page)
    return render_template(
        'aquarium.html',
        route='aquarium',
        title='Aquarium',
        head='Create a new aquarium',
        form=form,
        aquariums=aquariums)


@app.route('/aquarium/edit/<name>', methods=['GET', 'POST'])
@login_required
def edit_aquarium(name):
    form = AquariumForm()
    aquariums = Aquarium.query.all()
    aquarium = Aquarium.query.filter_by(name=name).first()
    if aquarium is not None:
        if form.validate_on_submit():
            aquarium.name = form.name.data
            aquarium.location = form.location.data
            db.session.commit()
            flash('The aquarium has been updated', 'success')
        else:
            form.name.data = aquarium.name
            form.location.data = aquarium.location
    return render_template(
        'aquarium.html',
        route='edit_aquarium',
        title='Edit an aquarium',
        head='Edit the {} aquarium'.format(aquarium.name),
        form=form,
        aquariums=aquariums)


@app.route('/aquarium/set/<aquarium_id>', methods=['GET'])
@login_required
def set_aquarium(aquarium_id):
    prev = request.args.get('return')
    if prev is None:
        prev = '/index'
    current_user.current_aquarium = aquarium_id
    db.session.commit()
    next_page = request.args.get('next')
    aquarium = Aquarium.query.get(aquarium_id)
    if not next_page or url_parse(next_page.netloc) != '':
        next_page = url_for('index')
    flash('You have set {} as the current aquarium'.format(aquarium.name), 'info')
    return redirect(prev)


@app.route('/feeding', methods=['GET'])
@login_required
def feeding():
    page = request.args.get('page', 1, type=int)
    form = NewFeedingForm()
    aquariums = Aquarium.query.all()
    query = Feeding.query.filter_by(
        aquarium_id=current_user.current_aquarium).order_by(
            Feeding.timestamp.desc()).paginate(
                page, app.config['PAGINATE'], False)
    feedings = Feeding.query.filter_by(
        aquarium_id=current_user.current_aquarium).order_by(
            Feeding.timestamp.desc()).all()
    counts = []
    myusers = set([x.user.name for x in feedings])
    for user in myusers:
        count = len([x for x in feedings if x.user.name == user])
        counts.append({'name': user, 'count': count})
    pager = getpager(query, 'feeding')
    return render_template(
        'feeding.html',
        route='feeding',
        title='Feeding',
        form=form,
        query=query,
        counts=counts,
        aquariums=aquariums,
        pager=pager)


@app.route('/feeding/new', methods=['POST'])
@login_required
def new_feeding():
    feeding = Feeding(
        user_id=current_user.id,
        timestamp=datetime.utcnow(),
        aquarium_id=current_user.current_aquarium)
    db.session.add(feeding)
    db.session.commit()
    flash('Your feeding has been recorded', 'success')
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
        'index.html', route='index', title='Home', dash=dash, aquariums=aquariums)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid login information.  Try again!', 'danger')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        flash('You are logged in', 'info')
        return redirect(url_for('index'))
    return render_template('login.html', route='login', title='Log in', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash('You were successfully logged out', 'warning')
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
        flash('Congratulations you are now registered', 'success')
        return redirect(url_for('index'))
    return render_template('register.html', route='register', title='New User Registration', form=form)


@app.route('/temperature', methods=['GET'])
@login_required
def temperature():
    page = request.args.get('page', 1, type=int)
    form = NewTemperaturReadingForm()
    query = Temperature.query.filter_by(
        aquarium_id=current_user.current_aquarium).order_by(
            Temperature.timestamp.desc()).paginate(
                page, app.config['PAGINATE'], False)
    aquariums = Aquarium.query.all()
    average = 0

    temps = Temperature.query.filter_by(
        aquarium_id=current_user.current_aquarium).order_by(
            Temperature.timestamp.desc()).all()

    if len(temps) > 0:
        average = int(sum([x.temp for x in temps]) / len(temps))

    pager = getpager(query, 'temperature')
    return render_template(
        'temperature.html',
        title='Temperature',
        route='temperature',
        form=form,
        average=average,
        query=query,
        aquariums=aquariums,
        pager=pager)


@app.route('/temperature/new', methods=['POST'])
@login_required
def new_temperature():
    t = Temperature(
        temp=request.form['temp'],
        timestamp=datetime.utcnow(),
        aquarium_id=current_user.current_aquarium)
    db.session.add(t)
    db.session.commit()
    flash('The temperature reading for was sucessfully added', 'success')
    return redirect(url_for('temperature'))


@app.route('/user/<id>')
@login_required
def user(id):
    user = User.query.get(id)
    wchanges = WaterChange.query.filter_by(user_id=user.id)
    feedings = Feeding.query.filter_by(user_id=user.id)
    return render_template(
        'user.html', route='user', title='{}\'s profile'.format(user.name),
        user=user, waterChanges=wchanges, feedings=feedings)


@app.route('/waterchange', methods=['GET'])
@login_required
def waterchange():
    page = request.args.get('page', 1, type=int)
    form = NewWaterChangeForm()
    aquariums = Aquarium.query.all()
    query = WaterChange.query.filter_by(
        aquarium_id=current_user.current_aquarium).order_by(
            WaterChange.timestamp.desc()).paginate(
                page, app.config['PAGINATE'], False)
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

    pager = getpager(query, 'waterchange')
    return render_template(
        'waterchange.html',
        route='waterchange',
        title='Water Change',
        form=form,
        query=query,
        average=average,
        counts=counts,
        aquariums=aquariums,
        pager=pager)


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
    flash('Your waterchange was successfully recorded', 'success')
    return redirect(url_for('waterchange'))


def getpager(query, route):
    next_url = url_for(route, page=query.next_num) \
        if query.has_next else None
    prev_url = url_for(route, page=query.prev_num) \
        if query.has_prev else None
    startpage = 1
    endpage = query.pages + 1
    if query.pages > 10:
        if query.page > 5:
            startpage = query.page - 5
        if startpage + 10 < query.pages:
            endpage = startpage + 10

    return Pager(next_url, prev_url, startpage, endpage, route)
