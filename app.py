#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_sessionstore import Session
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin
import bcrypt as bc
from datetime import datetime
from dotenv import load_dotenv
import os

# load env file
load_dotenv(os.path.abspath(os.getcwd()) + "/.env")

DB_URI = os.getenv("DB_URI")

# app object
app = Flask(__name__)

# app configs
app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "super-secret"
app.config["SECURITY_PASSWORD_HASH"] = "bcrypt"
app.config["SECURITY_PASSWORD_SALT"] = b"$2b$12$wqKlYjmOfXPghx3FuC3Pu."
app.config["SESSION_TYPE"] = "sqlalchemy"
app.config["SESSION_SQLALCHEMY_TABLE"] = "sessions"

db = SQLAlchemy(app)
session = Session(app)
session.app.session_interface.db.create_all()


# db templates
class Users(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, nullable=False)  # id column
    email = db.Column(db.String(255), unique=True, nullable=False)  # noqa: E501
    password_hash = db.Column(db.String(128), nullable=False)

    @property
    def password(self):
        raise AttributeError("Unable to read password")

    @password.setter
    def password(self, password):
        self.password_hash = bc.hashpw(password.encode("utf8"), bc.gensalt())

    def verify_password(self, password):
        return bc.checkpw(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"


class Grocery(db.Model):
    __tablename__ = "grocerylist"
    id = db.Column(db.Integer, primary_key=True, nullable=False)  # id column
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))  # noqa: E501
    item = db.Column(
        db.String(16), nullable=False
    )  # grocery list, 500 char max, can't be blank
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Lists {self.id}>"


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, Users, Grocery)
security = Security(app, user_datastore)


# solution for heroku 500 Internal Error: https://stackoverflow.com/a/69814221
@app.before_first_request
def create_tables():
    db.create_all()
    user_datastore.create_user(email="tester@test.com", password="test_pw2")
    db.session.commit()


# main list
@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        grocery_list = request.form["content"]
        new_list = Grocery(content=grocery_list)

        try:
            db.session.add(new_list)
            db.session.commit()
            return redirect("/")

        except Exception:
            return "Unable to updated grocery list, try again!"

    else:
        lists = Grocery.query.order_by(Grocery.date_created).all()
        return render_template("index.html", lists=lists)


# delete function
@app.route("/delete/<int:id>")
def delete(id):
    item_to_delete = Grocery.query.get_or_404(id)

    try:
        db.session.delete(item_to_delete)
        db.session.commit()
        return redirect("/")

    except Exception:
        return "Error: Unable to delete item from list"


# update function
@app.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):
    list = Grocery.query.get_or_404(id)

    if request.method == "POST":
        list.content = request.form["content"]

        try:
            db.session.commit()
            return redirect("/")

        except Exception:
            return "Error: Issue with updating your item"
    else:
        return render_template("update.html", list=list)


if __name__ == "__main__":
    app.run(debug=True)
