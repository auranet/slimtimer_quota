Utility script for checking slimtimer hours

Installing requirements
=======================

    pip install -r requirements.txt

Usage
=====

    Usage: slimtimer_quota.py -u email -p passwd [options]

    Options:
      -h, --help            show this help message and exit
      -u USER, --user=USER  Email/username on slimtimer
      -p PASSWORD, --passwd=PASSWORD
                            Password on slimtimer
      -Q MONTH_QUOTAS, --month-quota=MONTH_QUOTAS
                            task_name:hours
      -q HALF_MONTH_QUOTAS, --half-month-quota=HALF_MONTH_QUOTAS
                            task_name:hours
      -r, --report-mode     Print current times and quotas
      -t THRESHOLD, --threshold=THRESHOLD
                            Number of hours within quota to warn


Example
=======

./slimtimer_quota.py -u 'test@example.com' -p myPassword -q 'My Task:10'
