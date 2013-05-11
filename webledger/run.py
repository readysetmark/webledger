import os
import time
import datetime
import calendar

from flask import Flask, render_template, request, url_for

import webledger.parser.ledgertree as ledgertree
import webledger.journal.journal as j
import webledger.report.balance as balance
import webledger.utilities.utilities as utilities


################################################
# Flask App

app = Flask(__name__)
app.debug = True



################################################
# Routes

@app.route("/")
def command():
	"""
	Generate a report based on cmd query parameter.
	"""
	command = request.args.get("cmd", "")
	result = "Unknown command: " + command

	if len(command) == 0:
		# default command for now
		command = "balance assets liabilities :excluding units :title Balance Sheet"

	cmd_parts = command.split(" ")

	if cmd_parts[0] == "balance":
		parameters = balance.BalanceReportParameters.from_command(cmd_parts[1:])
		data = balance.generate_balance_report(journal, parameters)

		page = get_page_data(data)
		result = render_template("balance.html", page=page, command=command, path="/")
	elif cmd_parts[0] == "register":
		parameters = balance.BalanceReportParameters.from_command(cmd_parts[1:])
		data = balance.generate_register_report(journal, parameters)

		page = get_page_data(data)
		result = render_template("register.html", page=page, command=command, path="/")

	return result


@app.route("/networth")
def networth():
	two_years_ago = utilities.date_add_months(datetime.date.today(), -24)
	two_years_ago = datetime.date(
		year=two_years_ago.year,
		month=two_years_ago.month,
		day=1)
	parameters = balance.MonthlySummaryParameters(
		title="Net Worth",
		accounts_with=["assets","liabilities"],
		exclude_accounts_with=["units"],
		period_start=two_years_ago,
		period_end=None)
	data = balance.generate_monthly_summary(journal, parameters)

	page = get_page_data(data)
	return render_template("linechart.html", page=page, command=None, path="networth")



################################################
# Utilities

def get_page_data(data):
	"""
	Returns a dictionary of data to be rendered by the page. The "data" parameter is
	data specific for the current page being rendered. Standard data for all pages will
	be generated/fetched here.
	"""
	return {
		"data": data,
		"reports": get_reports(),
		"payables_receivables": get_payables_receivables()
	}


def get_reports():
	"""
	Get list of reports to include in the navigation list
	"""
	return [
		{
			"command": "balance assets liabilities :excluding units :title Balance Sheet",
			"title": "Balance Sheet"
		},
		{
			"path": "networth",
			"title": "Net Worth"
		},
		{
			"command": "balance income expenses :period this month :title Income Statement",
			"title": "Income Statement - Current Month"
		},
		{
			"command": "balance income expenses :period last month :title Income Statement",
			"title": "Income Statement - Previous Month"
		}
	]


def get_payables_receivables():
	"""
	Get a list of accounts payable and receivable with balances
	"""
	pr_accounts = list()

	for account in sorted(journal.payables_and_receivables_accounts.keys()):
		command = "register assets:receivables:" + account + " liabilities:payables:" + account
		pr_accounts.append(
			{
				"title": account,
				"command": command
			}
		)

	return pr_accounts


################################################
# Main + Setup

def read_journal_data(source_filename):
	"""
	Read in and return the journal data
	"""
	t1 = time.time()
	tree = ledgertree.parse_into_ledgertree(source_filename)
	journal = j.ledgertree_to_journal(tree)
	t2 = time.time()

	print "Parsed ledger file in %0.3f ms" % ((t2-t1)*1000.0)

	return journal



if __name__ == "__main__":
	#source_filename = "input\\test.dat"
	#source_filename = "input\\ledger.dat"
	source_filename = os.getenv("LEDGER_FILE", "")
	
	if source_filename == "":
		print "Could not find path to ledger file in LEDGER_FILE enviornment variable."
	else:
		journal = read_journal_data(source_filename)
		
		app.run()
