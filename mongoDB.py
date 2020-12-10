# Update to suit home_safe database
from flask_mongoengine import MongoEngine

from .__init__ import db


def bool_to_int(v):
    if 'true' in str(v):
        return 1
    elif 'false' in str(v):
        return 0
    else:
        raise ValueError


# users table in our database
class User(db.Document):
    name = db.StringField()
    user_id = db.IntField()
    authkey = db.StringField()
    login = db.IntField()
    read_access = db.IntField()
    write_access = db.IntField()


def delete_all():
    try:
        User.objects({}).delete()
        print("Delete all finished")
    except Exception as e:
        print("Failed " + str(e))


def getUserRowIfExists(user_id):
    get_user_row = User.objects(user_id=user_id).first()
    if (get_user_row != None):
        return get_user_row
    else:
        print("User does not exist")
        return False


def addUserAndLogin(name, user_id):
    row = getUserRowIfExists(user_id)
    if (row != False):
        row.update(login=1)
    else:
        print("Adding user " + name)
        User(name=name, user_id=user_id, authkey=None, login=1, read_access=0, write_access=0).save()
    print("User " + name + " login added")


def addUserPermission(user_id, read, write):
    row = getUserRowIfExists(user_id)
    if row != False:
        row.read_access = bool_to_int(read)
        row.write_access = bool_to_int(write)
        row.update(read_access = row.read_access, write_access = row.write_access)
        print("User permission added")


def userLogout(user_id):
    row = getUserRowIfExists(user_id)
    if (row != False):
        row.update(login = 0)
        print("User " + row.name + "logout updated")


def addAuthKey(user_id, authkey):
    row = getUserRowIfExists(user_id)
    if (row != False):
        row.update(authkey = auth)
        print("User " + row.name + "authkey added")


def getAuthKey(user_id):
    row = getUserRowIfExists(user_id)
    if row != False:
        return row.authkey
    else:
        print("User with id " + user_id + " doesn't exist")


def getUserAccess(user_id):
    row = getUserRowIfExists(user_id)
    if (row != False):
        getUserRow = User.objects(user_id=user_id).first()
        read = getUserRow.read_access
        if read == 1:
            read = True
        else:
            read = False
        ################################
        write = getUserRow.write_access
        if write == 1:
            write = True
        else:
            write = False
    return read, write


def viewAll():
    for user in User.objects():
        print(str(user_id) + " | " +
              user.name + " | " +
              str(user.user_id) + " | " +
              str(user.authkey) + " | " +
              str(user.login))


def getAllLoggedInUsers():
    online_users = User.objects(login=1)
    online_user_record = {"user_record": []}
    print("LoggedIn Users:")
    for user in online_users:
        if user.read_access:
            read = "checked"
        else:
            read = "unchecked"
        if user.write_access:
            write = "checked"
        else:
            write = "unchecked"
        online_user_record["user_record"].append([user.name, user.user_id, read, write])
        print(str(user.id) + " | " +
              user.name + " | " +
              str(user.user_id) + " | " +
              str(user.authkey) + " | " +
              str(user.read_access) + " | " +
              str(user.write_access))
    return online_user_record

