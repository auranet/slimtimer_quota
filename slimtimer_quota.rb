#!/usr/bin/env ruby

require 'date'
require 'optparse'
require 'rubygems'
require 'ruby-debug'
require 'slimtimer4r'

def check_quotas(quotas, entries, args={})
  defaults = {
    :soft_limit => 2 * 60 * 60,
    :report_mode => false,
  }
  args = defaults.merge(args)

  quotas.each do |task, quota_seconds|
    pattern = Regexp.new(task)
    task_entries = entries.find_all{|e| e.task.name =~ pattern}
    total_seconds = task_entries.inject(0){|total, e| total += e.duration_in_seconds}
    if args[:report_mode]
      puts "#{task}: #{total_seconds / 3600.0} of #{quota_seconds / 3600.0}"
    else
      if total_seconds > quota_seconds
        puts "Quota exceeded for '#{task}'! #{total_seconds / 3600.0} > #{quota_seconds / 3600.0}"
      elsif total_seconds > quota_seconds - args[:soft_limit]
        puts "Quota soft limit (#{args[:soft_limit]} / 3600.0}) exceeded for '#{task}'! #{total_seconds / 3600.0} > #{quota_seconds / 3600.0}"
      end
    end
  end
end

def parse_args
  options = {
    :month_quotas => {},
    :half_month_quotas => {},
  }
  optparse = OptionParser.new do |opts|
    opts.banner = "Usage: #{$0} -u email -p passwd -k apikey [options]"

    opts.on("-u", "--user EMAIL", "Email/username on slimtimer") do |user|
      options[:user] = user
    end

    opts.on("-p", "--passwd PASSWD", "Password on slimtimer") do |passwd|
      options[:passwd] = passwd
    end

    opts.on("-k", "--api-key KEY", "API key on slimtimer") do |key|
      options[:key] = key
    end

    opts.on("-q", "--month-quota QUOTA", "task_name:hours") do |quota|
      task, hours = quota.split(':')
      options[:month_quotas][task] = hours.to_f * 60 * 60
    end

    opts.on("-Q", "--half-month-quota QUOTA", "task_name:hours") do |quota|
      task, hours = quota.split(':')
      options[:half_month_quotas][task] = hours.to_f * 60 * 60
    end

    opts.on("-r", "--report-mode", "Print current times and quotas") do
      options[:report_mode] = true
    end
  end
  optparse.parse!(ARGV)

  unless options[:user] and options[:passwd] and options[:key]
    puts 'You must specify and user, password, and api key!'
    puts optparse
    exit
  end

  options
end

options = parse_args
slimtimer = SlimTimer.new(options[:user], options[:passwd], options[:key])
today = Date.today
month_start = Date.new(today.year, today.month, 1)
month_end = Date.new(today.year, today.month, -1)
if today.day < 16
  half_month = [month_start, Date.new(today.year, today.month, 15)]
else
  half_month = [Date.new(today.year, today.month, 16, month_end)]
end

if not options[:month_quotas].empty?
  if options[:report_mode]
    puts 'Report for month quotas'
  end
  month_entries = slimtimer.list_timeentries(month_start, month_end)
  check_quotas(options[:month_quotas], month_entries, options)
end

if not options[:half_month_quotas].empty?
  if options[:report_mode]
    puts 'Report for half month quotas'
  end
  half_month_entries = slimtimer.list_timeentries(*half_month)
  check_quotas(options[:half_month_quotas], half_month_entries, options)
end
