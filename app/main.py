from flask import (
    Flask,
    render_template,
    flash,
    redirect,
    url_for,
    session,
    request,
    logging,
)

import requests
import logging

app = Flask(__name__)
# Index
@app.route("/")
def index():
    return render_template("index.html")

# Login to use Dashboard
@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template(
        "login.html"
    )

# Register an Account to use Dashboard
@app.route("/create", methods=["GET", "POST"])
def create():
    return render_template("create_new.html")

# Show Dashboard once user has logged in
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    return render_template("cv_display.html")


@app.route("/select", methods=["GET", "POST"])
def select():
    return render_template("select_cv.html")


@app.route("/upload", methods=["GET", "POST"])
def upload():
    return render_template("upload.html")


@app.route("/display", methods=["GET", "POST"])
def display():
    return render_template("cv_display.html")


if __name__ == "__main__":
    app.run(debug=True)
