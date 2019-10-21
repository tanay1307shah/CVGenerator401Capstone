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
from werkzeug import secure_filename
from pyresparser import ResumeParser
import nltk
import requests
import logging
import os



app = Flask(__name__)
UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
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


@app.route("/upload",methods=["POST"])
def uploadFile():
    if request.method == 'POST':
        f = request.files['file']
        filename = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
        data = ResumeParser(os.path.join(app.config['UPLOAD_FOLDER'],filename)).get_extracted_data()
      
    return data

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
