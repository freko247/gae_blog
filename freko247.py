# -*- coding: utf-8 -*-
import jinja2
import os
import urllib
import webapp2

from google.appengine.ext import db
from google.appengine.api import users


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
DEFAULT_BLOG = 'freko247'


class Post(db.Model):
    '''Models an individual Blog entry wtih author, content and date'''
    author = db.StringProperty()
    content = db.StringProperty(multiline=True)
    date = db.DateTimeProperty(auto_now_add=True)


class Co_Writer(db.Model):
    '''Blog co-writers'''
    grantee = db.StringProperty()
    writer = db.StringProperty()


def blog_key(blog_name=None):
    '''Constructs a Datastore key for a Blog entity
        with blog_name.
    '''
    return db.Key.from_path('Blog', blog_name or DEFAULT_BLOG)


def can_post(user, blog_name):
    if user:
        q = Co_Writer.all().ancestor(
            blog_key(blog_name)).filter('writer =', user.nickname())
        co_writer = q.get()
        if co_writer or is_owner(user, blog_name):
            return True
    return False


def is_owner(user, blog_name):
    if user:
        if user.nickname() == blog_name:
            return True
    return False


class MainPage(webapp2.RedirectHandler):
    def get(self):
        user = users.get_current_user()
        blog_name = self.request.get('blog_name') or \
            self.request.cookies.get(u'blog_name')
        if user:
            if not blog_name:
                blog_name = user.nickname()
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            if not blog_name:
                blog_name = DEFAULT_BLOG
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        posts = Post.all().ancestor(
            blog_key(blog_name)).order('-date')
        co_writers = Co_Writer.all().ancestor(
            blog_key(blog_name)).order('writer')
        template_values = {
            'posts': posts or None,
            'url': url,
            'url_linktext': url_linktext,
            'can_post': can_post(user, blog_name),
            'blog_name': blog_name,
            'is_owner': is_owner(user, blog_name),
            'co_writers': co_writers,
        }
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.set_cookie('blog_name', blog_name)
        self.response.write(template.render(template_values))


class Blog(webapp2.RedirectHandler):
    def post(self):
        user = users.get_current_user()
        if user:
            blog_name = self.request.cookies.get('blog_name')
            post = Post(parent=blog_key(blog_name))
            post.author = users.get_current_user().nickname()
            post.content = self.request.get('content')
            post.put()
            # TODO: Don't reload entire page when submitting new post...
            query_params = {'blog_name': blog_name}
            self.redirect('/?' + urllib.urlencode(query_params))
        self.redirect('/')


class Co_writerManager(webapp2.RedirectHandler):
    def post(self):
        user = users.get_current_user()
        if user:
            add = self.request.get('add')
            remove = self.request.get('remove')
            writers = self.request.get('co_writers', allow_multiple=True)
            if add:
                blog = user.nickname()
                co_writer = Co_Writer(parent=blog_key(blog))
                co_writer.writer = self.request.get('co_writer')
                co_writer.grantee = blog
                co_writer.put()
                query_params = {'blog_name': blog}
                self.redirect('/?' + urllib.urlencode(query_params))
            elif remove and writers:
                blog_name = self.request.cookies.get('blog_name')
                q = Co_Writer.all().ancestor(
                    blog_key(blog_name)).filter('writer IN', writers)
                co_writers = q.get()
                db.delete(co_writers)
        self.redirect('/')


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/new_post', Blog),
                               ('/update_co_writers', Co_writerManager)],
                              debug=True
                              )
