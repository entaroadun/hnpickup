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
from google.appengine.ext.webapp import template
from google.appengine.ext import db

## =================================
## === ETL data table, very simple,
## === it holds just three values
## === that are collected from
## === two web pages every ~ 15 min
## =================================

class HNtime(db.Model):
  etime = db.IntegerProperty()
  time_new = db.FloatProperty()
  time_best = db.FloatProperty()
  time_diff = db.FloatProperty()

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
    data_best = [];
    data_new = [];
    pickup_ratio = [];
    str_ndata_elements = self.request.get('ndata_elements')
    ndata_elements = 96 ## this is equal to full 24h = 96 * 15 min
## ------------------------
## -- remeber to cleanup user
## -- input, some one might
## -- hack your app
    str_ndata_elements = re.sub('\D+','',str_ndata_elements);
    if len(str_ndata_elements) > 0 and int(str_ndata_elements) > 2 and int(str_ndata_elements) <= 1000:
      ndata_elements = int(str_ndata_elements);
## ---------------------------
## -- now we are ready to get 
## -- the data and feed it into
## -- a json template
    qry = db.GqlQuery('SELECT * FROM HNtime ORDER BY etime DESC limit '+str(ndata_elements));
    results = qry.fetch(ndata_elements)
    for i in range(ndata_elements-1,-1,-1): ## reverse the data, i think "reverse" function takes a lot of cpu
      if i < len(results):
        data_best.append([int(results[i].etime),float(results[i].time_best)])
        data_new.append([int(results[i].etime),float(results[i].time_new)])
        pickup_ratio.append([int(results[i].etime),float(results[i].time_diff)]) ## the difference tells us if it's good time or not 
## --  plugin the data into a tamplate variable
    template_values = {
      'data_best': data_best,
      'data_new': data_new,
      'pickup_ratio': pickup_ratio
    }
    path = os.path.join(os.path.dirname(__file__), '1-etl_view.tmpl')
    self.response.out.write(template.render(path, template_values))


def main():
    application = webapp.WSGIApplication([('/etl.json', MainHandler)], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

