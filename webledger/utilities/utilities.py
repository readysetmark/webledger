"""
Utilities

Contains general utility functions for dates, etc...
"""

import datetime
import calendar


def date_add_months(date, num_months):
	"""
	Adds num_months to date
	"""
	year, month, day = date.timetuple()[:3]

	month += num_months
	
	if num_months > 0:
		while month > 12:
			month -= 12
			year += 1
	elif num_months < 0:
		while month < 1:
			month += 12
			year -= 1

	month_max_days = calendar.monthrange(year, month)[1]
	if day > month_max_days:
		day = month_max_days

	return datetime.date(year=year, month=month, day=day)
