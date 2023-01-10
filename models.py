#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from app import db
from flask_login import UserMixin
from datetime import datetime


class User(db.Model, UserMixin):
    """
    Class to house data for user login credentials

    Attributes
    ----------
    id (pk): str
        unique id field used for identifying users
    email : str
        unique email address used for logins
    username : str
        identifier used for internal pages
    password_hash : str
        hashed value that represents user password for logins
    """

    __tablename__ = "users"

    id = db.Column(db.String(40), primary_key=True, nullable=False)  # noqa: E501
    email = db.Column(db.String(50), unique=True, nullable=False)  # noqa: E501
    username = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)  # noqa: E501

    def __repr__(self):
        """
        Returns users unique identifier
        """
        return f"<User {self.id}>"


class Grocery(db.Model):
    """
    Class that houses grocery items

    Attributes
    ----------
    id (pk): int
        serialized id for each grocery item
    user_id (fk): str
        unique user id field. references user.id
    item : str
        actual item entered for list
    date_updated : timestamp
        most recent update for items entered to list
    """

    __tablename__ = "grocerylist"

    id = db.Column(db.Integer, primary_key=True, nullable=False)  # id column
    user_id = db.Column(db.String, db.ForeignKey("users.id"))  # noqa: E501
    item = db.Column(
        db.String(16), nullable=False
    )  # grocery list, 500 char max, can't be blank
    date_updated = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        """
        Returns serial identifier for item
        """
        return f"<Lists {self.id}>"
