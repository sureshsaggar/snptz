#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 coding=utf-8

import logging
import datetime
from google.appengine.api import mail
from google.appengine.api import users
from google.appengine.ext import db
import models

logging.info('Scheduled task ran.')

def construct_digest(nickname, profile_list):
    digest_greeting = '''
Hi %(username)s,

Here's what your esteemed colleagues are up to this week:


    '''
    # format digest_greeting with user's first_name
    personalized_digest_plaintext = digest_greeting % {"username": nickname}

    for profile in profile_list:
        colleague_summary = '''
%(colleague_nick)s (%(colleague_teams)s)
---------------------
%(colleague_tasks)s

        '''
        # find something to use to identify this colleague
        prof_name = profile.first_name
        if prof_name is None:
            prof_name = profile.nickname

        # list all team names this colleague belongs to
        prof_team_names = ", ".join([m.team.name for m in profile.membership_set])
        prof_taskweek = profile.this_weeks_tw
        # TODO refactor control flow. this is whack
        if prof_taskweek is not None:
            prof_taskweek = prof_taskweek.optimistic
        if prof_taskweek is None:
            prof_tasks = "just chillin... (no reported tasks!)"
        else:
            prof_tasks = "\n".join(prof_taskweek)

        personalized_digest_plaintext = personalized_digest_plaintext +\
             colleague_summary % {"colleague_nick": prof_name,
                        "colleague_teams": prof_team_names,
                        "colleague_tasks": prof_tasks}
    return personalized_digest_plaintext

# XXX TODO this is for testing purposes. change to models.Profile.all() for production
user_list = []
user_list.append(models.Profile.find_by_email('evanmwheeler@gmail.com'))
user_list.append(models.Profile.find_by_email('tedpower@gmail.com'))

for user in user_list:

    # get a list of this user's esteemed_colleagues
    esteemed_colleagues = user.esteemed_colleagues
    if esteemed_colleagues is not None:
        # get user's first_name
        # (or use nickname if first_name isnt specified)
        nick = user.first_name
        if nick is None:
            nick = user.nickname

        # construct a personalized message body
        digest_message_body = construct_digest(nick, esteemed_colleagues)

        digest = mail.EmailMessage(
        sender='SNPTZ <weekly@snptz.com>',
        to=user.email,
        reply_to='SNPTZ <mail@snptzapp.appspotmail.com>',
        # TODO make the subject of the email include the date
        subject='SNPTZ Esteemed Colleagues digest for %s' % datetime.datetime.now().strftime("%b %d"),
        body=digest_message_body)

        digest.send()
