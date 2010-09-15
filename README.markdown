Utility script for checking slimtimer hours

Usage
=====

    Usage: ./slimtimer_quota.rb -u email -p passwd -k apikey [options]
        -u, --user EMAIL                 Email/username on slimtimer
        -p, --passwd PASSWD              Password on slimtimer
        -k, --api-key KEY                API key on slimtimer
        -q, --month-quota QUOTA          task_name:hours
        -Q, --half-month-quota QUOTA     task_name:hours
        -r, --report-mode                Print current times and quotas

Example
=======

./slimtimer_quota.rb -u 'test@example.com' -p myPassword -k XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX -q 'My Task:10'
