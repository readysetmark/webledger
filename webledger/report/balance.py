"""
Balance Report Generator

Generates balance report data in a format that is easy to convert to JSON
"""

from decimal import *
import datetime
import calendar
import json
import re
import webledger.journal.journal as journal

# duped from run.py. should find a better place for it
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


#========================================================
#	Balance Report Parameters class
#========================================================

class BalanceReportParameters:
	@classmethod
	def from_command(cls, command):
		"""
		Create a parameters object from a query command
		"""
		accounts_with = []
		exclude_accounts_with = []
		period = []
		period_start = None
		period_end = None
		title = []
		phase = "select"

		for token in command:
			if token == ":excluding":
				phase = "filter"
			elif token == ":period":
				phase = "period"
			elif token == ":since":
				phase = "periodstart"
			elif token == ":upto":
				phase = "periodend"
			elif token == ":title":
				phase = "title"
			elif phase == "select":
				accounts_with.append(token)
			elif phase == "filter":
				exclude_accounts_with.append(token)
			elif phase == "period":
				period.append(token)
			elif phase == "periodstart":
				period_start = datetime.datetime.strptime(token, "%Y/%m/%d").date()
				phase = "invalid"
			elif phase == "periodend":
				period_end = datetime.datetime.strptime(token, "%Y/%m/%d").date()
				phase = "invalid"
			elif phase == "title":
				title.append(token)
			else:
				raise Exception("Invalid token in balance command parameters: " + token)

		# parse period
		# TODO: should move this somewhere else eventually
		if len(period) > 0:
			period_str = " ".join(period)

			if period_str == "this month":
				today = datetime.date.today()
				period_start = datetime.date(year=today.year, month=today.month, day=1)
				period_end = datetime.date(year=today.year, month=today.month, day=calendar.monthrange(today.year, today.month)[1])
			elif period_str == "last month":
				today = datetime.date.today()
				month_ago = date_add_months(today, -1)
				period_start = datetime.date(year=month_ago.year, month=month_ago.month, day=1)
				period_end = datetime.date(year=month_ago.year, month=month_ago.month, day=calendar.monthrange(month_ago.year, month_ago.month)[1])
			else:
				raise Exception("Invalid period expression: " + period_str)

		return cls(title=" ".join(title) if len(title) > 0 else None,
			accounts_with=accounts_with if len(accounts_with) > 0 else None,
			exclude_accounts_with=exclude_accounts_with if len(exclude_accounts_with) > 0 else None,
			period_start=period_start,
			period_end=period_end)


	def __init__(self, title=None,
			accounts_with=None, exclude_accounts_with=None,
			period_start=None, period_end=None):
		self.title = title if title != None else "Balance"
		self.period_start = period_start
		self.period_end = period_end
		self.accounts_with = accounts_with
		self.exclude_accounts_with = exclude_accounts_with




#========================================================
#	Balance Report Generator
#========================================================

def generate_balance_report(journal_data, parameters):
	"""
	Returns balance report data based on report parameters provided
	"""
	lines = None

	# filter accounts based on accounts to include/exclude
	accounts = filter_accounts(journal_data, parameters)

	# get list of all amounts that apply to each account
	# within the period start/end parameters
	all_account_amounts = flatten_list([
			[(account, entry.amount[0], account == entry.account)
			for account in entry.account_lineage]
		for entry in journal_data.entries
		if entry.account in accounts and within_period(entry.header.date, parameters)])

	# reduce the list of accounts to ones that had activity in the report period
	accounts = set([tuple[0] for tuple in all_account_amounts])

	if len(all_account_amounts) > 0:
		# reduce the list to calculate account balances
		all_account_balances = [
			reduce((lambda t1, t2: (t1[0], t1[1]+t2[1])),
				filter((lambda tuple: tuple[0] == account), all_account_amounts))
			for account in accounts]

		# filter to non-zero accounts only
		nonzero_account_balances = filter(
			(lambda tuple: tuple[1] != 0), all_account_balances)
		
		# filter parent accounts that only have one direct descendant
		# these accounts will be the ones where there is another account that
		# starts with the same name, but is longer and has the same amount
		account_balance_list = filter(
			(lambda tuple: keep_tuple(tuple, nonzero_account_balances)),
			nonzero_account_balances)

		# calculate total balance
		total_balance = sum([tuple[1] for tuple in all_account_amounts if tuple[2]])

		account_balance_list.sort(key=lambda tuple: tuple[0])
		account_balance_list.append(("", total_balance))

		# format account name for display
		display_list = list()
		for tuple in account_balance_list:
			indent = 0
			parent_name = ""
			display_name = tuple[0]

			for other in account_balance_list:
				if display_name.startswith(other[0]) and display_name != other[0] and display_name[len(other[0])] == ":":
					parent_name = other[0]
					indent += 1

			if len(parent_name) > 0:
				display_name = display_name.replace(parent_name + ":", "")

			display_list.append((tuple[0], tuple[1], display_name, indent))

		lines = map(lambda tuple: generate_balance_report_line(tuple), display_list)
	
	return generate_balance_report_data(parameters, lines)


#========================================================
#	Balance Report Generator Helper Functions
#========================================================

def filter_accounts(journal_data, report_parameters):
	"""
	Get list of accounts to report on based on report_parameters.
	"""
	accounts = {account
		for account in journal_data.all_accounts
		if (report_parameters.accounts_with == None
				or len(report_parameters.accounts_with) == 0 
				or one_of_in(report_parameters.accounts_with, account))
			and (report_parameters.exclude_accounts_with == None
				or len(report_parameters.exclude_accounts_with) == 0
				or not one_of_in(report_parameters.exclude_accounts_with, account))}

	return accounts


def one_of_in(terms, string):
	"""
	Returns true if string contains one of the terms in terms.
	"""
	regex = re.compile("|".join(terms), re.IGNORECASE)
	return True if regex.search(string) else False


def within_period(entry_date, parameters):
	"""
	Returns true if entry_date meets period start/end parameters
	"""
	within_period = True

	if parameters.period_start != None and entry_date < parameters.period_start:
		within_period = False

	if parameters.period_end != None and entry_date > parameters.period_end:
		within_period = False

	return within_period


def keep_tuple(tuple, tuple_list):
	"""
	filter parent accounts that only have one direct descendant
	these accounts will be the ones where there is another account that
	starts with the same name, but is longer and has the same amount
	"""
	for t in tuple_list:
		if t[0].startswith(tuple[0]) and len(t[0]) > len(tuple[0]) and t[1] == tuple[1]:
			return False

	return True


#========================================================
#	Balance Report Data Structure Functions
#========================================================

def generate_balance_report_line(tuple):
	"""
	Generates the pystache dictionary for a balance sheet line
	"""
	account_style_format = "padding-left: {:d}px;"
	padding_left_base = 8
	indent_padding = 20

	data = dict()
	data["account"] = tuple[2]
	data["balance"] = format_amount(tuple[1])
	data["row_class"] = "grand_total" if len(tuple[0]) == 0 else ""
	data["balance_class"] = tuple[0].split(":")[0].lower()
	data["account_style"] = account_style_format.format(padding_left_base + (tuple[3] * indent_padding))

	return data


def generate_balance_report_data(parameters, lines):
	"""
	Generates the pystache dictionary for a balance sheet report
	"""
	date_format = "%B %d, %Y"
	data = dict()
	data["title"] = parameters.title
	data["lines"] = lines

	# generate report subtitle	
	if parameters.period_start != None and parameters.period_end != None:
		data["subtitle"] = "For the period of " + parameters.period_start.strftime(date_format) + " to " + parameters.period_end.strftime(date_format)
	elif parameters.period_start != None:
		data["subtitle"] = "Since "	+ parameters.period_start.strftime(date_format)
	elif parameters.period_end != None:
		data["subtitle"] = "Up to "	+ parameters.period_end.strftime(date_format)
	else:
		data["subtitle"] = "As of "	+ datetime.date.today().strftime("%B %d, %Y")

	return data


#========================================================
#	Utility Functions
#========================================================

def flatten_list(list):
	"""
	Flattens a list of lists to a single list
	"""
	return [item 
		for sublist in list
			for item in sublist]


def format_amount(amount, negative_in_parentheses=True):
	"""
	Formats an amount into a nice string for display.
	"""
	currency_format_string = "{:,.2f}"
	amount_string = ""

	if amount < 0 and negative_in_parentheses:
		amount_string = "($" + currency_format_string.format(amount * -1) + ")"
	else:
		amount_string = "$" + currency_format_string.format(amount)

	return amount_string


#===============================================================================
#===============================================================================
# Monthly Summary


class MonthlySummaryParameters:

	def __init__(self, title="Monthly Summary", 
			accounts_with=None, exclude_accounts_with=None,
			period_start=None, period_end=datetime.date.today()):
		self.title = title
		self.period_start = period_start
		self.period_end = period_end
		self.accounts_with = accounts_with
		self.exclude_accounts_with = exclude_accounts_with


def generate_monthly_summary(journal_data, parameters):
	"""
	Returns a total per month
	"""

	# filter accounts based on accounts to include/exclude
	accounts = filter_accounts(journal_data, parameters)

	# get list of all amounts that apply to each account
	# within the period start/end parameters
	all_month_amounts = [
		#(datetime.date(year=entry.header.date.year,month=entry.header.date.month,day=calendar.monthrange(entry.header.date.year, entry.header.date.month)[1]), entry.amount[0])
		(datetime.date(year=entry.header.date.year,month=entry.header.date.month,day=1), entry.amount[0])
		for entry in journal_data.entries
		if entry.account in accounts]

	months = set([tuple[0] for tuple in all_month_amounts if within_period(tuple[0], parameters)])

	monthly_amounts = [
		reduce(lambda t1, t2: (month, t1[1] + t2[1]),
			filter(lambda tuple: tuple[0] <= month, all_month_amounts))
		for month in months]

	monthly_amounts.sort(key=lambda tuple: tuple[0])

	
	tuples = list()
	currency_format_string = "{:.2f}"
	display_currency_format_string = "{:,.2f}"

	for tuple in monthly_amounts:
		d = dict()
		d["date"] = tuple[0].strftime("%d-%b-%Y")
		d["amount"] = currency_format_string.format(tuple[1])
		d["hover"] = tuple[0].strftime("%b %Y") + ": " + format_amount(tuple[1])
		tuples.append(d)

	monthly_summary = dict()
	monthly_summary["title"] = parameters.title
	monthly_summary["tuples"] = json.dumps(tuples, indent=4, separators=(',', ': '))
	return monthly_summary



#========================================================
#	Register Report Generator
#========================================================

def generate_register_report(journal_data, parameters):
	"""
	Returns register report data based on report parameters provided
	"""

	# filter accounts based on accounts to include/exclude
	accounts = filter_accounts(journal_data, parameters)

	# get list of all entries that apply to each account
	# within the period start/end parameters, grouped by the transaction header
	transactions = dict()

	for entry in journal_data.entries:
		if entry.account in accounts and within_period(entry.header.date, parameters):
			key = (entry.header.date, entry.header.description)
			if key in transactions:
				transactions[key].append(entry)
			else:
				transactions[key] = [entry]

	# generate line items
	# keep a running total
	total = 0
	lines = []
	for key in sorted(transactions.keys()):
		key_first_line = True
		# TODO: sorted_entries = transactions[key].sort(key=lambda entry: entry.amount[0])
		for entry in transactions[key]:
			line = dict()
			total += entry.amount[0]
			if key_first_line:
				key_first_line = False
				line["date"] = entry.header.date
				line["description"] = entry.header.description
			else:
				line["td-class"] = "no-border-top"
			line["account"] = entry.account
			line["amount"] = format_amount(entry.amount[0], False)
			line["total"] = format_amount(total, False)
			lines.append(line)

	register = dict()
	register["title"] = "Register Report"
	register["lines"] = lines

	return register
