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
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import urlfetch
from google.appengine.api.urlfetch import DownloadError 
from google.appengine.ext.webapp import template

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
## == Web page that does all the ETL
## == "heavy lifting", i.e.,
## == combines and transforms data
## == from two different web pages
## == (this is will be run by frontend
## == cron job defined in cron.yaml)
## =================================

class MainHandler(webapp.RequestHandler):
  def get(self):
    raw_data = [];
## ---------------------------
## -- ETL Source 1: 
## -- 15-point average of oldest pages
## -- simple regular expression extraction
    data_new = [];
    data_new_timing = float(0);
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
        raw_data.append({'col1':'newest','col2':m.group(1),'col3':m.group(2)})
      data_new.sort()
      half_of_data = int(len(data_new)/2)
      data_new_num = 0
      data_new_den = 0
      for i in range(half_of_data+1,len(data_new)+1):
        data_new_num += data_new[i-1]
        data_new_den += 1
      if data_new_den: 
        data_new_timing = float(data_new_num)/float(data_new_den)  
## ---------------------------
## -- ETL Source 2: 
## -- 15-point avarege of newst pages
## -- simple regular expression extraction
    data_best = [];
    data_best_timing = float(0);
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
        raw_data.append({'col1':'news','col2':m.group(1),'col3':m.group(2)});
      data_best.sort()  
      half_of_data = int(len(data_best)/2)
      data_best_num = 0
      data_best_den = 0
      for i in range(1,half_of_data+1):
        data_best_den += 1
        data_best_num += data_best[i-1]
      if data_best_den: 
        data_best_timing = float(data_best_num)/float(data_best_den)  
## ---------------------------
## -- if we have results from
## -- both sources then lets 
## -- put it in a database
    if data_new_timing and data_best_timing:
      etime_now = int(time.time()*1000)
      hntime = hntiming(etime=etime_now,timing_new=data_new_timing,timing_best=data_best_timing)
      hntime.put()
      raw_data.append({'col1':'timestamp','col2':'newest','col3':'news'})
      raw_data.append({'col1':etime_now,'col2':data_new_timing,'col3':data_best_timing})
      raw_data.append({'col1':'lenghts','col2':len(data_new),'col3':len(data_best)})
      raw_data.append({'col1':'denominators','col2':data_new_den,'col3':data_best_den})
      raw_data.append({'col1':'numerators','col2':data_new_num,'col3':data_best_num})
## ---------------------------
## -- we can double check if the
## -- results went to the DB
## -- but we will do it by looking
## -- at second last (previous) entry
    qry = db.GqlQuery('SELECT * FROM hntiming ORDER BY etime DESC limit 2');
    results = qry.fetch(2)
    if len(results) > 1:
      raw_data.append({'col1':results[1].etime,'col2':results[1].timing_new,'col3':results[1].timing_best})
## ---------------------------
## -- finally print the report
## -- not really needed 
## -- mostly for debugging 
    path = os.path.join(os.path.dirname(__file__), '1-etl_do.tmpl')
    self.response.out.write(template.render(path,{'results':raw_data}))

def main():
    application = webapp.WSGIApplication([('/etl_process', MainHandler)], debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()

