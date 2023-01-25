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
import uuid


@login_mgr.user_loader
def load_user(user_id):
    """
    Loader callback for flask session, keeps
    current user object loaded in current session
    based on stored id
    """
    return User.query.get(user_id)


# app object instance
app = create_app()


@app.before_request
def session_handler():
    """
    Set session duration
    """
    session.permanent = True  # prolongs session life
    # max duration of session
    app.permanent_session_lifetime = timedelta(minutes=120)


# homepage
@app.route("/", methods=["GET", "POST"])
def index():
    """
    Homepage will show users own grocery list,
    otherwise redirect to login page
    """

    unique_id = session.get("unique_id", None)  # unique id for db

    if request.method == "POST":
        item = request.form["content"]  # get data from post req
        new_list = Grocery(item=item, user_id=unique_id)  # create item obj

        try:
            db.session.add(new_list)
            db.session.commit()  # push data to db
            return redirect("/")

        except Exception:
            return "Unable to updated grocery list, try again!"

    else:
        # get list of all groceriies for logged in user
        lists = (
            Grocery.query.filter_by(user_id=unique_id)
            .order_by(Grocery.date_updated)
            .all()
        )
        return render_template("index.html", lists=lists, title="myLiist")


# login function
@app.route("/login/", methods=["GET", "POST"], strict_slashes=False)
def login():
    """
    Login page for existing users
    """

    form = LoginForm()  # login form obj

    if form.validate_on_submit():
        try:
            # check for existing email
            user = User.query.filter_by(email=form.email.data).first()

            # if entered pw matches hashed pw in db:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)  # if email found, login as user
                session["unique_id"] = user.id  # apply uuid to session param
                return redirect(url_for("index"))  # return to list page
            else:
                flash("Invalid Username or Password!!!", "danger")
        except Exception as e:
            flash(e, "danger")

    # return auth page
    return render_template(
        "auth.html", form=form, text="Login", title="Login", btn_action="Login"
    )


# register function
@app.route("/register/", methods=["GET", "POST"], strict_slashes=False)
def register():
    """
    Registration page for new user
    """

    form = NewUserForm()  # registration form obj
    if form.validate_on_submit():
        try:
            email = form.email.data  # email
            username = form.username.data  # username
            pw = form.password.data  # pw

            # new user object created with values from above
            newuser = User(
                id=uuid.uuid4(),
                email=email,
                username=username,
                # decode pw before hashing
                password_hash=bcrypt.generate_password_hash(pw).decode("utf8"),
            )

            db.session.add(newuser)
            db.session.commit()  # push data to db
            flash("Account succesfully created", "success")
            return redirect(url_for("login"))

        # apply exceptions
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

    # return auth page
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
    """
    Logs user out of session
    """

    logout_user()
    return redirect(url_for("login"))


# delete function
@app.route("/delete/<int:id>")
def delete(id):
    """
    Route for deleting an item from the list

    Attributes
    ----------
    id : int
        numerical index of item from database
    """

    item_to_delete = Grocery.query.get_or_404(id)

    try:
        db.session.delete(item_to_delete)
        db.session.commit()  # commit deletion to db
        return redirect("/")  # return to list

    except Exception:
        return "Error: Unable to delete item from list"


# update function
@app.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):
    """
    Route that updates an existing item in list

    Attributes
    ----------
    id : int
        numerical index of item in database
    """

    item_to_update = Grocery.query.filter_by(id=id).first()  # get item from db

    if request.method == "POST":

        # update existing item row
        item_to_update.item = request.form["content"]

        try:
            db.session.commit()  # commit changes to db
            return redirect("/")  # return to list

        except Exception:
            return "Error: Issue with updating your item"
    else:
        return render_template("update.html", list=item_to_update)


if __name__ == "__main__":
    app.run(debug=True)
    import logging

    logging.basicConfig(
        format="%(asctime)s [%(threadName)-12.12s] \
            [%(levelname)-5.5s]  %(message)s",
        level=logging.DEBUG,
    )

    console_handler = logging.StreamHandler()

    logger = logging.getLogger()

    logger.addHandler(console_handler)
