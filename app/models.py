from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), index=True)
    name = db.Column(db.String(32))
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow())
    current_aquarium = db.Column(db.Integer, default=1)
    feedings = db.relationship('Feeding', backref='user', lazy='dynamic')
    water_changes = db.relationship(
        'WaterChange', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.name)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Feeding(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    aquarium_id = db.Column(db.Integer, db.ForeignKey('aquarium.id'))

    def __repr__(self):
        u = User.query.get(self.user_id)
        return '<Feeding {} by {}>'.format(self.timestamp, u.name)


class WaterChange(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    aquarium_id = db.Column(db.Integer, db.ForeignKey('aquarium.id'))

    def __repr__(self):
        u = User.query.get(self.user_id)
        return '<Water Change {} changed {} percent on {}'.format(
            u.name, self.amount, self.timestamp)


class Temperature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temp = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    aquarium_id = db.Column(db.Integer, db.ForeignKey('aquarium.id'))

    def __repr__(self):
        return '<Temperature {} degrees on {}>'.format(self.temp, self.timestamp)


class Aquarium(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), index=True)
    location = db.Column(db.String(64))
    feedings = db.relationship('Feeding', backref='aquarium', lazy='dynamic')
    water_changes = db.relationship(
        'WaterChange', backref='aquarium', lazy='dynamic')

    def __repr__(self):
        return '<Aquarium {}>'.format(self.name)
