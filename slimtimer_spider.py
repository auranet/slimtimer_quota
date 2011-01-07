#!/usr/bin/env python

import calendar
import csv
import logging
import logging.config
import re
import simplejson
from ConfigParser import ConfigParser
from datetime import date, timedelta
from lxml.html import document_fromstring
from mechanize import Browser
from optparse import OptionParser
from urllib import urlencode

DEFAULT_PARAMS = {
    'row': 'task',
    'column': 'time',
    'report': 'timesheet',
    'start_date': (date.today() - timedelta(days=365)).strftime("%m/%d/%Y"),
    'end_date': date.today().strftime("%m/%d/%Y"),
    'daterange': 'custom_range',
    'user_ids': '',
    'users': 'specific',
    'task_tags': '',
    'tasks': '',
    'task': 'all',
    'run_report': 'Run Report',
    'user[report_rounding_target]': 'total',
    'user[report_rounding_in_seconds]': '',
    'user[report_minimum_entry_duration]': '',
}

class SlimtimerSpider(object):

    def __init__(self, username, password):
        self.logger = logging.getLogger('SlimtimerSpider')
        self.username = username
        self.password = password
        self.br = Browser()
        # Uncomment these for tons of HTTP debugging
        #self.br.set_debug_redirects(True)
        #self.br.set_debug_responses(True)
        #self.br.set_debug_http(True)
        self.login()

    def login(self):
        self.logger.debug('Logging in as {}'.format(self.username))
        self.br.open('http://slimtimer.com/')
        self.br.select_form(nr=0)
        self.br['user[email]'] = self.username
        self.br['user[password]'] = self.password
        self.br.submit()

    def get_report(self, **kwargs):
        # Mutate users_ids list to a string like this
        # 123423=1|12312=1|
        if isinstance(kwargs['user_ids'], list):
            kwargs['user_ids'] = '|'.join(
                ["{}=1".format(id) for id in kwargs['user_ids']])

        params = {}

        params.update(DEFAULT_PARAMS)
        params.update(kwargs)
        for date_arg in ('start_date', 'end_date'):
            # date, time, datetime?
            if hasattr(params[date_arg], 'strftime'):
                params[date_arg] = params[date_arg].strftime('%m/%d/%Y')
        report_url = 'http://slimtimer.com/report/run'
        self.br.open(report_url, urlencode(params))
        js = self.br.response().read()
        # js = \
        # Element.update("results", "<sweet-html/>");
        # Element.hide("loading-indicator");
        # Element.show("results-wrapper");
        html = js.split('\n')[0][27:-3].decode('string_escape')
        doc = document_fromstring(html)
        csv_link = doc.cssselect('a#export-csv-report')[0]
        csv_response = self.br.open(csv_link.attrib['href'])
        csvin = csv.reader(csv_response)
        headers = None
        for i, row in enumerate(csvin):
            if i < 1:
                headers = row
                continue
            if row[0] == 'Total Hours':
                break
            yield dict(zip(headers, row))

    def get_users(self):
        """Get a dictionary of Slimtimer ids and usernames"""

        response = self.br.open(
            'http://slimtimer.com/report/update_users_filter',
            urlencode(DEFAULT_PARAMS))
        js = response.read()
        data = js.split(' = ')[-1]
        json = data.replace('id', '"id"').replace('label', '"label"')
        users = simplejson.loads(json)
        return users

def main():
    parser = OptionParser('usage: %prog -f config.conf')
    parser.add_option("-f", "--config-file", dest='config_file',
        help="Configuration file")
    options, args = parser.parse_args()

    if not (options.config_file):
        parser.error("Please specify a configuration file.")

    logging.config.fileConfig(options.config_file)
    config = ConfigParser()
    config.read(options.config_file)
    ss = SlimtimerSpider(
        config.get('slimtimer', 'user'),
        config.get('slimtimer', 'password'),
    )
    logging.info('Retriving users from Slimtimer')
    users = ss.get_users()
    logging.info('Found {} users'.format(len(users)))
    for user in users:
        logging.info(
            'Retriving time entries for {id} ({label})'.format(**user))
        for entry in ss.get_report(user_ids=[user['id']],
            start_date=(date.today() - timedelta(days=1)),
            end_date=date.today()):
            logging.debug(str(entry))

if __name__ == '__main__':
    main()
