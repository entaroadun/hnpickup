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
import urllib
import re
import time 
import math
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import urlfetch
from google.appengine.api.urlfetch import DownloadError 
from google.appengine.ext.webapp import template

## =================================
## === ETL data table, very simple
## === it holds just three values
## === that are collected from
## === two web pages every ~ 15 min
## =================================

class hntiming(db.Model):
  etime = db.IntegerProperty()
  timing_new = db.FloatProperty()
  timing_best = db.FloatProperty()

## =================================
## === DM data table, very simple
## === we use ETL table to compute
## === quantiles that will drive 
## === decision whether to submit
## =================================

class hnquantiles(db.Model):
  etime = db.IntegerProperty()
  quant1 = db.FloatProperty()
  quant2 = db.FloatProperty()
  quant3 = db.FloatProperty()
  quant4 = db.FloatProperty()

## =================================
## == I took it from the web
## == http://code.activestate.com/recipes/511478-finding-the-percentile-of-the-values/
## == usually more complicated statistical
## == methods are needed (e.g. numpy)
## =================================

def percentile(N, percent, key=lambda x:x):
  """
  Find the percentile of a list of values.
  @parameter N - is a list of values. Note N MUST BE already sorted.
  @parameter percent - a float value from 0.0 to 1.0.
  @parameter key - optional key function to compute value from each element of N.
  @return - the percentile of the values
  """
  if not N:
    return None
  k = (len(N)-1) * percent
  f = math.floor(k)
  c = math.ceil(k)
  if f == c:
    return key(N[int(k)])
  d0 = key(N[int(f)]) * (c-k)
  d1 = key(N[int(c)]) * (k-f)
  return d0+d1

## =================================
## == Here we calculate the percentiles
## == and store them in a DB -
## == a large chunk of data is 
## == summarized by quantiles
## == (data mining task is good for
## == backend cron jobs - you can look
## == in backends.yaml and cron.yaml)
## =================================

class MainHandler(webapp.RequestHandler):
  def get(self):
    raw_data = [];
    pickup_ratio = [];
    qry = db.GqlQuery('SELECT * FROM hntiming')
    results = qry.fetch(999)
    for result in results:
      pickup_ratio.append(result.timing_best-result.timing_new)
      raw_data.append({'col1':result.etime,'col2':result.timing_best-result.timing_new})
    pickup_ratio.sort()
## -------------------------------
## -- four intervals: 0.125 0.250 0.500 1.000
## -- normally we would have something more complicated
## -- for extracting important information
    quant1 = percentile(pickup_ratio,0.125)
    quant2 = percentile(pickup_ratio,0.250)
    quant3 = percentile(pickup_ratio,0.500)
    quant4 = percentile(pickup_ratio,1.000)
    raw_data.append({'col1':'pr1','col2':quant1})
    raw_data.append({'col1':'pr2','col2':quant2})
    raw_data.append({'col1':'pr3','col2':quant3})
    raw_data.append({'col1':'pr4','col2':quant4})
## -------------------------------
## -- store quantiles in db with a 
## -- time stamp
    etime_now = int(time.time()*1000)
    hnquant = hnquantiles(etime=etime_now,quant1=quant1,quant2=quant2,quant3=quant3,quant4=quant4)
    hnquant.put()
## -------------------------------
## -- check if we can retrieve 
## -- previous answer
    qry = db.GqlQuery('SELECT * FROM hnquantiles ORDER BY etime DESC limit 2');
    results = qry.fetch(2)
    if len(results) > 1:
      raw_data.append({'col1':'pr1','col2':results[1].quant1})
      raw_data.append({'col1':'pr2','col2':results[1].quant2})
      raw_data.append({'col1':'pr3','col2':results[1].quant3})
      raw_data.append({'col1':'pr4','col2':results[1].quant4})
## -------------------------------
## -- all we did is printed in a table
## -- not neccessary but good for debugging
    path = os.path.join(os.path.dirname(__file__), '2-dm_do.tmpl')
    self.response.out.write(template.render(path,{'results':raw_data}))

def main():
    application = webapp.WSGIApplication([('/dm_process', MainHandler)], debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()

