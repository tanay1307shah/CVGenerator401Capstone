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

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    create_engine,
    Table,
    Column,
    Integer,
    String,
    MetaData,
    PickleType,
)

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from werkzeug import secure_filename

import os
import json

import en_core_web_sm
import pyresparser
from pyresparser import ResumeParser

import datetime
import numpy as np
import logging
import time
import ast

app = Flask(__name__)
app.secret_key = "secret_key"
app.config["SESSION_TYPE"] = "filesystem"
UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.debug = False
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgres://wxmbglsslzjtsh:9d28f587de43065816914688c5885aca03ee9c9a0d058602ff2063b67bc6a277@ec2-54-235-89-123.compute-1.amazonaws.com:5432/d7lk5jteu84m0e"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

meta = MetaData()
users = Table(
    "users",
    meta,
    Column("id", Integer, primary_key=True),
    Column("username", String),
    Column("password", String),
)

useritems = Table(
    "useritems",
    meta,
    Column("id", Integer, primary_key=True),
    Column("username", String),
    Column("jsonObjAttributes", String),
)

engine = create_engine(
    "postgres://wxmbglsslzjtsh:9d28f587de43065816914688c5885aca03ee9c9a0d058602ff2063b67bc6a277@ec2-54-235-89-123.compute-1.amazonaws.com:5432/d7lk5jteu84m0e",
    echo=True,
)
meta.create_all(engine)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=True)
    password = db.Column(db.String(200))

    def __init__(self, username, password):
        self.username = username
        self.password = password


class Useritem(db.Model):
    __tablename__ = "useritems"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=True)
    jsonObjAttributes = db.Column(db.String(20000))

    def __init__(self, username, jsonObjAttributes):
        self.username = username
        self.jsonObjAttributes = jsonObjAttributes

    def getJson(self):
        return self.jsonObjAttributes


request_session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
request_session.mount("http://", adapter)
request_session.mount("https://", adapter)

def getAllResumes(username):
    if username is None:
        return render_template('login.html', errormsg="Username does not exist")
    else:
        results = db.session.query(Useritem).filter(
            Useritem.username == username).all()

        return results

def getAdminResumes():
    results = db.session.query(Useritem)
    return results
# Index
@app.route("/")
def index():
    return render_template(
        "index.html",
    )


def check_db_for_correct_user(username, password):
    return (
        db.session.query(User).filter(User.username == username).count()
        and db.session.query(User).filter(User.password == password).count()
    )


def check_db_for_existing_user(username):
    return db.session.query(User).filter(User.username == username).count() > 0


def add_to_db(username, password):
    if not check_db_for_existing_user(username):
        data = User(username, password)
        db.session.add(data)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template(
        "register.html", errormsg="This username exists, Please try again"
    )

def add_resume_to_user_db(username, jsonString):
    data = Useritem(username, jsonString)
    db.session.add(data)
    db.session.commit()


# def remove_item_from_user_db(user, deleteid):
#     Useritem.query.filter_by(username=user, itemid=deleteid).delete()
#     db.session.commit()

# Login to use Dashboard
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.values.get("username")  # Your form's

        password = request.values.get("password")  # input names
        if check_db_for_correct_user(username, password):
            session["username"] = username
            return redirect(url_for("dashboard"))
        else:
            return render_template(
                "login.html", errormsg="Username or Password is incorrect"
            )
    else:
        # You probably don't have args at this route with GET
        # method, but if you do, you can access them like so:
        return render_template("login.html")


# Register an Account to use Dashboard
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.values.get("username")  # Your form's
        password = request.values.get("password")  # input names
        return add_to_db(username, password)
    return render_template("register.html")

# Show Dashboard once user has logged in
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    resumes = getAllResumes(session["username"])
    jsonResumes = []
    for resume in resumes:
        jsonResumes.append(json.loads(resume.getJson()))
    return render_template("dashboard.html", resumes = jsonResumes)

# Show Dashboard once user has logged in
@app.route("/adminDashboard", methods=["GET", "POST"])
def adminDashboard():
    resumes = getAdminResumes()
    jsonResumes = []
    for resume in resumes:
        jsonResumes.append(json.loads(resume.getJson()))
    return render_template("adminDashboard.html", resumes = jsonResumes)

# Add item
@app.route("/addItem", methods=["GET", "POST"])
def addItem():
    itemid = request.values.get("itemid")
    add_item_to_user_db(session["username"], itemid)
    return render_template('output.html', output=itemid)

# Remove item
@app.route("/deleteItem", methods=["GET", "POST"])
def deleteItem():
    itemid = request.values.get("id")
    remove_item_from_user_db(session["username"], str(itemid))
    return render_template('output.html')


@app.route("/uploaded", methods=["GET","POST"])
def uploadFile():
    f = request.files['file']
    filename = secure_filename(f.filename)
    f.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
    data = ResumeParser(os.path.join(app.config['UPLOAD_FOLDER'],filename)).get_extracted_data()
    return render_template("create_new.html", parsedData = data)

@app.route("/generateResume",methods=["GET", "POST"])
def generateResume():
    content = request.args
    str_content = json.dumps(content)
    add_resume_to_user_db(session["username"], str_content)
    return str_content

@app.route("/create", methods=["GET", "POST"])
def create():
    return render_template("create_new.html", parsedData = {})

@app.route("/printResume", methods=["GET", "POST"])
def printResume():
    resume = request.args
    json_data = ast.literal_eval(resume['data'])
    jsonString =  json.dumps(json_data)
    jsonResume = json.loads(jsonString)
    return render_template("print.html", resume = jsonResume)

@app.route("/upload", methods=["GET", "POST"])
def upload():
    return render_template("upload.html")

if __name__ == "__main__":
    app.run(debug=True)