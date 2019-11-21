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
@app.route("/index")
def index():
    return render_template("index.html")

# Login to use Dashboard
@app.route("/", methods=["GET", "POST"])
def login():
    return render_template(
        "login.html"
    )

@app.route("/verifyLogin", methods=["POST"])
def verifylogin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('pass')
    return {1: username,2: password}



@app.route("/uploaded",methods=["GET","POST"])
def uploadFile():
        f = request.files['file']
        filename = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
        data = ResumeParser(os.path.join(app.config['UPLOAD_FOLDER'],filename)).get_extracted_data()
        return render_template("updateInfo.html", parsedData = data)
 
@app.route("/generateResume",methods=["POST"])
def generateResume():
    return request.args

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
