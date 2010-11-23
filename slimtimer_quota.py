#!/usr/bin/env python

import calendar
import re
from datetime import date
from lxml.html import document_fromstring
from mechanize import Browser
from optparse import OptionParser
from urllib import urlencode

class SlimtimerSpider(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.br = Browser()
        self.login()

    def login(self):
        self.br.open('http://slimtimer.com/')
        self.br.select_form(nr=0)
        self.br['user[email]'] = self.username
        self.br['user[password]'] = self.password
        self.br.submit()

    def get_month_totals(self, today=date.today()):
        start_date = date(today.year, today.month, 1)
        end_date = date(today.year, today.month,
            calendar.monthrange(today.year, today.month)[1])
        return self.get_report(start_date=start_date, end_date=end_date)

    def get_half_month_totals(self, today=date.today()):
        if today.day < 16:
            start_date = date(today.year, today.month, 1)
            end_date = date(today.year, today.month, 15)
        else:
            start_date = date(today.year, today.month, 16)
            end_date = date(today.year, today.month,
            calendar.monthrange(today.year, today.month)[1])
        return self.get_report(start_date=start_date, end_date=end_date)

    def get_report(self, **kwargs):
        params = {
            'row': 'task',
            'column': 'time',
            'report': 'audit',
            'start_date': '9/17/2010',
            'end_date': '9/24/2010',
            'daterange': 'custom_range',
            'user_ids': '',
            'users': 'all',
            'task_tags': '',
            'tasks': '',
            'task': 'all',
            'run_report': 'Run Report',
            'user[report_rounding_target]': 'total',
            'user[report_rounding_in_seconds]': '360',
            'user[report_minimum_entry_duration]': '',
        }
        params.update(kwargs)
        for date_arg in ('start_date', 'end_date'):
            # date, time, datetime?
            if hasattr(params[date_arg], 'strftime'):
                params[date_arg] = params[date_arg].strftime('%m/%d/%Y')
        report_url = 'http://slimtimer.com/report/run'
        response = self.br.open(report_url, urlencode(params))
        js = response.read()
        # js = \
        # Element.update("results", "<sweet-html/>");
        # Element.hide("loading-indicator");
        # Element.show("results-wrapper");
        html = js.split('\n')[0][27:-3].decode('string_escape')
        doc = document_fromstring(html)
        rows = doc.cssselect('table.report tr')[1:-1]
        totals = {}
        for row in rows:
            task = row.cssselect('.task')[0].text_content()
            hours = float(row.cssselect('.hours')[0].text_content())
            if task in totals:
                totals[task] += hours
            else:
                totals[task] = hours
        return totals

def check_quotas(options):
    ss = SlimtimerSpider(options.user, options.password)

    if options.half_month_quotas:
        quotas = ss.get_half_month_totals()
        results = []
        for quota_def in options.half_month_quotas:
            task, quota_hours, total_hours = get_report(quota_def, quotas)
            if options.report_mode or total_hours + options.threshold > quota_hours:
                results.append((task, quota_hours, total_hours))
        print_results("Half month quotas", results)

    if options.month_quotas:
        quotas = ss.get_month_totals()
        results = []
        for quota_def in options.month_quotas:
            task, quota_hours, total_hours = get_report(quota_def, quotas)
            if options.report_mode or total_hours + options.threshold > quota_hours:
                results.append((task, quota_hours, total_hours))
        print_results("Month quotas", results)

def print_results(title, results):
    if results:
        print title
        for task, quota_hours, total_hours in results:
            print "\"{0}\" {1:.2f} of {2:.2f} hours".format(
                task, total_hours, quota_hours)

def get_report(criteria, quotas_dict):
    task_pattern, hours = criteria.split(':')
    task_re = re.compile(task_pattern)
    total = sum([quotas_dict[k] for k in quotas_dict.keys()
        if task_re.search(k)])
    return task_pattern, float(hours), total

def main():
    parser = OptionParser('usage: %prog -u email -p passwd [options]')
    parser.add_option("-u", "--user", dest='user',
        help="Email/username on slimtimer")
    parser.add_option("-p", "--passwd", dest='password',
        help="Password on slimtimer")
    parser.add_option("-Q", "--month-quota", dest='month_quotas',
        default=[], action='append', help="task_name:hours")
    parser.add_option("-q", "--half-month-quota", dest='half_month_quotas',
        default=[], action='append', help="task_name:hours")
    parser.add_option("-r", "--report-mode", dest='report_mode',
        action='store_true', help="Print current times and quotas")
    parser.add_option("-t", "--threshold", dest='threshold',
        default='2', help="Number of hours within quota to warn")
    options, args = parser.parse_args()

    if not (options.user and options.password):
        parser.error("Need a email and password to login to slimtimer")

    options.threshold = float(options.threshold)

    check_quotas(options)

if __name__ == '__main__':
    main()
