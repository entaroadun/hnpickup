#!/usr/bin/env python
#
# Data Mining starts with collecting
# the right data. Here we mine the average
# score of the lowest scored articles on HN "news" web page
# and the highest scored articles on HN "newest" web page
# if we would know that "newest" articles can get to the 
# "news" page then it's good time to submit. We can 
# approximate this by waiting until lowest articles on the
# first page have similar scoring pattern then articles on
# the "newest" page.
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

# Read more at
# http://code.google.com/appengine/docs/python/tools/libraries.html#Django

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from google.appengine.dist import use_library
use_library('django', '1.2')
from google.appengine.ext.webapp import template

## #################################
## Here you can put what you have learned
## at the Computer Science, Computer 
## Engineering, Databases, Data Warehousing,
## Business Intelligence, Database Management,
## or Data Modelling classes
## #################################

## =================================
## == N-point average constant
## == How many point will we use
## == to summarize dynamics of HN
## =================================

N_POINT_AVERAGE = 6

## =================================
## === ETL data table, very simple,
## === it holds just three values
## === (plus a time stamp)
## === that are collected from
## === two web pages every ~ 15 min
## =================================

class HNSCORE(db.Model):
  etime = db.IntegerProperty()
  score_news = db.FloatProperty()
  score_newest = db.FloatProperty()
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
    html_data = []
## ---------------------------
## -- ETL Source 1: 
## -- N-point average of highest score submissions
## -- simple regular expression extraction
## -- (a much better way is to use web APIs)
## -- (look for web API here http://www.programmableweb.com/)
    data_newest = []
    data_newest_score = float(0)
    result = urlfetch.fetch(url='https://news.ycombinator.com/newest',deadline=60)
    if result.status_code == 200:
      txt_data = result.content
      for m in re.finditer(r"(\d+) points?</span> by (.+?) (\d+) (minutes?|hours?|days?) ago",txt_data):
        data_newest.append(int(m.group(1)))
        html_data.append({'col1':'newest','col2':m.group(1),'col3':m.group(2)})
      data_newest.sort(reverse=True)
      data_newest_num = 0
      data_newest_den = 0
      if len(data_newest) >= N_POINT_AVERAGE:
        for i in range(0,N_POINT_AVERAGE):
          data_newest_num += data_newest[i]
          data_newest_den += 1
      if data_newest_den: 
        data_newest_score = float(data_newest_num)/float(data_newest_den)  
## ---------------------------
## -- ETL Source 2: 
## -- N-point avarege of lowest score submissions
## -- simple regular expression extraction
## -- (a much better way is to use web APIs)
## -- (look for web API here http://www.programmableweb.com/)
    data_news = []
    data_news_score = float(0)
    result = urlfetch.fetch(url='https://news.ycombinator.com/news',deadline=60)
    if result.status_code == 200:
      txt_data = result.content
      for m in re.finditer(r"(\d+) points?</span> by (.+?) (\d+) (minutes?|hours?|days?) ago",txt_data):
        data_news.append(int(m.group(1)))
        html_data.append({'col1':'news','col2':m.group(1),'col3':m.group(2)})
      data_news.sort()  
      data_news_num = 0
      data_news_den = 0
      if len(data_news) >= N_POINT_AVERAGE:
        for i in range(0,N_POINT_AVERAGE):
          data_news_num += data_news[i]
          data_news_den += 1
      if data_news_den: 
        data_news_score = float(data_news_num)/float(data_news_den)  
## ---------------------------
## -- if we have results from
## -- both sources then lets 
## -- put it in a database
    if data_newest_score and data_news_score:
      etime_now = int(time.time()*1000)
      hntime = HNSCORE(etime=etime_now,score_news=data_news_score,score_newest=data_newest_score,pickup_ratio=data_newest_score/data_news_score)
      hntime.put()
      html_data.append({'col1':'timestamp','col2':'newest','col3':'news'})
      html_data.append({'col1':etime_now,'col2':data_newest_score,'col3':data_news_score})
      html_data.append({'col1':'lenghts','col2':len(data_newest),'col3':len(data_news)})
      html_data.append({'col1':'denominators','col2':data_newest_den,'col3':data_news_den})
      html_data.append({'col1':'numerators','col2':data_newest_num,'col3':data_news_num})
## ---------------------------
## -- we can double check if the
## -- results went to the DB
## -- but we will do it by looking
## -- at second last (previous) entry
    qry = db.GqlQuery('SELECT * FROM HNSCORE ORDER BY etime DESC limit 2')
    results = qry.fetch(2)
    if len(results) > 1:
      html_data.append({'col1':results[1].etime,'col2':results[1].score_newest,'col3':results[1].score_news})
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

