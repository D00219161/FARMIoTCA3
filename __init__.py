from flask import Flask, render_template, url_for, session, flash
import json, string, random, hashlib

# Mongo Database import connection
from flask_mongoengine import MongoEngine
#import pymongo
#from pymongo import MongoClient
#import dnspython

from functools import wraps
from werkzeug.utils import redirect

app = Flask(__name__)

# Mongo DB Connection
#cluster = MongoClient("mongodb+srv://Roisin:DFM5CauDv8K9tXpY@cluster0.b528o.mongodb.net/home_safe?retryWrites=true&w=majority")
#db = cluster["home_safe"]
#collection = db["electricity_usage"], db["temp_usage"], db["users"]
#db = cluster(app)

# Mongo Database Config
app.config['MONGOBD_SETTINGS']={
    'db':'home_safe',  # will use test
    'host':'localhost',
    'port':27017
}
db = MongoEngine()
db.init_app(app)

#from . import homesafeDB, temperatureDB, electricityDB, PB
from . import PB, mongoDB

alive = 0
data = {}

# Grant read and write access to the authkey "SD3b-Raspberry-Pi" - More than One Pi
PB.grant_access("Homesafe-Matthew-Raspberry-Pi", True, True)  # Matthew's Pi Connection to read & write
PB.grant_access("Homesafe-Finbar-Raspberry-Pi", True, True)  # Finbar's Pi Connection to read & write


@app.route("/")
def index():
    clear_user_session()
    return render_template("index.html")


# User login
@app.route("/user_login")
def user_login():
    if not User.authorised:
        print("Not authorized, redirecting....")
        return redirect(url_for('create.html'))

    account_info = User.get('/me')
    if account_info.ok:
        print("User Logged In")
        me = account_info.json()
        session['logged_in'] = True
        session['user'] = me['name']
        session['user_id'] = me['id']
        return redirect(url_for('main'))

    return redirect(url_for('index'))


def clear_user_session():
    session['logged_in'] = None
    session['user'] = None
    session['user_id'] = None


@app.route("/", methods = ['POST', 'GET'])
def login():
    clear_user_session()
    render_template("index.html")


def LoginRequired(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'logged_in' in session:
            if session['logged_in']:
                return f(*args, **kwargs)
        flash("Please login first")
        return redirect(url_for('index'))

    return wrapper


# Create account route
@app.route("/create")
def create():
    return render_template("create.html")


# Dashboard route
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# Electricity route
@app.route("/electricity")
def electricity():
    return render_template("electricity.html")


# Temperature route
@app.route("/temperature")
def temperature():
    return render_template("temperature.html")


# Settings route
@app.route("/settings")
def settings():
    return render_template("settings.html")


# Notification route
@app.route("/notification")
def notification():
    return render_template("notification.html")


# Running Bill route
@app.route("/runningbill")
def runningbill():
    return render_template("runningbill.html")


# James View ( Secondary User - avgtemperature & avgelectricity routes)
@app.route("/avgtemperature")
def average_temperature():
    return render_template("avgtemperature.html")


@app.route("/avgelectricity")
def average_electricity():
    return render_template("avgelectricity.html")


# Logout route
@app.route("/logout")
@LoginRequired
def logout():
    mongoDB.userLogout(session['user_id'])
    mongoDB.viewAll()
    clear_user_session()
    flash("You just logged out")
    return redirect(url_for("/"))


# Required route
@app.route("/main")
@LoginRequired
def main():
    flash(session["user"])
    mongoDB.addUserAndLogin(session['user'], int(session['user_id']))
    mongoDB.viewAll()
    return render_template("index.html", user_id=session['user_id'], online_users=mongoDB.getAllLoggedInUsers())


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
