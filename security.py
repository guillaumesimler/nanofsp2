# ----- Multi User Block -----
# ----- Security.py ------
#
#
#  For obvious security reasons, the security management is
#  outside the main file
#
#  A Program by Guillaume Simlerimport random
import string
import hashlib
import hmac


# Cookie encoding

codeword = "qd8qfem2eq4r52+tu"


def hash_cookie(id):
    return hmac.new(codeword, id).hexdigest()


def encode_cookie(id):
    return "%s|%s" % (id, hash_cookie(id))


def check_cookie(cookieval):
    temp = cookieval.split('|')[0]

    return cookieval == encode_cookie(temp)


# Password encoding


def make_salt():
    return ''.join((random.choice(string.letters)) for x in xrange(5))


def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()

    h = hashlib.sha256(name + pw + salt).hexdigest()

    return '%s|%s' % (h, salt)


def check_pw(name, pw, h):

    salt = h.split('|')[1]
    return h == make_pw_hash(name, pw, salt)
