"""
*************** models\postcomments.py ***************

This file handles the Postcomments class, storing the related
comments content Google Data Store.

More info in
https://github.com/guillaumesimler/nanofsp2#section7

"""
from google.appengine.ext import db

class PostComments(db.Model):
    postkey = db.IntegerProperty(required=True)
    author = db.StringProperty(required=True)
    comment = db.TextProperty(required=True)
    date = db.DateTimeProperty(auto_now_add=True)

    @classmethod
    def by_postkey(self, id):
        k = PostComments.all().filter(
            'postkey =', int(id)).order('-date').fetch(100)
        return k
