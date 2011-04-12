#!/usr/bin/env python

import calendar
import logging
import logging.config
import re
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from optparse import OptionParser
from ConfigParser import ConfigParser
from models import get_session, TimeEntry

def check_quotas(config, report_mode=False):
    quotas = get_quotas(config)
    session = get_session(config)

    results = []
    for name, quota in quotas.iteritems():
        entries = session.query(TimeEntry).filter(
            TimeEntry.start_dt >= quota['start']).filter(
            TimeEntry.start_dt <= quota['end'])
        quota['total'] = sum([entry.duration for entry in entries
            if quota['regex'].search(entry.task)])
        # Unpredictable arithmetic in 2.6, if not cast to float
        quota['total'] = float(quota['total'])
        if report_mode or quota['total'] + quota['threshold'] > quota['hours']:
            results.append((name[6:], quota))
    if results:
        print_results(results)

def print_results(results):
    for name, quota in results:
        print "{0}: {total:.2f} of {hours:.2f} hours for {start} to {end}".format(name, **quota)

def month_range(today=date.today()):
    start_date = date(today.year, today.month, 1)
    end_date = date(today.year, today.month,
        calendar.monthrange(today.year, today.month)[1])
    return start_date, end_date

def half_month_range(today=date.today()):
    if today.day < 16:
        start_date = date(today.year, today.month, 1)
        end_date = date(today.year, today.month, 15)
    else:
        start_date = date(today.year, today.month, 16)
        end_date = date(today.year, today.month,
        calendar.monthrange(today.year, today.month)[1])
    return start_date, end_date

def build_quota(config, section):
    regex = re.compile(config.get(section, 'regex'))
    hours = float(config.get(section, 'hours'))
    if config.has_option(section, 'range'):
        raw_range = config.get(section, 'range')
        if raw_range in ('half-month', 'half month'):
            start, end = half_month_range()
        elif raw_range == 'month':
            start, end = month_range()
        else:
            raise RuntimeError('Bad range for {0}'.format(section))
    else:
        start, end = month_range()
    if config.has_option(section, 'threshold'):
        threshold = float(config.get(section, 'threshold'))
    else:
        threshold = 2
    return {
        'regex': regex,
        'hours': hours,
        'start': start,
        'end': end,
        'threshold': threshold,
    }

def get_quotas(config):
    quotas = {}
    for section in config.sections():
        if not section.startswith('quota'):
            continue
        try:
            quotas[section] = build_quota(config, section)
        except:
            e = ''.join(traceback.format_exception(*sys.exc_info()))
            logging.error('Could not build quota for {0}:\n{1}'.format(
                section, e))
    return quotas

def main():
    parser = OptionParser('usage: %prog [options]')
    parser.add_option("-f", "--config-file", dest='config_file',
        help="Configuration file")
    parser.add_option("-r", "--report-mode", dest='report_mode',
        action='store_true', help="Print current times and quotas")
    options, args = parser.parse_args()

    if not (options.config_file):
        parser.error("Please specify a configuration file.")

    logging.config.fileConfig(options.config_file)
    config = ConfigParser()
    config.read(options.config_file)
    check_quotas(config, report_mode=options.report_mode)

if __name__ == '__main__':
    main()
