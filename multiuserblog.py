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



# Main Class(es)

class MainPage(Handler):
    def render_pages(self, subject = "", text = "", error = ""):
        self.render("front.html", subject = subject, text = text, error = error)


    def get(self):
        self.write("Hello Guillaume !!!")


    def post(self):
        title = self.request.get("title")
        art = self.request.get("art")



# Function triggering the 
app = webapp2.WSGIApplication([
                             ('/', MainPage)
                            ], 
debug=True)
