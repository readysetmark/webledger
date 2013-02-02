"""
Balance Report Generator

Generates balance report data in a format that is easy to convert to JSON
"""

from decimal import *
import webledger.journal.journal as journal

#========================================================
#	Balance Report Generator
#========================================================

def generate_balance_report(journal_data, report_date):
	"""
	Returns balance report data up to report_date
	"""

	asset_accounts = {account 
		for account in journal_data.all_accounts 
		if "assets" in account.lower() and not "units" in account.lower()}

	liability_accounts = {account
		for account in journal_data.all_accounts
		if "liabilities" in account.lower()}

	# union the two sets
	accounts = asset_accounts | liability_accounts

	# get list of all amounts that apply to each account
	all_account_amounts = flatten_list([
			[(account, entry.amount[0], account == entry.account)
			for account in entry.account_lineage]
		for entry in journal_data.entries
		if entry.account in accounts and entry.header.date <= report_date])

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

		display_list.append((display_name, indent, tuple[1]))


	lines = map(lambda tuple: generate_balance_report_line(tuple), display_list)
	
	return generate_balance_report_data(report_date, lines)


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
	data["account"] = tuple[0]
	data["balance"] = format_amount(tuple[2])
	data["row_class"] = "grand_total" if len(tuple[0]) == 0 else ""
	data["account_style"] = account_style_format.format(padding_left_base + (tuple[1] * indent_padding))

	if len(tuple[0]) == 0:
		data["balance_class"] = ""
	elif tuple[2] > 0:
		data["balance_class"] = "positive"
	else:
		data["balance_class"] = "negative"

	return data


def generate_balance_report_data(report_date, lines):
	"""
	Generates the pystache dictionary for a balance sheet report
	"""
	data = dict()
	data["report_date"] = report_date.strftime("%B %d, %Y")
	data["lines"] = lines
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


def format_amount(amount):
	"""
	Formats an amount into a nice string for display.
	"""
	currency_format_string = "{:,.2f}"
	amount_string = ""

	if amount < 0:
		amount_string = "($" + currency_format_string.format(amount * -1) + ")"
	else:
		amount_string = "$" + currency_format_string.format(amount)

	return amount_string
