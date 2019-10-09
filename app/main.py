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
@app.route("/register", methods=["GET", "POST"])
def register():
    return render_template("register.html")

# Show Dashboard once user has logged in
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    return render_template("dashboard.html")


if __name__ == "__main__":
    app.run(debug=True)
