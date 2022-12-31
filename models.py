#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from app import db
from flask_login import UserMixin
from datetime import datetime


class User(db.Model, UserMixin):
    """
    Class to house users for login
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, nullable=False)  # id column
    email = db.Column(db.String(50), unique=True, nullable=False)  # noqa: E501
    password_hash = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f"<User {self.email}>"


class Grocery(db.Model):
    """
    Class that houses grocery items
    """

    __tablename__ = "grocerylist"

    id = db.Column(db.Integer, primary_key=True, nullable=False)  # id column
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))  # noqa: E501
    item = db.Column(
        db.String(16), nullable=False
    )  # grocery list, 500 char max, can't be blank
    date_updated = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Lists {self.id}>"
