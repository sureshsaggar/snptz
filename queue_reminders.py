#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 coding=utf-8

import logging
import time
import datetime
from google.appengine.api import mail
from google.appengine.api import taskqueue
from google.appengine.api import users
from google.appengine.ext import db
import models

logging.info('Scheduled task starting...')

plaintext_template = '''

Hi %(username)s,

HIT REPLY to this email and describe
(inline, below) what you worked on last
week and what you're going to work on
this week (one task per line, please).  
Or visit http://www.snptz.com

--~--~--~--~--~--~--~--~--~--~--~--~--~--~
HOW DID LAST WEEK GO?
Edit your goals from last week:
--~--~--~--~--~--~--~--~--~--~--~--~--~--~

%(tasks)s

--~--~--~--~--~--~--~--~--~--~--~--~--~--~
WHAT'RE YOU GOING TO DO THIS WEEK?
--~--~--~--~--~--~--~--~--~--~--~--~--~--~

REPLACE ME!
REPLACE ME!
REPLACE ME!
REPLACE ME!

--~--~--~--~--~--~--~--~--~--~--~--~--~--~
(list any number of tasks above these two hyphens)
'''

html_template = '''

<a href="http://www.snptz.com"><img src="http://www.snptz.com/static/logoMed.png" width="174" height="50" alt="SNPTZ"></a>
<p>Good morning %(username)s!</p>

<p>
HIT REPLY to this email and describe
(inline, below) what you worked on last
week and what you're going to work on
this week (one task per line).  
Or visit <a href="http://www.snptz.com">snptz.com</a>.  
</p>

--~--~--~--~--~--~--~--~--~--~--~--~--~--~<br/>
<span style="font-weight:bold;">How'd it go?</b><br/>
Update this list with what you actually completed<br/>
--~--~--~--~--~--~--~--~--~--~--~--~--~--~<br/>
<pre style="font-family: arial,sans-serif;">
%(tasks)s
</pre>
--~--~--~--~--~--~--~--~--~--~--~--~--~--~<br/>
<span style="font-weight:bold;">WHAT'RE YOU GOING TO DO THIS WEEK?</span><br/>
--~--~--~--~--~--~--~--~--~--~--~--~--~--~<br/>
<br/>
<br/>
REPLACE ME!<br/>
<br/>
<br/>
--~--~--~--~--~--~--~--~--~--~--~--~--~--~<br/>
(list any number of tasks above this line)<br/>
'''

first_time_plaintext = '''

Hi %(username)s,

Welcome to SNPTZ!

Please HIT REPLY and tell us a few things you're going to do this week, BETWEEN THE LINES below.
Or visit www.snptz.com 

--~--~--~--~--~--~--~--~--~--~--~--~--~--~
WHAT'RE YOU GOING TO DO THIS WEEK?
--~--~--~--~--~--~--~--~--~--~--~--~--~--~

REPLACE ME!
REPLACE ME!
REPLACE ME!
REPLACE ME!

--~--~--~--~--~--~--~--~--~--~--~--~--~--~
(list any number of tasks above these two hyphens)
'''

first_time_html = '''
<a href="http://www.snptz.com"><img src="http://www.snptz.com/static/logoMed.png" width="174" height="50" alt="SNPTZ"></a>
<p>Hi %(username)s!</p>
<p>Welcome to SNPTZ!</p>
<p>
Please HIT REPLY and tell us a few things you're going to do this week, BETWEEN THE LINES below.
Or visit <a href="http://www.snptz.com">snptz.com</a>.  
</p>

--~--~--~--~--~--~--~--~--~--~--~--~--~--~<br/>
<span style="font-weight:bold;">WHAT'RE YOU GOING TO DO THIS WEEK?</span><br/>
--~--~--~--~--~--~--~--~--~--~--~--~--~--~<br/>
<br/>
<br/>
REPLACE ME!<br/>
<br/>
<br/>
--~--~--~--~--~--~--~--~--~--~--~--~--~--~<br/>
(list any number of tasks above this line)<br/>
'''

q = models.Profile.all()
q.filter('weekly_email = ', True)
user_list = q.fetch(100)
logging.info("there are %s users" %(len(user_list)))

for user in user_list:
    logging.info("user is %s" % (user.first_name))
    # get the list of what the user planned to do last time
    last_past = user.freshest_taskweek
    if user.first_name is not None:
        first_name = user.first_name
    if last_past is not None:
        # join all the tasks with linebreaks
        tasks_as_lines = user.freshest_taskweek.optimistic_as_str
        # personalize the message_template
        personalized_plaintext_message = plaintext_template % {"username": first_name, "tasks": tasks_as_lines}
        personalized_html_message = html_template % {"username": first_name, "tasks": tasks_as_lines}
    else:
        personalized_html_message = first_time_html % {"username": first_name}
        personalized_plaintext_message = first_time_plaintext % {"username": first_name}

    sender='SNPTZ <weekly@snptz.com>'
    to=user.email
    reply_to='SNPTZ <mail@snptzapp.appspotmail.com>'
    subject='SNPTZ for %s' % datetime.datetime.now().strftime("%b %d")
    body=personalized_plaintext_message
    html=personalized_html_message

    taskqueue.add(url='/sendmail', params={'sender': sender,'to': to,'reply_to': reply_to,'subject': subject,'html':personalized_html_message,'body': personalized_plaintext_message})
