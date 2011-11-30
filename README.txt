## =============================
## == "I took CS, DM, ML, NLP, and 
## == AI classes, what's next?"
## =============================

Apply your new strengths to the real world data. 
There are a lot of challenging data mining problems 
waiting to be solved. Let's start small. 

The first step is to get your own data. Is there 
any websites that you visit every day? I'm sure 
they produce fresh content every day: new articles,
new stats, new numbers. How about you start 
collecting them? If you have your own data 
you decide what interesting question it may answer.

Next step. Does your favorite website have any 
trends? More articles are published in summer 
than in winter? More people are willing to "like" 
articles in spring than in autumn. Is it possible 
to predict which article will create more web traffic,
thus, more revenue from advertisements?

Finally, once you mine the answer you should 
display it. Do it so that it's pleasurable 
for the eye. Colorful time series or multidimensional 
scaling should do the trick. Describe your graph 
so the people not familiar with your project 
can understand it and enjoy it.

Does it seem like a lot of work? Well, here is a source
code that deploys your app with one command on Google App 
Engine. You just need to focus on where to get 
the data (ETL), what to do with it (DM), and how
to display it (VISUALIZATION). The source code has example
that you can swap with an idea of your own.

Little by little you will master how to add monetary
value to your data, sell it, or build a business
model.

## =============================
## == START
## =============================

Create an account and new app placeholder at:

http://appengine.google.com/

Please install Google App Engine SDK from:

http://code.google.com/appengine/downloads.html

Getting started with Python web app development is here:

http://code.google.com/appengine/docs/python/gettingstarted/

For lunching the app you can use this nice GUI:

http://code.google.com/p/google-appengine-mac-launcher/
http://code.google.com/p/google-appengine-wx-launcher/

It's also good to have Google Analytics account:

http://www.google.com/analytics/

You can also check webmaster tools to make sure your
website is properly indexed by Google:

https://www.google.com/webmasters/tools

Don't forget to rename your app in the app.yaml file:

application: hnpickupdev -> application: yourapp

Current source code requires at least six data points.
That means you have to run "/etl_process" webpage at
least six times and "/dm_process" at least once
before you see a graph.

## =============================
## == INTRO
## =============================

This is example of a simple data mining application.
Here Hacker News aggregator is our source of data. 
The data mining objective is to figure out when is good time
to post an article or a story on Hacker News website so
other people will up-vote it and it will get to from 
the "newest" page to "news" page.

## =============================
## == MODEL
## =============================

This app can serve as a simple business model where 
you claim is that your DATA MINING application 
bring better EXPERIENCE, OUTCOME, and VALUE to 
existing products. How come? If you start adding new
knowledge to existing data you will see the
pattern: large data can be abstracted to a small 
chunk of information that is more valuable
than the large dataset. That's how you sell your 
service. Example? Every day you observe cars;
that's a lot of data, however, you notice that
around 8 am there are many more cars than at other
hours; this is your small chunk of information.
This small chunk will save you 30 min of stuck
in traffic: better experience, outcome and value.

## =============================
## == CODE
## =============================

Most data mining application will have very similar 
information flow:

1.ETL -> 2.DM -> 3.VISUALIZATION

Which means:

1.GET THE DATA -> 2.ADD VALUE -> 3.USE IT

That's why the code is organized into three sections:

1. ETL = Extract, Transform, Load (GET THE DATA)
2. DM = Data Mining (ENRICH THE DATA, ADD VALUE)
3. VISUALISATION = Data presentation in a format 
   that can support decision making process (USE IT, SHOW IT)

You can think of the code as a "Hello, World!" web data mining 
example. You shouldn't be surprised that most of the code went
into visualization. That's how you get your customers to buy-in. 
Data for visualization is obtained using JSON serialization.

## =============================
## == WARNING
## =============================

This app shows some raw data. For more complicated projects
it might not be good idea to show the raw data. Too much
data on the user interface will clog the decision making
process.

## =============================
## == FUTURE
## =============================

The hope is that early stage start-ups can use this 
code to quickly organize their thoughts and prototype 
their idea. Google App Engine can run this app for free, 
giving opportunity to demonstrate a working version of 
their idea.
