from flask import Flask, render_template, url_for, session, flash, request
import json, string, random, hashlib

# Mongo Database import connection
from flask_pymongo import pymongo

from functools import wraps
from werkzeug.utils import redirect

app = Flask(__name__)


# Mongo DB Connection in db.py file

from . import db, PB

alive = 0
data = {}

# Grant read and write access to the authkey "SD3b-Raspberry-Pi" - More than One Pi
PB.grant_access("Homesafe-Matthew-Raspberry-Pi", True, True)  # Matthew's Pi Connection to read & write
PB.grant_access("Homesafe-Finbar-Raspberry-Pi", True, True)  # Finbar's Pi Connection to read & write
PB.grant_access("Homesafe-Aisling-Raspberry-Pi", True, True)  # Aisling's Pi Connection to read & write
PB.grant_access("Homesafe-Roisin-Raspberry-Pi", True, True)  # Roisin's Pi Connection to read & write
PB.grant_access("FarmCharts", True, True)  # Roisin's Pi Connection to read & write

# test to insert data to the data base
@app.route("/test")
def test():
    db.db.user.insert_one({"name":"Roisin"})
    return "Connected to the database"


@app.route("/", methods=['POST', 'GET'])
def index():
    # if 'firstName' in session:
    #     return 'You are logged in as ' + session['firstName']
    return render_template("index.html")
    #db.db.users.find({'firstName' : request.form.get('firstName'), 'password' : request.form.get('password')})
    #clear_user_session()
    #return render_template("index.html")


def clear_user_session():
    session['firstName'] = None
    session['password'] = None
    #session['user_id'] = None


def LoginRequired(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if db.db.users.find_one({'firstName': 'firstName'}):
            return f(*args, **kwargs)
            return 'User there'
        else:
            flash("Please login first")
            return redirect(url_for('index'))
    return wrapper


# Create account route
@app.route("/create", methods=['POST', 'GET'])
def create():
    db.db.users.insert({'firstName': request.form.get('firstName'), 'surname': request.form.get('surname'),
    'address': request.form.get('address'), 'dateOfBirth': request.form.get('dateOfBirth'),
    'emailAddress': request.form.get('emailAddress'), 'gender': request.form.get('gender'), 'password': request.form.get('password'),
    'phoneNumber': request.form.get('phoneNumber'), 'postCode': request.form.get('postCode')})
    return render_template("create.html")


# Dashboard route
@app.route("/dashboard")
#@LoginRequired
def dashboard():
    return render_template("dashboard.html")


# Electricity route
@app.route("/electricity")
#@LoginRequired
def electricity():
    return render_template("electricity.html")


# Temperature route
@app.route("/temperature")
#@LoginRequired
def temperature():
    return render_template("temperature.html")


# Settings route
@app.route("/settings")
#@LoginRequired
def settings():
    return render_template("settings.html")


# Running Bill route
@app.route("/runningbill")
#@LoginRequired
def runningbill():
    return render_template("runningbill.html")


@app.route("/colorscheme")
#@LoginRequired
def colorscheme():
    return render_template("colorscheme.html")


# James View ( Secondary User )
# avgtemperature route
@app.route("/avgtemperature")
# @LoginRequired
def average_temperature():
    return render_template("avgtemperature.html")


# avgelectricity route
@app.route("/avgelectricity")
# @LoginRequired
def average_electricity():
    return render_template("avgelectricity.html")


# Color Scheme James route
@app.route("/colorschemejames")
# @LoginRequired
def colorschemejames():
    return render_template("colorschemejames.html")


# Notification route
@app.route("/notification")
#@LoginRequired
def notification():
    return render_template("notification.html")


# Logout route
@app.route("/logout")
#@LoginRequired
def logout():
    clear_user_session()
    flash("You just logged out")
    return redirect(url_for("/main"))


# Required route
@app.route("/main")
#@LoginRequired
def main():
    return render_template("index.html")


def str_to_bool(s):
    if 'true' in str(s):
        return True
    elif 'false' in str(s):
        return False
    else:
        raise ValueError


@app.route("/grant-<user_id>-<read>-<write>", methods=["POST", "GET"])
def grant_access(user_id, read, write):
    if int(session['user_id']) == 1884560171685373:
        print("Granting " + user_id + " read: " + read + " write: " + write + " permission")
        # store user read/write permissions into the database
        mongoDB.addUserPermission(user_id, read, write)
        auth_key = mongoDB.getAuthKey(user_id)
        # grant PubNub read/write access
        PB.grant_access(auth_key, str_to_bool(read), str_to_bool(write))
    else:
        print("Who are you?")
        return json.dumps({"access":"denied"})
    return json.dumps({"access":"granted"})


# Salting
def salt(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


# Creating auth key for user
def create_auth_key():
    s = salt(10)
    hashing = hashlib.sha256((str(session['user_id']) + s).encode('utf-8'))
    return hashing.hexdigest()


@app.route("/get_auth_Key", methods=["POST", "GET"])
def get_auth_key():
    print("Creating authkey for " + session['user'])
    auth_key = create_auth_key()
    mongoDB.addAuthKey(int(session['user_id']), auth_key)
    (read, write) = mongoDB.getUserAccess(int(session['user_id']))
    # Use PubNub to grant these privileges to this user
    PB.grant_access(auth_key, read, write)
    auth_response = {"authKey":auth_key, "cipherKey":PB.cipherKey}
    json_response = json.dumps(auth_response)
    return str(json_response)
    return str("authkey")


if __name__ == "__main__":
    app.run()
