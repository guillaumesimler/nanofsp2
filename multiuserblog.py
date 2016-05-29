import os
import jinja2
import webapp2

from google.appengine.ext import db

# initialize Jinja

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), 
                            autoescape= True)


#Helper Class (reduce work in handler)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

# Create the entity (Google Datastore's table)


class Blogentries(db.Model):
    title = db.StringProperty(required = True)
    bodytext = db.TextProperty(required = True)
    contributor = db.StringProperty(required = True)
    date = db.DateTimeProperty(auto_now_add = True)
    modified = db.DateTimeProperty(auto_now = True)


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



            self.redirect('/blog/%s' %str(key))
        else:
            error = "Something went wrong. The title or the bodytext were not filled"

            self.render_newpost(title, bodytext, error)


class NewPostDisplay(Handler):
    def get(self, keyid):
        
        # to be replaced
        key = db.Key.from_path('Blogentries', int(keyid))
        display = db.get(key)

        if not display:
            self.error(404)

        # end of the replacement 

        self.render("single_entry.html", display = display)


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
