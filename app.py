#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os  # std lib

from flask import Flask  # 3rd party
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# postgres db uri
DB_URI = os.getenv("DB_URI")
SECRET_KEY = os.getenv("SECRET_KEY")

# initialize session mgr obj
login_mgr = LoginManager()
login_mgr.session_protection = "strong"
login_mgr.login_view = "login"
login_mgr.login_message_category = "info"

db = SQLAlchemy()  # interact with db
bcrypt = Bcrypt()  # password hashing


def create_app():
    """
    Creates Flask instance using application factory method. Applying
    this method allows scalability as the project matures and also prevents
    the extension from becoming bound to the app. The login_mgr,
    db, and bcrypt objects are all initialized below.
    """

    app = Flask(__name__)  # initiate flask obj

    app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI  # set db uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # improves perf
    app.config["SQLALCHEMY_ECHO"] = True  # log db actions to console
    app.config["SECRET_KEY"] = SECRET_KEY  # secret key for db

    # initiate all objects
    login_mgr.init_app(app)
    db.init_app(app)
    bcrypt.init_app(app)

    app.app_context().push()  # share app context per request
    db.create_all()  # create all db tables

    return app
