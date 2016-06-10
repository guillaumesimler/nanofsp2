"""
*************** models\userdata.py ***************

This file handles the Userdata class, storing the related
User info Googel Data Store.

More info in
https://github.com/guillaumesimler/nanofsp2#section7

"""
from google.appengine.ext import db

class UserData(db.Model):
    Username = db.StringProperty(required=True)
    hPassword = db.StringProperty(required=True)
    Email = db.StringProperty()

    @classmethod
    def by_id(self, uid):
        return UserData.get_by_id(uid)

    @classmethod
    def by_name(self, name):
        k = UserData.all().filter('Username =', name).fetch(1)
        return k