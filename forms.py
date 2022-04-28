from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class LoginForm(FlaskForm):

    email = StringField("Email: ", validators=[Email("Incorrect email")])
    psw = PasswordField("Password: ", validators=[DataRequired(), Length(min=4, max=100, message="Password must be between 4 and 100 characters")])
    remember = BooleanField("Remember", default = False)
    submit = SubmitField("Enter")

class RegisterForm(FlaskForm):
    name = StringField('Name: ', validators=[Length(min=4, max=100, message='Name must be between 4 and 100 characters' )])
    email = StringField('Email: ', validators=[Email('Incorrect email')])
    psw = PasswordField('Password: ', validators=[DataRequired(), Length(min=4, max=100, message="Password must be between 4 and 100 characters")])
    psw2 = PasswordField('Repeat password: ', validators=[DataRequired(), EqualTo('psw', message="Passwords don't match")])
    submit = SubmitField('Sign up')