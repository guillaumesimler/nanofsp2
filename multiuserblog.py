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


blogentries = [{"title": "A first Test", "bodytext": "A convincing first test", "date": "26.05.2016"}, 
               {"title": "A second Test", "bodytext": "The confirmation", "date": "29.05.2016"}]

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
            temp = {"title": title, "bodytext": bodytext, "date": "30.05.2016"}

            blogentries.append(temp)

            self.redirect('/blog')
        else:
            error = "Something went wrong. The title or the bodytext were not filled"

            self.render_newpost(title, bodytext, error)


class MainPage(Handler):
    def render_pages(self, error = ""):

        self.render("front-page.html", blogentries = blogentries)


    def get(self):
        self.render_pages()




# Function triggering the 
app = webapp2.WSGIApplication([
                             ('/blog', MainPage),
                             ('/blog/newpost', NewPostHandler)
                            ], 
debug=True)
