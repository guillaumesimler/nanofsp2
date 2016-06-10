"""
*************** models\blogentries.py ***************

This file handles the Blogentries class, storing the related
blog content Google Data Store.

More info in
https://github.com/guillaumesimler/nanofsp2#section7

"""
from google.appengine.ext import db

class Blogentries(db.Model):
    title = db.StringProperty(required=True)
    bodytext = db.TextProperty(required=True)
    contributor = db.StringProperty(required=True)
    date = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now=True)
    likes = db.IntegerProperty(default=0)
    dislikes = db.IntegerProperty(default=0)
    commentsnb = db.IntegerProperty(default=0)
    # This last element is arguably weak (see Readme)
    likers = db.TextProperty()
