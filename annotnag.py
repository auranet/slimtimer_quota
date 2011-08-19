#!/usr/bin/env python

import logging
import logging.config
import re
import smtplib
from collections import defaultdict
from datetime import date, timedelta
from email.mime.text import MIMEText
from optparse import OptionParser
from sqlalchemy import not_, or_
from ConfigParser import ConfigParser
from models import get_session, TimeEntry, SlimtimerUser

def email_offenders(session, user_entries):
    for user_id in user_entries.keys():
        user = session.query(SlimtimerUser).get(user_id)
        if user.email and user_entries[user_id]:
            lines = ['Following Non-Aura entries require annotations:']
            user = session.query(SlimtimerUser).get(user_id)
            for entry in user_entries[user_id]:
                lines.append(' '.join(
                    [' ', user.label, entry.task, str(entry.start_dt)]))
            msg = MIMEText('\n'.join(lines))
            msg['Subject'] = 'Slimtimer Annotation Nagging'
            msg['From'] = 'noreply@aura-software.com'
            msg['To'] = user.email
            smtp = smtplib.SMTP('localhost')
            smtp.sendmail('noreply@aura-software.com', [user.email],
                msg.as_string())

def group_entries(entries):
    grouped_entries = defaultdict(list)
    for entry in entries:
        grouped_entries[entry.user_id].append(entry)
    return grouped_entries

def print_alerts(session, user_entries):
    for user_id in user_entries.keys():
        print
        user = session.query(SlimtimerUser).get(user_id)
        for entry in user_entries[user_id]:
            print '  ', user.label, entry.task, entry.start_dt

def main():
    parser = OptionParser('usage: %prog [options] task')
    parser.add_option("-f", "--config-file", dest='config_file',
        help="Configuration file")
    options, args = parser.parse_args()

    if not (options.config_file):
        parser.error("Please specify a configuration file.")

    logging.config.fileConfig(options.config_file)
    config = ConfigParser()
    config.read(options.config_file)

    session = get_session(config)
    today = date.today()

    entries = session.query(TimeEntry).filter(
        not_(TimeEntry.task.like('Aura %'))).filter(
        or_(TimeEntry.comment == None, TimeEntry.comment == '')).filter(
        TimeEntry.start_dt >= today).filter(
        TimeEntry.start_dt <= (today + timedelta(days=1)))

    grouped_entries = group_entries(entries)

    if grouped_entries:
        print 'Following Non-Aura entries require annotations:'
        print_alerts(session, grouped_entries)
        email_offenders(session, grouped_entries)

if __name__ == '__main__':
    main()
