#!/usr/bin/env python
#
# Data Mining starts with collecting
# the right data. Here we mine the average
# time of newest articles on HN "news" web page
# and oldest articles on HN "newest" web page
# if "newest" articles get to the "news" page
# then it's good time to submit. We don't knwo this
# exact time but we can just approximate
# 
# Google App Engine CRON job will run this page
# user will not have access to it.
# Google App Engine has backends for that kind of work.
# app.yaml and cron.yaml define access to this page
#
# If you have intensive ETL then is should go
# to the backend if not you can run it on the frontend.
# Look in cron.yaml file for "target: xxx" entries
# 
# Remember to deploy backend manually:
# appcfg.py backends <dir> update
#

import os
import urllib
import re
import time 
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import urlfetch
from google.appengine.api.urlfetch import DownloadError 
from google.appengine.ext.webapp import template

## =================================
## == N-point average constant
## == How many point will we use
## == to summarize dynamics of HN
## =================================

N_POINT_AVERAGE = 10

## =================================
## === ETL data table, very simple,
## === it holds just three values
## === (plus a time stamp)
## === that are collected from
## === two web pages every ~ 15 min
## =================================

class HNtime(db.Model):
  etime = db.IntegerProperty()
  time_best = db.FloatProperty()
  time_new = db.FloatProperty()
  pickup_ratio = db.FloatProperty()

## =================================
## == Web page that does all the ETL
## == "heavy lifting", i.e.,
## == combines and transforms data
## == from two different web pages
## == (this is will be run by frontend
## == cron job defined in cron.yaml)
## =================================

class MainHandler(webapp.RequestHandler):
  def get(self):
    html_data = [];
## ---------------------------
## -- ETL Source 1: 
## -- N-point average of oldest pages
## -- simple regular expression extraction
## -- (a much better way is to use web APIs)
## -- (look for web API here http://www.programmableweb.com/)
    data_new = [];
    data_new_time = float(0);
    result = urlfetch.fetch(url='https://news.ycombinator.com/newest',deadline=60)
    if result.status_code == 200:
      txt_data = result.content
      for m in re.finditer(r"(\d+) (minutes?|hours?) ago",txt_data):
        if m.group(2) == 'hour' or m.group(2) == 'hours':
          tmp_time = int(m.group(1)) * 60
        elif m.group(2) == 'day' or m.group(2) == 'days': 
          tmp_time = int(m.group(1)) * 1440
        else:
          tmp_time = int(m.group(1))
        data_new.append(tmp_time)
        html_data.append({'col1':'newest','col2':m.group(1),'col3':m.group(2)})
      data_new.sort(reverse=True)
      data_new_num = 0
      data_new_den = 0
      for i in range(0,N_POINT_AVERAGE):
        data_new_num += data_new[i]
        data_new_den += 1
      if data_new_den: 
        data_new_time = float(data_new_num)/float(data_new_den)  
## ---------------------------
## -- ETL Source 2: 
## -- 15-point avarege of newst pages
## -- simple regular expression extraction
## -- (a much better way is to use web APIs)
## -- (look for web API here http://www.programmableweb.com/)
    data_best = [];
    data_best_time = float(0);
    result = urlfetch.fetch(url='https://news.ycombinator.com/news',deadline=60)
    if result.status_code == 200:
      txt_data = result.content
      for m in re.finditer(r"(\d+) (minutes?|hours?|days?) ago",txt_data):
        if m.group(2) == 'hour' or m.group(2) == 'hours':
          tmp_time = int(m.group(1)) * 60
        elif m.group(2) == 'day' or m.group(2) == 'days': 
          tmp_time = int(m.group(1)) * 1440
        else:
          tmp_time = int(m.group(1))
        data_best.append(tmp_time)
        html_data.append({'col1':'news','col2':m.group(1),'col3':m.group(2)});
      data_best.sort()  
      data_best_num = 0
      data_best_den = 0
      for i in range(0,N_POINT_AVERAGE):
        data_best_num += data_best[i]
        data_best_den += 1
      if data_best_den: 
        data_best_time = float(data_best_num)/float(data_best_den)  
## ---------------------------
## -- if we have results from
## -- both sources then lets 
## -- put it in a database
    if data_new_time and data_best_time:
      etime_now = int(time.time()*1000)
      hntime = HNtime(etime=etime_now,time_best=data_best_time,time_new=data_new_time,pickup_ratio=data_new_time/data_best_time)
      hntime.put()
      html_data.append({'col1':'timestamp','col2':'newest','col3':'news'})
      html_data.append({'col1':etime_now,'col2':data_new_time,'col3':data_best_time})
      html_data.append({'col1':'lenghts','col2':len(data_new),'col3':len(data_best)})
      html_data.append({'col1':'denominators','col2':data_new_den,'col3':data_best_den})
      html_data.append({'col1':'numerators','col2':data_new_num,'col3':data_best_num})
## ---------------------------
## -- we can double check if the
## -- results went to the DB
## -- but we will do it by looking
## -- at second last (previous) entry
    qry = db.GqlQuery('SELECT * FROM HNtime ORDER BY etime DESC limit 2');
    results = qry.fetch(2)
    if len(results) > 1:
      html_data.append({'col1':results[1].etime,'col2':results[1].time_new,'col3':results[1].time_best})
## ---------------------------
## -- finally print the report
## -- not really needed 
## -- mostly for debugging 
    path = os.path.join(os.path.dirname(__file__), '1-etl_do.tmpl')
    self.response.out.write(template.render(path,{'results':html_data}))

def main():
    application = webapp.WSGIApplication([('/etl_process', MainHandler)], debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()

