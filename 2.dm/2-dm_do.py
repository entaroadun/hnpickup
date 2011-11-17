#!/usr/bin/env python
#
# This is very simple data mining case.
# If the "worst best articles" are very new compared
# "best new articles" then we suspect it's
# good time to publish your link: 
#
# pickup_ratio = score_new/score_best
#
# good_time = newsest_are_scored_high/news_are_scored_low
#
# Quantiles are perfect for quantifying random variables.
# We want to create four intervals when it is good to
# submit: very good, good, so-so, and bad.
#
# Normally data mining will be more CPU and memory intensive.
# Google App Engine has backends for that kind of work.
# In order to have a script running in backend persistant
# machine we need to define entries in:
# backends.yamp, app.yaml, and cron.yaml
# 
# Remember to deploy backend manually:
# appcfg.py backends <dir> update
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
## == We arbitrary set the quantile
## == intervals
## ================================

QUANTILE_VERY_GOOD = 0.9
QUANTILE_GOOD = 0.8
QUANTILE_SO_SO = 0.7

## =================================
## === ETL data table, very simple
## === it holds just three values
## === that are collected from
## === two web pages every ~ 15 min
## =================================

class HNscore(db.Model):
  etime = db.IntegerProperty()
  score_best = db.FloatProperty()
  score_new = db.FloatProperty()
  pickup_ratio = db.FloatProperty()

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
  max_best = db.FloatProperty()
  max_new = db.FloatProperty()
  max_pickup = db.FloatProperty()

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
    html_data = [];
    score_best = [];
    score_new = [];
    pickup_ratio = [];
    qry = db.GqlQuery('SELECT * FROM HNscore ORDER BY etime DESC')
    results = qry.fetch(1000)
    for result in results:
      score_best.append(result.score_best)
      score_new.append(result.score_new)
      pickup_ratio.append(result.pickup_ratio)
      html_data.append({'col1':result.etime,'col2':result.pickup_ratio})
## -------------------------------
## -- three probabilities: 0.9, 0.8, 0.7
## -- normally we would have something more complicated
## -- for extracting important information but
## -- that's how we do DM here
    pickup_ratio.sort()
    quant1 = percentile(pickup_ratio,QUANTILE_VERY_GOOD)
    quant2 = percentile(pickup_ratio,QUANTILE_GOOD)
    quant3 = percentile(pickup_ratio,QUANTILE_SO_SO)
    max_best = max(score_best)
    max_new = max(score_new)
    max_pickup = max(pickup_ratio)
    html_data.append({'col1':'quant1','col2':quant1})
    html_data.append({'col1':'quant2','col2':quant2})
    html_data.append({'col1':'quant3','col2':quant3})
    html_data.append({'col1':'max','col2':max_pickup})
## -------------------------------
## -- store quantiles in db with a 
## -- time stamp
    etime_now = int(time.time()*1000)
    hnquantiles = HNquantiles(etime=etime_now,quant1=quant1,quant2=quant2,quant3=quant3,max_best=max_best,max_new=max_new,max_pickup=max_pickup)
    hnquantiles.put()
## -------------------------------
## -- check if we can retrieve 
## -- previous answer
    qry = db.GqlQuery('SELECT * FROM HNquantiles ORDER BY etime DESC limit 2');
    results = qry.fetch(2)
    if len(results) > 1:
      html_data.append({'col1':'quant1','col2':results[1].quant1})
      html_data.append({'col1':'quant2','col2':results[1].quant2})
      html_data.append({'col1':'quant3','col2':results[1].quant3})
      html_data.append({'col1':'max','col2':results[1].max_pickup})
## -------------------------------
## -- all we did is printed in a table
## -- not neccessary but good for debugging
    path = os.path.join(os.path.dirname(__file__), '2-dm_do.tmpl')
    self.response.out.write(template.render(path,{'results':html_data}))

def main():
    application = webapp.WSGIApplication([('/dm_process', MainHandler)], debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()

