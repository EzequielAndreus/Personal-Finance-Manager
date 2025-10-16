from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Login view"""
    if "user_id" in session:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session["user_id"] = user.id
            session["username"] = user.username
            session["is_admin"] = user.is_admin
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(url_for("dashboard.index"))
        else:
            flash("Invalid username or password", "danger")

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    """Logout route"""
    username = session.get("username", "User")
    session.clear()
    flash(f"Goodbye, {username}!", "info")
    return redirect(url_for("auth.login"))
