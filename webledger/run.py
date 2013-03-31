import os
import time
import datetime
import calendar

from flask import Flask, render_template, request, url_for

import webledger.parser.ledgertree as ledgertree
import webledger.journal.journal as j
import webledger.report.balance as balance


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

		page = {
			"data": data,
			"navlist": get_navlist()
		}
		result = render_template("balance.html", page=page, command=command, path="/")
	elif cmd_parts[0] == "register":
		parameters = balance.BalanceReportParameters.from_command(cmd_parts[1:])
		data = balance.generate_register_report(journal, parameters)

		page = {
			"data": data,
			"navlist": get_navlist()
		}
		result = render_template("register.html", page=page, command=command, path="/")

	return result


@app.route("/networth")
def networth():
	two_years_ago = date_add_months(datetime.date.today(), -24)
	two_years_ago = datetime.date(
		year=two_years_ago.year,
		month=two_years_ago.month,
		day=calendar.monthrange(two_years_ago.year, two_years_ago.month)[0])
	parameters = balance.MonthlySummaryParameters(
		title="Net Worth",
		accounts_with=["assets","liabilities"],
		exclude_accounts_with=["units"],
		period_start=two_years_ago,
		period_end=None)
	data = balance.generate_monthly_summary(journal, parameters)

	page = {
		"data": data,
		"navlist": get_navlist()
	}
	return render_template("linechart.html", page=page, command=None, path="networth")



################################################
# Utilities

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



def get_navlist():
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
