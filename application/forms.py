from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Email
from application.models import User


class LoginForm(FlaskForm):
    email = StringField('Email ID', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    name = StringField('First Name', validators=[
                       DataRequired(), Length(min=4, max=10)])
    email = StringField('Email ID', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField(
        'Confirm Password', validators=[DataRequired(), EqualTo('password')])
    # remember = BooleanField('Remember Me')
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(
                'You have an account with this Email already')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email ID', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField(
        'Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Update Password')


class CreateGroupForm(FlaskForm):
    name = StringField('Group Name', validators=[
                       DataRequired(), Length(min=4, max=15)])
    desc = StringField('Description of the Group', validators=[
                       DataRequired(), Length(min=4, max=22)])
    submit = SubmitField('Create Group')


class SearchMovieForm(FlaskForm):
    name = StringField('Movie Name', validators=[
                       DataRequired(), Length(max=50)])
    submit = SubmitField('Search')
