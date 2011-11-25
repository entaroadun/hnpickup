#!/usr/bin/env python
#
# The icing on the cake is to present the data
# to a user. Probably presenting the raw ETL data
# is not a good idea. This may produce a lot of clutter.
# But for debugging purposes we want to have all data 
# in one place to make sure that the app is working 
# according to the specification. I also thought that
# for bigger application you want to disconnect
# main page generation from data loading. This seems 
# to me more scalable than generating data and HTML at the 
# same time
#
# The URL to this page (.*) is defined in app.yaml
# (all unmatched URLs end up here - ideally we
# would have some unmatched URLs error handling)
#

import os
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp.util import run_wsgi_app

# Read more at
# http://code.google.com/appengine/docs/python/tools/libraries.html#Django

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from google.appengine.dist import use_library
use_library('django', '1.2')
from google.appengine.ext.webapp import template

## =================================
## == We let jQuery do the most work;
## == use client CPU instead of app
## == engine CPU
## =================================

class MainHandler(webapp.RequestHandler):
  def get(self):
    path = os.path.join(os.path.dirname(__file__), '3-view_do.tmpl')
    self.response.out.write(template.render(path,{}))

class ErrorHandler(webapp.RequestHandler):
  def get(self):
    path = os.path.join(os.path.dirname(__file__), '3-view_err.tmpl')
    self.response.set_status(404)
    self.response.out.write(template.render(path,{'path':self.request.path}))

def main():
    application = webapp.WSGIApplication([('/', MainHandler),('/.*',ErrorHandler)], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

