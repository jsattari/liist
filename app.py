#!/usr/bin/env python3
# -*- coding:utf-8 -*-


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from dotenv import load_dotenv
import os

# load env file
load_dotenv(os.path.abspath(os.getcwd()) + "/.env")

DB_URI = os.getenv("DB_URI")

login_mgr = LoginManager()
login_mgr.session_protection = "strong"
login_mgr.login_view = "login"
login_mgr.login_message_category = "info"

db = SQLAlchemy()
bcrypt = Bcrypt()


def create_app():

    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
    app.config["SECRET_KEY"] = "super-secret"

    login_mgr.init_app(app)
    db.init_app(app)
    bcrypt.init_app(app)

    app.app_context().push()
    db.create_all()

    return app
