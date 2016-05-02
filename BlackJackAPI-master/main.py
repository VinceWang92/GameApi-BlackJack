#!/usr/bin/env python
# Contains scripts and cron and taskqueue jobs.
import logging

import webapp2
from google.appengine.api import mail, app_identity
from api import blackJackApi

from models import User
from utils import get_by_urlsafe

# Send all users a reminder email. Currently set to email once a year.
class SendReminderEmail(webapp2.RequestHandler):
    def get(self):
        """Send a reminder email to each User."""
        app_id = app_identity.get_application_id()
        users = User.query(User.email != None)
        for user in users:
            subject = 'This is a reminder!'
            body = 'Hello {}, Want to play some BlackJack?'.format(user.name)
            mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                           user.email,
                           subject,
                           body)


# Sends a user an email when they create a User
class SendUserEmail(webapp2.RequestHandler):
    def post(self):
        """Send an email upon User Creation"""
        logging.debug('HOOBUS"')
        user = get_by_urlsafe(self.request.get('user_key'), User)
        subject = 'Welcome!'
        body = "Welcome to BlackJack!"
        logging.debug(body)
        mail.send_mail('noreply@{}.appspotmail.com'.
                       format(app_identity.get_application_id()),
                       user.email,
                       subject,
                       body)




app = webapp2.WSGIApplication([
    ('/crons/send_reminder', SendReminderEmail),
    ('/tasks/send_user_email', SendUserEmail),
], debug=True)
