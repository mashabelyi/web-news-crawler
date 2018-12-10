#!/usr/bin/env python

#
# Scrape large archives in batches
#
import os, subprocess

## Config
N_CONCURRENT = 10 # number of crawlers to run concurrently
LOG_DIR = 'log' # directory to store logs

source = ['cnn', 'foxnews'] # domains to scrape
# time_range = (20170101, 20171231) # time range to scrape
time_range = (20170101, 20170131) # time range to scrape
interval = (0, 0, 30) # (yrs, months, days) date object

def int_to_date(date_int):
	date = str(date_int)
	yr = date[0:4]
	mm = date[4:6]
	dd = date[6:8]
	return (int(yr), int(mm), int(dd))

def date_str(date):
	return "{}{:02d}{:02d}".format(date[0], date[1], date[2])

def advance_date(date, interval):

	dd = date[2] + interval[2]
	mm = date[1]
	yr = date[0]

	if dd > 31:
		dd = 1
		mm += 1

	mm += interval[1]
	if mm > 12:
		mm = 1
		yr += 1

	yr += interval[0]

	return (yr, mm, dd)


def split_time_range(time_range, interval):
	start = int_to_date(time_range[0])
	end = int_to_date(time_range[1])

	splits = []
	while start < end:
		tmp = advance_date(start, interval)
		splits.append((date_str(start), date_str(tmp)))
		start = advance_date(tmp, (0, 0, 1))

	return splits

def build_command(data):
	data['log'] = LOG_DIR
	return "python run.py --start {start} --end {end} --source {source} &> {log}/{source}.{start}.{end}.log&".format(**data)


## make log directory if needed
if not os.path.exists(LOG_DIR):
	os.makedirs(LOG_DIR)

## split into time ranges
splits = split_time_range(time_range, interval)

## inputs for each source
batch = []
for time in splits:
	for name in source:
		cmd = build_command({
			'source': name,
			'start': time[0],
			'end': time[1] 
			})
		batch.append(cmd)


## scrape until everything is done
for line in batch:
	print(line)
	subprocess.run(line, shell=True)




