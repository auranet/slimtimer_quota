import logging
import logging.config
import re
from collections import defaultdict
from datetime import date, timedelta
from optparse import OptionParser
from ConfigParser import ConfigParser
from models import get_session, TimeEntry, SlimtimerUser

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

    for task in args:
        print 'Task: {0}'.format(task)
        print

        # Print today's totals
        entries = session.query(TimeEntry).filter(
            TimeEntry.task == task).filter(
            TimeEntry.start_dt >= today).filter(
            TimeEntry.start_dt <= (today + timedelta(days=1)))
        grouped_entries = group_entries(entries)
        print 'Time Today:'
        print
        print_user_totals(session, grouped_entries)
        print

        # Print month's totals
        entries = session.query(TimeEntry).filter(
            TimeEntry.task == task).filter(
            TimeEntry.start_dt >= date(today.year, today.month, 1)).filter(
            TimeEntry.start_dt <= (today + timedelta(days=1)))
        grouped_entries = group_entries(entries)
        print 'Time This Month:'
        print
        print_user_totals(session, grouped_entries)

def group_entries(entries):
    grouped_entries = defaultdict(list)
    for entry in entries:
        grouped_entries[entry.user_id].append(entry)
    return grouped_entries

def print_user_totals(session, user_entries):
    for user_id in user_entries.keys():
        user = session.query(SlimtimerUser).get(user_id)
        hours = sum(map(lambda e: e.duration, user_entries[user_id]))
        print '{0}: {1:0.2f}'.format(user.label, hours)

if __name__ == '__main__':
    main()
