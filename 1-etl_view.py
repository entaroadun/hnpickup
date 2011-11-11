#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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

class hntiming(db.Model):
  etime = db.IntegerProperty()
  timing_new = db.FloatProperty()
  timing_best = db.FloatProperty()

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
    data_new = [];
    data_best = [];
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
    qry = db.GqlQuery('SELECT * FROM hntiming ORDER BY etime DESC limit '+str(ndata_elements));
    results = qry.fetch(ndata_elements)
    for i in range(ndata_elements-1,-1,-1): ## reverse the data, i think "reverse" function takes a lot of cpu
      if i < len(results):
        data_new.append([int(results[i].etime),float(results[i].timing_new)])
        data_best.append([int(results[i].etime),float(results[i].timing_best)])
## --  plugin the data into a tamplate variable
    template_values = {
      'data_new': data_new,
      'data_best': data_best
    }
    path = os.path.join(os.path.dirname(__file__), '1-etl_view.tmpl')
    self.response.out.write(template.render(path, template_values))


def main():
    application = webapp.WSGIApplication([('/etl.json', MainHandler)], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

