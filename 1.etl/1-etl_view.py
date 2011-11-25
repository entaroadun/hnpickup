#!/usr/bin/env python
#
# Here we want to get the ETL data
# into a JSON structure for viewing in JS
# or in some other external software
#
# Any user can access this data 
# through a URL defined in app.yaml
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

## ##################################
## In order to get the data into R,
## you need to write following:
##
## library(rjson);
## dat <- fromJSON(file='http://hnpickup.appspot.com/etl.json?ndata_elements=999');
## score_newest <- sapply(dat[[1]][['data']],function(x){x[2]})
## score_news <- sapply(dat[[2]][['data']],function(x){x[2]})
## pickup_ratio <- sapply(dat[[3]][['data']],function(x){x[2]})
## 
## plot(score_newest,score_news,lwd=2);
##
## ##################################

## =================================
## == Maximum number of data points 
## == that is allowed to download
## == (3000 ~ is roughly a month)
## =================================

MAX_NDATA_ELEMENTS = 3000

## =================================
## === ETL data table, very simple,
## === it holds just three values
## === that are collected from
## === two web pages every ~ 15 min
## =================================

class HNSCORE(db.Model):
  etime = db.IntegerProperty()
  score_news = db.FloatProperty()
  score_newest = db.FloatProperty()
  pickup_ratio = db.FloatProperty()

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
    data_news = []
    data_newest = []
    pickup_ratio = []
    str_ndata_elements = self.request.get('ndata_elements')
    ndata_elements = 48 ## this is equal to 12h = 12 * 4 * 15min
## ------------------------
## -- remeber to cleanup user
## -- input, some one might
## -- hack your app
    str_ndata_elements = re.sub('\D+','',str_ndata_elements)
    if len(str_ndata_elements) > 0 and int(str_ndata_elements) <= MAX_NDATA_ELEMENTS:
## -- if MAX_SMOOTH = 5 then minimum number of data points is 7
      if int(str_ndata_elements) < 7:
	ndata_elements = 7
      else:
        ndata_elements = int(str_ndata_elements)
## ---------------------------
## -- now we are ready to get 
## -- the data and feed it into
## -- a json template
    qry = db.GqlQuery('SELECT * FROM HNSCORE ORDER BY etime DESC limit '+str(ndata_elements))
    results = qry.fetch(ndata_elements)
    for i in range(ndata_elements-1,-1,-1): ## reverse the data, i think "reverse" function takes a lot of cpu
      if i < len(results):
        data_news.append([int(results[i].etime),float(results[i].score_news)])
        data_newest.append([int(results[i].etime),float(results[i].score_newest)])
        pickup_ratio.append([int(results[i].etime),float(results[i].pickup_ratio)]) ## the difference tells us if it's good time or not 
## --  plugin the data into a tamplate variable
    template_values = {
      'data_news': data_news,
      'data_newest': data_newest,
      'pickup_ratio': pickup_ratio
    }
    path = os.path.join(os.path.dirname(__file__), '1-etl_view.tmpl')
    self.response.out.write(template.render(path, template_values))

def main():
    application = webapp.WSGIApplication([('/etl.json', MainHandler)], debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()

