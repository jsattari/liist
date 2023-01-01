#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from flask import render_template, redirect, flash, url_for, session, request

from datetime import timedelta
from sqlalchemy.exc import (
    IntegrityError,
    DataError,
    DatabaseError,
    InterfaceError,
    InvalidRequestError,
)
from werkzeug.routing import BuildError


from flask_bcrypt import check_password_hash

from flask_login import (
    login_user,
    logout_user,
    login_required,
)

from app import create_app, db, login_mgr, bcrypt
from models import User, Grocery
from forms import LoginForm, NewUserForm


@login_mgr.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


app = create_app()


@app.before_request
def session_handler():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=120)


# homepage
@app.route("/", methods=["GET", "POST"])
def index():
    username = session.get("username", None)
    if request.method == "POST":
        item = request.form["content"]
        new_list = Grocery(item=item, username=username)

        try:
            db.session.add(new_list)
            db.session.commit()
            return redirect("/")

        except Exception:
            return "Unable to updated grocery list, try again!"

    else:
        lists = (
            Grocery.query.filter_by(username=username)
            .order_by(Grocery.date_updated)
            .all()
        )
        return render_template("index.html", lists=lists, title="myLiist")


# login function
@app.route("/login/", methods=["GET", "POST"], strict_slashes=False)
def login():
    form = LoginForm()

    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                session["username"] = user.username
                return redirect(url_for("index"))
            else:
                flash("Invalid Username or Password!!!", "danger")
        except Exception as e:
            flash(e, "danger")
    return render_template(
        "auth.html", form=form, text="Login", title="Login", btn_action="Login"
    )


# register function
@app.route("/register/", methods=["GET", "POST"], strict_slashes=False)
def register():
    form = NewUserForm()
    if form.validate_on_submit():
        try:
            email = form.email.data
            username = form.username.data
            pw = form.password.data

            newuser = User(
                email=email,
                username=username,
                password_hash=bcrypt.generate_password_hash(pw).decode("utf8"),
            )

            db.session.add(newuser)
            db.session.commit()
            flash("Account succesfully created", "success")
            return redirect(url_for("login"))

        except InvalidRequestError:
            db.session.rollback()
            flash("Something went wrong!", "danger")
        except IntegrityError:
            db.session.rollback()
            flash("Email or Username already exists!.", "warning")
        except DataError:
            db.session.rollback()
            flash("Invalid Entry", "warning")
        except InterfaceError:
            db.session.rollback()
            flash("Error connecting to the database", "danger")
        except DatabaseError:
            db.session.rollback()
            flash("Error connecting to the database", "danger")
        except BuildError:
            db.session.rollback()
            flash("An error occured !", "danger")
    return render_template(
        "auth.html",
        form=form,
        title="Register For Liist!",
        btn_action="Create account",
    )


# logout function
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


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
