import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
								autoescape = True)

class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

class Post(db.Model):
	title = db.StringProperty(required = True)
	post = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)

class newpost(Handler):
	def render_front(self, title="", post="", error=""):
		self.render("new_post.html", title=title, post=post, error=error)

	def get(self):
		self.render_front()

	def post(self):
		title = self.request.get('title')
		post = self.request.get('post')

		if title and post:
			a = Post(title = title, post = post)
			a.put()
			id = a.key().id()
			self.redirect("/blog/%s" % id)
		else:
			error = 'We need both a title and body.'
			self.render_front(title, post, error)

class blog(Handler):
	def render_front(self):
		posts = db.GqlQuery('SELECT * FROM Post ORDER BY created DESC LIMIT 5')
		self.render("blog_posts.html", posts=posts)

	def get(self):
		self.render_front()

class ViewPostHandler(Handler):

	def get(self,id):
		post = Post.get_by_id( int(id) )
		self.render("permalink.html", post=post)

application = webapp2.WSGIApplication([
	('/blog', blog),
	('/newpost', newpost),
	webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
