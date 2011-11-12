#!/usr/bin/env python
#
# This is very simple data mining case.
# If the "oldest new articles" are close to
# "newest best articles" then we suspect it's
# good time to publish your link. But how often
# this happens. Ideally we would wait when this 
# difference is minimal. Instead, we can use quantiles
# that will stratify the rarety of this situation.
# We arbitrarly decide that less than 0.125 are rare
# cases and this is very good time to submit. 0.25 is not
# so bad either. 
#
# Normally data mining will be more CPU and memory intensive.
# Google App Engine has backends for that kind of work.
# In order to have a script running in backend persistant
# machine we need to define entries in:
# backends.yamp, app.yaml, and cron.yaml
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

class HNtime(db.Model):
  etime = db.IntegerProperty()
  time_best = db.FloatProperty()
  time_new = db.FloatProperty()
  time_diff = db.FloatProperty()

## =================================
## === DM data table, very simple
## === we use ETL table to compute
## === quantiles that will drive 
## === decision whether to submit
## =================================

class HNquantiles(db.Model):
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
    qry = db.GqlQuery('SELECT * FROM HNtime')
    results = qry.fetch(999)
    for result in results:
      pickup_ratio.append(result.time_diff)
      raw_data.append({'col1':result.etime,'col2':result.time_diff})
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
    hnquantiles = HNquantiles(etime=etime_now,quant1=quant1,quant2=quant2,quant3=quant3,quant4=quant4)
    hnquantiles.put()
## -------------------------------
## -- check if we can retrieve 
## -- previous answer
    qry = db.GqlQuery('SELECT * FROM HNquantiles ORDER BY etime DESC limit 2');
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

