from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models import User


class LoginForm(FlaskForm):
    email = StringField('Email Address:', validators=[DataRequired(
        message="Email address is required"),
        Email(message="That isn't a valid email")])
    password = PasswordField('Password:', validators=[DataRequired(
        message="You can't log in without a password")])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    name = StringField('Name:', validators=[DataRequired()])
    email = StringField('Email Address:', validators=[
        DataRequired(), Email(message="That isn't a valid email")])
    password = PasswordField('Password:', validators=[DataRequired()])
    password_verify = PasswordField('Verify Password:', validators=[
        DataRequired(), EqualTo(
            'password', message="The passwords do not match")])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address')


class NewFeedingForm(FlaskForm):
    submit = SubmitField('Submit')


class NewWaterChangeForm(FlaskForm):
    amount = StringField('Amount:', validators=[DataRequired()])
    submit = SubmitField('Submit')


class NewTemperaturReadingForm(FlaskForm):
    temp = StringField('Temperature:', validators=[DataRequired()])
    submit = SubmitField('Submit')
