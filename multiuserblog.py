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
        self.render("04_newpost.html", title = title, bodytext = bodytext, error = error, user = user)

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
    likes = db.IntegerProperty()
    dislikes = db.IntegerProperty()
    comments = db.IntegerProperty()


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
                b = Blogentries(title= title, bodytext=bodytext, contributor=username)
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

        if not blogentry:
            self.error(404)

        self.render("03_singlepost.html", blogentry = blogentry, username = username, user = username)


    def post(self, keyid):
        blogentry = self.get_blogentry(keyid)

        self.redirect("/blog/edit?q=" + str(blogentry.key().id()))


class SingleEdit(Handler):


    def get(self):

        self.checkcookie()
        username = self.get_user()

        keyid = self.request.get('q')
        blogentry = self.get_blogentry(keyid)

        if blogentry:
            self.render_newpost(title = blogentry.title, bodytext = blogentry.bodytext, error = "in Editing Mode", user = username)
        
        else:
            self.redirect('/blog')



    def post(self):

        keyid = int(self.request.get("q"))
        blogentry = self.get_blogentry(keyid)

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
        self.checkcookie()

        blogentries= db.GqlQuery("SELECT * FROM Blogentries ORDER BY date DESC LIMIT 10")

        username = self.get_user()

        self.render("02_front-page.html", blogentries = blogentries, user = username)


# --------------------    Login & register Section        --------------------

# Helper function for register

def check_user(username, error_message = ''):
    user_re = re.compile(r"^[a-zA-Z0-9_-]{6,20}$")

    if not user_re.match(username):
        error_message = 'The username does not fit the requirements'

    k = UserData.by_name(username)
    
    if k:
        error_message = 'This username is already used'

    return error_message


def check_fir_pass(fir_password, error_message = ''):
    fir_re = re.compile(r"^.{6,20}$")

    if not fir_re.match(fir_password):
        error_message = "Your password is invalid"

    return error_message


def check_sec_pass(fir_password, sec_password, error_message=''):
    if not fir_password or not sec_password or fir_password != sec_password:
        error_message = "Your passwords don't match"

    return error_message


def check_email(email, error_message=''):
    email_re = re.compile(r"^[\S]+@[\S]+.[\S]+$")

    if email and not email_re.match(email):
        error_message = "are you sure it is an email?"

    return error_message


def check_disclaimer(disclaimer, error_message=''):
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

        values = [username,
                  '',
                  '',
                  email]       

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
            self.render("10_register.html", errors = errors, values = values) 


class Login(Handler):

    def get(self):
        error = self.request.get('q')
        self.render("11_login.html", error=error)

    def post(self):

        username = self.request.get("username")
        password = self.request.get("password")

        check_name = UserData.by_name(username)[0]
        
        if check_name and security.check_pw(username, password, check_name.hPassword):
            key = str(check_name.key().id())
            new_cookie = security.encode_cookie(key)

            self.response.headers.add_header('Set-Cookie', 'id=%s; Path=/' % new_cookie)

            self.redirect('/blog')
        else:
            self.render("11_login.html", error = 'no valid username or password')


class Logout(Handler):

    def get(self):
        self.response.headers.add_header('Set-Cookie', 'id= ; Path=/')

        q = "You've been logged out"
        self.redirect('/blog/login?q=' + q)

# --------------------------------    Comment Section        ---------------------------------

class Like(Handler):
    def get (self):
        q = self.request.get('q')

        post = Blogentries.get_by_id(int(q))

        if post.likes:
            post.likes += 1
        else:
            post.likes = 1

        post.put()

        self.redirect('/blog/%s' %q)


class Dislike(Handler):
    def get (self):
        q = self.request.get('q')

        post = Blogentries.get_by_id(int(q))

        if post.dislikes:
            post.dislikes += 1
        else:
            post.dislikes = 1

        post.put()

        self.redirect('/blog/%s' %q)
        
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

        k2 = db.GqlQuery("SELECT * FROM UserData ORDER BY Username")

        self.render('99_debug.html', k1= k1, k2= k2)

# ------------------------------------------------------------------------------------------

# Function triggering the page generation
app = webapp2.WSGIApplication([
                             ('/blog', MainPage),
                             ('/blog/newpost', NewPost),
                             ('/blog/([0-9]+)', SinglePost),
                             ('/blog/edit', SingleEdit),
                             ('/blog/like', Like),
                             ('/blog/dislike', Dislike),
                             ('/blog/register', Register),
                             ('/blog/login', Login),
                             ('/blog/logout', Logout),
                             ('/blog/welcome', Welcome),
                             ('/blog/debug', Debug)
                            ],
debug=True)


