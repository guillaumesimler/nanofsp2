# ----- Multi User Block -----
#
#  A Program by Guillaume Simler



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


#Helper Class (reduce work in handler)

class Handler(webapp2.RequestHandler):
    # classic HTML write order from GAE
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    # Load the templates
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

# Create the entity (Google Datastore's table)
# (for more info - please check the readme )

class Blogentries(db.Model):
    title = db.StringProperty(required = True)
    bodytext = db.TextProperty(required = True)
    contributor = db.StringProperty(required = True)
    date = db.DateTimeProperty(auto_now_add = True)
    modified = db.DateTimeProperty(auto_now = True)


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

# Main Classes

class NewPostHandler(Handler):
    def render_newpost(self, title="", bodytext="", error=""):
        self.render("newpost.html", title = title, bodytext = bodytext, error = error)

    def get(self):
        self.render_newpost()

    def post(self):

        title = self.request.get("title")
        bodytext = self.request.get("bodytext")

        if bodytext and title:
            b = Blogentries(title= title, bodytext=bodytext, contributor="Guillaume")
            b.put()

            key = b.key().id()

            self.redirect('/blog/%s' % str(key))

        else:
            error = "Something went wrong. The title or the bodytext were not filled"

            self.render_newpost(title, bodytext, error)


class NewPostDisplay(Handler):
    def get(self, keyid):

        key = db.Key.from_path('Blogentries', int(keyid))
        blogentry = db.get(key)

        if not blogentry:
            self.error(404)


        self.render("single_entry.html", blogentry = blogentry)


# Helper function for  register

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

class RegisterPage(Handler):

    
    def get(self):
        self.render("register.html", errors = '', values= '')

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
            hPassword = security.make_pw_hash(username, fir_password)
            a = UserData(Username= username, hPassword = hPassword, Email = email)
            a.put()
            
            self.redirect('/blog/welcome?username=' + username)
        else:    
            self.render("register.html", errors = errors, values = values) 



class Welcome(Handler):

    def get(self):

        username = self.request.get('username')

        self.write('<h1> Hello, ' + username + '</h1>')

class MainPage(Handler):

    def get(self):
        blogentries= db.GqlQuery("SELECT * FROM Blogentries ORDER BY date DESC LIMIT 10")

        self.render("front-page.html", blogentries = blogentries)

class Debug(Handler):

    def get(self):
      
        name = 'Werther'

        k = UserData.all().filter('Username =', name).fetch(1)

        self.render('99_debug.html', k= k)


# Function triggering the page generation
app = webapp2.WSGIApplication([
                             ('/blog', MainPage),
                             ('/blog/newpost', NewPostHandler),
                             ('/blog/([0-9]+)', NewPostDisplay),
                             ('/blog/register', RegisterPage),
                             ('/blog/welcome', Welcome),
                             ('/debug', Debug)
                            ],
debug=True)
