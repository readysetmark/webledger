"""
Ledger Reports
- Income Statement
- Balance Sheet
"""
import DateFunctions
import pystache
import LedgerData


#========================================================
#		Pretty printing functions
#========================================================

def _remove_top_account_name(account):
	"""
	Removes the top-level account from the account name.
	i.e. "Expenses:Auto:Gas" returns as "Auto:Gas"
	"""
	loc = account.find(":") + 1
	name = account

	if loc < len(account):
		name = account[loc:]

	return name


def _print_amounts(amounts_dict):
	"""
	Prints all the amount/commodity combinations in an amount dictionary.
	"""
	currency_string_format = "{:,.2f}"
	commodity_string_format = "{:,.4f}"
	amount_string = ""

	for commodity, amount in amounts_dict.items():
		if len(amount_string) > 0:
			amount_string += "<br />"

		if commodity == "$":
			amount_string += currency_string_format.format(amount)
		else:
			amount_string += commodity_string_format.format(amount) + " " + commodity

	return amount_string



#========================================================
#		Filter function creators
#========================================================

def _create_filter_not_a(filter_a):
	"""
	Returns a function that applies (not A)
	"""
	return (lambda thing: not filter_a(thing))


def _create_filter_a_or_b(filter_a, filter_b):
	"""
	Returns a function that applies (A or B)
	"""
	return (lambda thing: filter_a(thing) or filter_b(thing))


def _create_filter_a_and_b(filter_a, filter_b):
	"""
	Returns a function that applies (A and B)
	"""
	return (lambda thing: filter_a(thing) and filter_b(thing))


def _create_filter_account_name_starts_with(account_name):
	"""
	Returns a function for filtering account names starting with account_name
	"""
	return (lambda account: account.find(account_name) == 0)


def _create_filter_account_name_in(account_list):
	"""
	Returns a function for filtering account names to those in a list
	"""
	return (lambda account: account in account_list)


def _create_filter_account_name_contains(text):
	"""
	Returns a function for filtering account names containing certain text
	"""
	return (lambda account: account.find(text) >= 0)



#========================================================
#		Render Via Pystatche
#========================================================

def _render_report(template_file, output_file, data):
	"""
	Using Pystache, render the data using the template into the output file.
	"""
	template = open(template_file).read()

	f = open(output_file,"w")
	f.write(pystache.render(template, data))
	f.close()



#========================================================
#		Generate All Reports
#========================================================

def GenerateAllReports(report_data, report_date):
	"""
	Generates all the reports with an index
	"""
	templateFilename = "templates\\Index.html"
	outputFilename = "output\\Index.html"

	data = dict()
	reports = list()
	reports.append(GenerateBalanceSheetReport(report_data, report_date))
	reports.append(GenerateIncomeStatementReport(report_data, report_date))

	data["reports"] = reports	
	_render_report(templateFilename, outputFilename, data)

	return reports



#========================================================
#		Income Statement Report
#========================================================


def GenerateIncomeStatementReport(report_data, report_month):
	"""
	Generate the Income Statement Report
	"""
	filename = "IncomeStatement.html"
	templateFilename = "templates\\" + filename
	outputFilename = "output\\" + filename

	data = _GetIncomeStatementData(report_data, report_month)
	_render_report(templateFilename, outputFilename, data)

	return {"name": "Income Statement", "file": filename}


def _GetIncomeStatementData(report_data, report_month):
	"""
	Generate the JSON data for the Income Statement Report
	"""

	time_format = "%b %Y"

	data = dict()

	columns = dict()
	columns["this_month"] = report_month
	columns["last_month"] = DateFunctions.date_add_months(report_month, -1)
	columns["two_months_ago"] = DateFunctions.date_add_months(report_month, -2)
	columns["three_months_ago"] = DateFunctions.date_add_months(report_month, -3)
	columns["six_months_ago"] = DateFunctions.date_add_months(report_month, -6)
	columns["one_year_ago"] = DateFunctions.date_add_months(report_month, -12)
	columns["two_years_ago"] = DateFunctions.date_add_months(report_month, -24)
	columns["total"] = "Total"

	# column titles	
	
	column_titles = dict()
	for key in columns.keys():
		if key == "total":
			column_titles[key] = columns[key]
		else:
			column_titles[key] = columns[key].strftime(time_format)
	
	data["column_titles"] = column_titles
	
	# income accounts and subtotal

	income_account_filter = _create_filter_account_name_in(["Income:Bonus", "Income:Salary"])
	data["income_accounts"] = _get_monthly_totals_by_account(report_data, columns, income_account_filter)
	data["income_subtotal"] = _get_monthly_totals_aggregate(report_data, columns, income_account_filter)

	# expense accounts and subtotal

	expense_account_filter = _create_filter_account_name_starts_with("Expense")
	data["expense_accounts"] = _get_monthly_totals_by_account(report_data, columns, expense_account_filter)
	data["expense_subtotal"] = _get_monthly_totals_aggregate(report_data, columns, expense_account_filter)

	# grand total

	grand_total_account_filter = _create_filter_a_or_b(income_account_filter, expense_account_filter)
	data["grand_total"] = _get_monthly_totals_aggregate(report_data, columns, grand_total_account_filter)
	
	return data


def _get_monthly_totals_by_account(report_data, columns, account_filter):
	"""
	Returns a list of monthly totals for the columns in columns for
	each account determined by account_filter.
	"""
	monthly_totals = report_data.get_monthly_totals()
	final_balances = report_data.get_final_balances()

	# get list of accounts
	accounts = [account for account in report_data.get_account_list(False) if account_filter(account)]
	accounts.sort()

	# generate row data
	rows = list()
	row_count = 0
	for account in accounts:
		row = dict()

		if row_count % 2 == 0:
			row["row_class"] = "even"
		else:
			row["row_class"] = "odd"

		row_count = row_count + 1

		row["account_name"] = _remove_top_account_name(account)

		for columnkey in columns.keys():
			if columnkey == "total":
				row[columnkey] = _print_amounts(final_balances[account])
			else:
				key = (account, columns[columnkey])
		
				if key in monthly_totals.keys():
					row[columnkey] = _print_amounts(monthly_totals[key])
				else:
					row[columnkey] = "&nbsp;"

		rows.append(row)

	return rows


def _get_monthly_totals_aggregate(report_data, columns, account_filter):
	"""
	Writes aggregated monthly totals for the columns in columns and the total
	aggregate balance for the accounts determined by account_filter.
	"""
	monthly_totals = report_data.get_monthly_totals()
	final_balances = report_data.get_final_balances()

	# get list of accounts
	accounts = [account for account in report_data.get_account_list(False) if account_filter(account)]

	row = dict()
	for columnkey in columns.keys():
		if columnkey == "total":
			aggregate_total = dict()
			aggregate_total["$"] = 0
			for account in accounts:
				LedgerData.add_amounts_to_dictionary(aggregate_total, final_balances[account])

			row[columnkey] = _print_amounts(aggregate_total)
		else:
			keys = [(account, columns[columnkey]) for account in accounts]
			aggregate_total = dict()
			aggregate_total["$"] = 0
			for key in keys:
				if key in monthly_totals:
					LedgerData.add_amounts_to_dictionary(aggregate_total, monthly_totals[key])

			row[columnkey] = _print_amounts(aggregate_total)
	
	return row



#========================================================
#		Balance Sheet Report
#========================================================

def GenerateBalanceSheetReport(report_data, report_date):
	"""
	Generate the Balance Sheet Report
	"""
	filename = "BalanceSheet.html"
	templateFilename = "templates\\" + filename
	outputFilename = "output\\" + filename

	data = _GetBalanceSheetData(report_data, report_date)
	_render_report(templateFilename, outputFilename, data)

	return {"name": "Balance Sheet", "file": filename}


def _GetBalanceSheetData(report_data, report_date):
	"""
	Generate the JSON data for the Balance Sheet Report
	"""
	date_format = "%B %d, %Y"

	data = dict()

	data["ReportDate"] = report_date.strftime(date_format)

	report_data.get_final_balances()

	



	columns = dict()
	columns["this_month"] = report_month
	columns["last_month"] = DateFunctions.date_add_months(report_month, -1)
	columns["two_months_ago"] = DateFunctions.date_add_months(report_month, -2)
	columns["three_months_ago"] = DateFunctions.date_add_months(report_month, -3)
	columns["six_months_ago"] = DateFunctions.date_add_months(report_month, -6)
	columns["one_year_ago"] = DateFunctions.date_add_months(report_month, -12)
	columns["two_years_ago"] = DateFunctions.date_add_months(report_month, -24)

	# column titles	
	
	column_titles = dict()
	for key in columns.keys():
		column_titles[key] = columns[key].strftime(time_format)
	
	data["column_titles"] = column_titles
	
	# asset accounts and subtotal
	
	all_asset_accounts_filter = _create_filter_account_name_starts_with("Assets")
	not_unit_asset_accounts_filter = _create_filter_not_a(_create_filter_account_name_contains("Units"))
	asset_account_filter = _create_filter_a_and_b(all_asset_accounts_filter, not_unit_asset_accounts_filter)
	data["asset_accounts"] = _get_balance_to_month_by_account(report_data, columns, asset_account_filter)
	data["asset_subtotal"] = _get_aggregate_balance_to_month(report_data, columns, asset_account_filter)

	# liability accounts and subtotal

	liability_account_filter = _create_filter_account_name_starts_with("Liabilities")
	data["liability_accounts"] = _get_balance_to_month_by_account(report_data, columns, liability_account_filter)
	data["liability_subtotal"] = _get_aggregate_balance_to_month(report_data, columns, liability_account_filter)

	# grand total

	grand_total_account_filter = _create_filter_a_or_b(asset_account_filter, liability_account_filter)
	data["grand_total"] = _get_aggregate_balance_to_month(report_data, columns, grand_total_account_filter)
	
	return data


def _get_balance_to_month_by_account(report_data, columns, account_filter):
	"""
	Returns a list of monthly balances for the columns in columns for
	each account determined by account_filter.
	"""
	# get balances data
	monthly_balances = dict()
	for columnkey in columns.keys():
		monthly_balances[columnkey] = report_data.get_balances_to_end_of_month(columns[columnkey])

	# get list of accounts
	accounts = [account for account in report_data.get_account_list(False) if account_filter(account)]
	accounts.sort()

	# generate row data
	rows = list()
	row_count = 0
	for account in accounts:
		row = dict()

		if row_count % 2 == 0:
			row["row_class"] = "even"
		else:
			row["row_class"] = "odd"

		row_count = row_count + 1

		row["account_name"] = _remove_top_account_name(account)

		for columnkey in columns.keys():
			balances = monthly_balances[columnkey]

			if account in balances:
				row[columnkey] = _print_amounts(balances[account])
			else:
				row[columnkey] = "&nbsp;"

		rows.append(row)

	return rows


def _get_aggregate_balance_to_month(report_data, columns, account_filter):
	"""
	Writes aggregated monthly totals for the columns in columns and the total
	aggregate balance for the accounts determined by account_filter.
	"""
	# get balances data
	monthly_balances = dict()
	for columnkey in columns.keys():
		monthly_balances[columnkey] = report_data.get_balances_to_end_of_month(columns[columnkey])

	# get list of accounts
	accounts = [account for account in report_data.get_account_list(False) if account_filter(account)]

	row = dict()
	for columnkey in columns.keys():
		aggregate_total = dict()
		for account in accounts:
			balances = monthly_balances[columnkey]

			if account in balances:
				LedgerData.add_amounts_to_dictionary(aggregate_total, balances[account])

		row[columnkey] = _print_amounts(aggregate_total)
	
	return row
