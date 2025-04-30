from flask import Blueprint, render_template, session, redirect

home_bp = Blueprint('home', __name__)


@home_bp.route('/')
def homepage():
    user_email = session.get("email")
    return render_template('index.html', user_email=user_email)
@home_bp.route("/signup")
def signup_page():
    user_email = session.get("email")
    return render_template("signup.html", user_email=user_email)
@home_bp.route("/login")
def login_page():
    user_email = session.get("email")
    return render_template("login.html", user_email=user_email)
@home_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")