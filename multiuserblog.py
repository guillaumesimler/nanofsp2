# ----- Multi User Block -----
#
#  A Program by Guillaume Simler



# Libraries:
# jinja2 (templating lib), webapp2 (main GAE library) &
# db (Datastore) are linked to Google App Engine (GAE)


import os
import jinja2
import webapp2

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

    title = db.StringProperty(required = True)
    bodytext = db.TextProperty(required = True)
    contributor = db.StringProperty(required = True)
    date = db.DateTimeProperty(auto_now_add = True)
    modified = db.DateTimeProperty(auto_now = True)


# Main Classes

class NewPostHandler(Handler):

class Blogentries(db.Model):
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


class MainPage(Handler):

    def get(self):
        blogentries= db.GqlQuery("SELECT * FROM Blogentries ORDER BY date DESC LIMIT 10")

        self.render("front-page.html", blogentries = blogentries)




# Function triggering the page generation
app = webapp2.WSGIApplication([
                             ('/blog', MainPage),
                             ('/blog/newpost', NewPostHandler),
                             ('/blog/([0-9]+)', NewPostDisplay)
                            ],
debug=True)
