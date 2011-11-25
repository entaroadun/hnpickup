#!/usr/bin/env python
#
# Obviously, we want some way to get the 
# data mining results out of the server.
# This can be done similarly to ETL, that is,
# through JSON structure. This is very flexible way
# since we can also use JSON in other external 
# software.
#
# Here we want the end user to be able to get to
# the data through URL. This is defined in
# app.yaml
#

import os
import random
import re
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

# Read more at
# http://code.google.com/appengine/docs/python/tools/libraries.html#Django

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from google.appengine.dist import use_library
use_library('django', '1.2')
from google.appengine.ext.webapp import template



## =================================
## === DM data table, very simple
## === we use ETL table to compute
## === quantiles that will drive 
## === decision whether to submit
## =================================

class HNQUANTILES(db.Model):
  etime = db.IntegerProperty()
  quant1 = db.FloatProperty()
  quant2 = db.FloatProperty()
  quant3 = db.FloatProperty()
  max_news = db.FloatProperty()
  max_newest = db.FloatProperty()
  max_pickup = db.FloatProperty()

## =================================
## == sometimes we want to get the
## == ETL data to display it by some
## == drag'n'drop query system
## == or some visualization tool
## == here the data is fed to 
## == javascript tool trough json
## =================================

class MainHandler(webapp.RequestHandler):
  def get(self):
    str_ndata_elements = self.request.get('ndata_elements')
    ndata_elements = 1 ## most current percentiles
## ------------------------
## -- remeber to cleanup user
## -- input, some one might
## -- hack your app
    str_ndata_elements = re.sub('\D+','',str_ndata_elements);
    if len(str_ndata_elements) > 0 and int(str_ndata_elements) > 0 and int(str_ndata_elements) <= 1000:
      ndata_elements = int(str_ndata_elements);
## ---------------------------
## -- now we are ready to get 
## -- the data and feed it into
## -- json template
    qry = db.GqlQuery('SELECT * FROM HNQUANTILES ORDER BY etime DESC limit '+str(ndata_elements));
    data_quantiles = qry.fetch(ndata_elements)
## --  plugin the data into a tamplate variable
    template_values = {
      'data_quantiles': data_quantiles,
    }
    path = os.path.join(os.path.dirname(__file__), '2-dm_view.tmpl')
    self.response.out.write(template.render(path, template_values))

def main():
    application = webapp.WSGIApplication([('/dm.json', MainHandler)], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

