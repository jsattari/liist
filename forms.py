#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from wtforms import StringField, PasswordField

from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, Length, EqualTo, Email
from wtforms import ValidationError
from models import User


class LoginForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Email(), Length(1, 64)])
    password = PasswordField(
        validators=[InputRequired(), Length(min=8, max=16)])


class NewUserForm(FlaskForm):
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
