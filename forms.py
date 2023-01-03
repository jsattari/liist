#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from wtforms import StringField, PasswordField

from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, Length, EqualTo, Email
from wtforms import ValidationError
from models import User


class LoginForm(FlaskForm):
    """
    Class that represents login forms

    Attributes
    ----------
    email : str
        email address used by user for registration
    password : str
        password applied at registration for registered email address
    """

    email = StringField(validators=[InputRequired(), Email(), Length(1, 64)])
    password = PasswordField(
        validators=[InputRequired(), Length(min=8, max=16)])


class NewUserForm(FlaskForm):
    """
    New user login form

    Attributes
    ----------
    email : str
        email address that will be used for subseqent logins
    username : str
        alias that will be used for display on internal pages
    password : str
        8-16 character phrase that will be used for future logins
    check_password : str
        verification field. must be exact match for password field
    """

    email = StringField(validators=[InputRequired(), Email(), Length(1, 64)])
    username = StringField(validators=[InputRequired(), Length(1, 32)])
    password = PasswordField(validators=[InputRequired(), Length(8, 16)])
    check_password = PasswordField(
        validators=[
            InputRequired(),
            Length(8, 16),
            EqualTo("password", message="Passwords must match!"),
        ]
    )

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError("Email already registered!")
