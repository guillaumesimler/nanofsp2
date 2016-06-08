# ----- Multi User Block -----
#
#  A Program by Guillaume Simler


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!! Libraries + "init" !!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# Libraries:
# jinja2 (templating lib), webapp2 (main GAE library) &
# db (Datastore) are linked to Google App Engine (GAE)


import os
import jinja2
import webapp2
import re
import security


from google.appengine.ext import db

# initialize Jinja:
#   - it defines the folder to store the templates /templates/
#   - loads the template(s) into Jinja2
#   - automate the HTML escaping

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                            autoescape= True)



# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!! GAE Helper Classes !!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


# classic HTML write order from GAE

class Handler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    # Load the templates
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    # ------- Personal Addition: cookie validation -------
    def render_newpost(self, title="", bodytext="", error="", user=""):
        user = self.get_user()
        self.render("04_newpost.html", title = title, bodytext = bodytext,
                     error = error, user = user)

    def checkcookie(self):
        cookie = self.request.cookies.get('id')

        if not cookie or not security.check_cookie(cookie):
            q = "Please log in"
            self.redirect('/blog/login?q=' + q)

    def get_user(self):
        cookie = self.request.cookies.get('id')

        if cookie and security.check_cookie(cookie):
            cookie = int(cookie.split('|')[0])

            username = UserData.get_by_id(cookie).Username

            return username

    def get_blogentry(self, keyid):

        key = db.Key.from_path('Blogentries', int(keyid))
        blogentry = db.get(key)

        return blogentry


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!! DataStore Classes !!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# Create the entity (Google Datastore's table)
# (for more info - please check the readme )

class Blogentries(db.Model):
    title = db.StringProperty(required = True)
    bodytext = db.TextProperty(required = True)
    contributor = db.StringProperty(required = True)
    date = db.DateTimeProperty(auto_now_add = True)
    modified = db.DateTimeProperty(auto_now = True)
    likes = db.IntegerProperty(default= 0)
    dislikes = db.IntegerProperty(default= 0)
    commentsnb = db.IntegerProperty(default= 0)


class PostComments(db.Model):
    postkey = db.IntegerProperty(required = True)
    author = db.StringProperty(required = True)
    comment = db.TextProperty(required = True)
    date = db.DateTimeProperty(auto_now_add = True)

    @classmethod
    def by_postkey(self, id):
        k = PostComments.all().filter('postkey =', int(id)).order('-date').fetch(100)
        return k


class UserData(db.Model):
    Username = db.StringProperty(required = True)
    hPassword = db.StringProperty(required = True)
    Email = db.StringProperty()

    @classmethod
    def by_id(self, uid):
        return UserData.get_by_id(uid)

    @classmethod
    def by_name(self, name):
        k = UserData.all().filter('Username =', name).fetch(1)
        return k


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!! Main Classes !!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# --------------------   Page display Section        --------------------

class NewPost(Handler):

    def get(self):
        self.checkcookie()
        username = self.get_user()
        self.render_newpost()

    def post(self):

        title = self.request.get("title")
        bodytext = self.request.get("bodytext")
        edit = self.request.get("edit")

        username = self.get_user()


        if bodytext and title:
            if edit == "edit":
                b = Blogentries(title= title, bodytext=bodytext,
                                contributor=username)
                b.put()

                key = b.key().id()

                self.redirect('/blog/%s' % str(key))

            else:
                self.redirect('/blog')

        else:
            error = "Something went wrong. The title or the bodytext were not filled"

            self.render_newpost(title, bodytext, error)


class SinglePost(Handler):


    def get(self, keyid):
        self.checkcookie()
        username = self.get_user()

        blogentry = self.get_blogentry(keyid)

        comments = PostComments.by_postkey(keyid)

        q = self.request.get('q')

        if q == 'no':
            error = "Nice try, but it's your post !!!!"
        else:
            error = ''

        if not blogentry:
            self.error(404)

        self.render("03_singlepost.html", blogentry = blogentry,
                    username = username, comments = comments, 
                    error = error, user = username)


    def post(self, keyid):
        blogentry = self.get_blogentry(keyid)

        self.redirect("/blog/edit?q=" + str(blogentry.key().id()))


class SingleEdit(Handler):
    def init(self):
        self.checkcookie()
        username = self.get_user()

        keyid = self.request.get('q')
        blogentry = self.get_blogentry(keyid)

        return [blogentry, keyid, username]


    def get(self):

        init_val = self.init()
        
        blogentry = init_val[0]
        username = init_val[2]

        if blogentry:
            self.render_newpost(title = blogentry.title,
                                bodytext = blogentry.bodytext,
                                error = "in Editing Mode",
                                user = username)

        else:
            self.redirect('/blog')


    def post(self):

        init_val = self.init()
        
        blogentry = init_val[0]
        keyid = init_val[1]
        username = init_val[2]
        
        edit = self.request.get("edit")

        if edit == "edit":
            title = self.request.get("title")
            bodytext = self.request.get("bodytext")

            blogentry.title = title
            blogentry.bodytext = bodytext

            blogentry.put()

            self.redirect('/blog/' + str(keyid))

        elif edit == "delete":

            k = Blogentries.delete(blogentry)

            
        self.redirect('/blog')


class MainPage(Handler):

    def get(self):

        blogentries= db.GqlQuery("SELECT * FROM Blogentries ORDER BY date DESC LIMIT 10")

        username = self.get_user()

        self.render("02_front-page.html", blogentries = blogentries,
                    user = username)


# --------------------    Login & register Section        --------------------

# Helper function for register
# These functions will check for the undesired properties
# and return an error message or an empty

def check_user(username, error_message = ''):

    # Check n1: matching principles
    # - only digits or letter
    # - min 6 digits
    user_re = re.compile(r"^[a-zA-Z0-9_-]{6,20}$")

    if not user_re.match(username):
        error_message = 'The username does not fit the requirements'

    # Check n2: absence of identical entry
    k = UserData.by_name(username)

    if k:
        error_message = 'This username is already used'

    return error_message


def check_fir_pass(fir_password, error_message = ''):

    # Check n3: matching principles (min 6 characters)
    fir_re = re.compile(r"^.{6,20}$")

    if not fir_re.match(fir_password):
        error_message = "Your password is invalid"

    return error_message


def check_sec_pass(fir_password, sec_password, error_message=''):

    # check n4: password confirmation.
    # It is a simplified version. I don't check for the empty string
    # as the previous check will refuse such an entry and if the second
    # string would be '', it could not match to the first

    if fir_password != sec_password:
        error_message = "Your passwords don't match"

    return error_message


def check_email(email, error_message=''):

    # check n4: matching principles (only for entry)
    email_re = re.compile(r"^[\S]+@[\S]+.[\S]+$")

    if email and not email_re.match(email):
        error_message = "are you sure it is an email?"

    return error_message


def check_disclaimer(disclaimer, error_message=''):
    # check n4: verify the box was checked
    if disclaimer != 'on':
        error_message = 'Please accept the conditions to access the blog'

    return error_message


# RegisterPage

class Register(Handler):

    def get(self):
        self.render("12_register.html", errors = '', values= '')

    def post(self):
        username = self.request.get('username')
        fir_password = self.request.get('fir_password')
        sec_password = self.request.get('sec_password')
        email = self.request.get('email')
        disclaimer = self.request.get('disclaimer')

        # As I choose to work with indexes (had a problem with
        # dict), value is build symatrically to errors, the
        # following list. The '' "fake" the structure

        values = [username,
                  '',
                  '',
                  email,
                  '']

        # Run the checks and append the results to the list
        errors = [check_user(username),
                  check_fir_pass(fir_password),
                  check_sec_pass(fir_password, sec_password),
                  check_email(email),
                  check_disclaimer(disclaimer)]


        # Check for errors: if yes, at least one error won't be ''
        mover = True

        for error in errors:
            if error != '':
                mover = False

       # implement the input


        if mover:

            # create the password
            hPassword = security.make_pw_hash(username, fir_password)

            # create the database entry
            a = UserData(Username= username, hPassword = hPassword, Email = email)
            a.put()

            # encode the cookie
            key = str(a.key().id())
            new_cookie = security.encode_cookie(key)


            self.response.headers.add_header('Set-Cookie', 'id=%s; Path=/' % new_cookie)

            self.redirect('/blog')
        else:
            self.render("12_register.html", errors = errors, values = values)


class Login(Handler):

    def get(self):
        # This line is linked to Logout. I would push a message in q
        error = self.request.get('q')
        self.render("11_login.html", error=error)

    def post(self):

        # Get the data from the form
        username = self.request.get("username")
        password = self.request.get("password")

        # Get the database entry
        check_name = UserData.by_name(username)

        # Run the security test:
        # 1. there must be a registered user
        # 2. the password must be verified

        if check_name and security.check_pw(username, password, check_name[0].hPassword):
           # creates a secure cookie in case the tests succeed
            key = str(check_name[0].key().id())
            new_cookie = security.encode_cookie(key)

            self.response.headers.add_header('Set-Cookie', 'id=%s; Path=/' % new_cookie)

            self.redirect('/blog')
        else:
            # redirect to the login page with an error message
            # I clearly deviate from the original assignment as I don't
            # specify which element is wrong.
            # So a hacker can't know which part is right.
            self.render("11_login.html", error = 'no valid username or password')


class Logout(Handler):

    def get(self):

        # The principle is easy: the logout function
        # resets the cookie to a blank value (which would fail the
        # security tests) and redirect the user to the login page
        self.response.headers.add_header('Set-Cookie', 'id= ; Path=/')

        q = "You've been logged out"
        self.redirect('/blog/login?q=%s' %q)

# --------------------------------    Comment Section        ---------------------------------

class Like(Handler):

    def get(self):
        q = self.request.get('q')

        post = Blogentries.get_by_id(int(q))

        if post.contributor == self.get_user():
            error = "no"
            self.redirect('/blog/%s?q=%s' %(q, error))


        else:
            post.likes += 1
            post.put()

            self.redirect('/blog/%s' %q)


class Dislike(Handler):

    def get(self):
        q = self.request.get('q')

        post = Blogentries.get_by_id(int(q))

        if post.contributor == self.get_user():
            error = "no"
            self.redirect('/blog/%s?q=%s' %(q, error))

        else:
            post.dislikes += 1
            post.put()

            self.redirect('/blog/%s' %q)


class AddComment(Handler):
    
    def get(self):
        self.checkcookie()
        q = self.request.get('q')
        blogentry = self.get_blogentry(q)

        username = self.get_user()

        self.render("05_newcomment.html", blogentry = blogentry, comment = '', user = username)

    def post(self):
        q = self.request.get('q')
        blogentry = self.get_blogentry(q)

        edit = self.request.get('edit')

        author = self.get_user()
        comment = self.request.get('comment')

        if edit == 'edit' and comment:
            #Increment comment counter
            c = PostComments(postkey = int(q), author = author, comment = comment)
            c.put()

            blogentry = self.get_blogentry(q)
            blogentry.commentsnb += 1
            blogentry.put()

        
        self.redirect('/blog/%s' %q)



class EditComment(Handler):
    def init(self):
        self.checkcookie()
        q = self.request.get('q')
        r = self.request.get('r')

        blogentry = self.get_blogentry(q)
        commententry = PostComments.get_by_id(int(r))

        username = self.get_user()

        return [blogentry, commententry, username]
    
    def get(self):
        
        init_val = self.init()

        self.render("05_newcomment.html", blogentry = init_val[0], 
                    comment = init_val[1].comment, user = init_val[2], 
                    error = "in Editing Mode")

    def post(self):
        
        init_val = self.init()
        
        comment = self.request.get('comment')
        edit = self.request.get('edit')

        if edit == 'edit' and comment:
            #Increment comment counter
            init_val[1].comment = comment
            init_val[1].put()

        if edit == 'delete' or not comment:
            c = init_val[1]
            c = PostComments.delete(c)

            init_val[0].commentsnb = init_val[0].commentsnb -1
            init_val[0].put()

        
        self.redirect('/blog/%s' %init_val[0].key().id())
       
# --------------------------------    Legacy Section        ---------------------------------

class Welcome(Handler):

    def get(self):

        cookie = self.request.cookies.get('id')


        if security.check_cookie(cookie):
            cookie = int(cookie.split('|')[0])

            username = UserData.get_by_id(cookie)

            self.write('<h1> Hello, ' + username.Username + '</h1>')

        else:
            self.write('<h1>Bug</h1>')


# --------------------------------    Debug Section        ---------------------------------
# helper functions to debug

def cleanupDb(key):
    k = UserData.delete(UserData.get_by_id(key))


class Debug(Handler):

    def get(self):

        # first checkS
        name = 'Werther'

        k1 = UserData.all().filter('Username =', name).fetch(10)

        # Usedata content

        k2 = db.GqlQuery("SELECT * FROM UserData ORDER BY Username")


       # Blog content

        k3 = 'solved'

        # Comments


        k4 = PostComments.all().fetch(10)


        self.render('99_debug.html', k1= k1, k2= k2, k3 = k3, k4 = k4)

# ------------------------------------------------------------------------------------------

# Function triggering the page generation
app = webapp2.WSGIApplication([
                             ('/blog', MainPage),
                             ('/blog/newpost', NewPost),
                             ('/blog/([0-9]+)', SinglePost),
                             ('/blog/edit', SingleEdit),
                             ('/blog/comment', AddComment),
                             ('/blog/editcomment', EditComment),
                             ('/blog/like', Like),
                             ('/blog/dislike', Dislike),
                             ('/blog/register', Register),
                             ('/blog/login', Login),
                             ('/blog/logout', Logout),
                             ('/blog/welcome', Welcome),
                             ('/blog/debug', Debug)
                            ],
debug=True)


