import os
import time
import datetime
import calendar

from flask import Flask, render_template

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
def balancesheet():
	parameters = balance.BalanceReportParameters(
		title="Balance Sheet",
		accounts_with=["assets","liabilities"],
		exclude_accounts_with=["units"],
		period_start=None,
		period_end=None)
	data = balance.generate_balance_report(journal, parameters)

	page = {
		"title": "Balance Sheet",
		"data": data,
		"navlist": get_navlist()
	}
	return render_template("balance.html", page=page)


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
		"title": "Net Worth",
		"data": data,
		"navlist": get_navlist()
	}
	return render_template("linechart.html", page=page)


@app.route("/currentincomestatement")
def currentincomestatement():
	today = datetime.date.today()
	parameters = balance.BalanceReportParameters(
		title="Income Statement",
		accounts_with=["income","expenses"],
		exclude_accounts_with=None,
		period_start=datetime.date(year=today.year,
			month=today.month,
			day=1),
		period_end=datetime.date(year=today.year,
			month=today.month,
			day=calendar.monthrange(today.year, today.month)[1]))
	data = balance.generate_balance_report(journal, parameters)

	page = {
		"title": "Income Statement - Current Month", 
		"data": data,
		"navlist": get_navlist()
	}
	return render_template("balance.html", page=page)


@app.route("/previousincomestatement")
def previousincomestatement():
	today = datetime.date.today()
	month_ago = date_add_months(today, -1)
	parameters = balance.BalanceReportParameters(
		title="Income Statement",
		accounts_with=["income","expenses"],
		exclude_accounts_with=None,
		period_start=datetime.date(year=month_ago.year,
			month=month_ago.month,
			day=1),
		period_end=datetime.date(year=month_ago.year,
			month=month_ago.month,
			day=calendar.monthrange(month_ago.year, month_ago.month)[1]))
	data = balance.generate_balance_report(journal, parameters)

	page = {
		"title": "Income Statement - Previous Month",
		"data": data,
		"navlist": get_navlist()
	}

	return render_template("balance.html", page=page)



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

	return datetime.date(year=year, month=month, day=day)



def get_navlist():
	"""
	Get list of reports to include in the navigation list
	"""
	return [
		{
			"path": "balancesheet",
			"title": "Balance Sheet"
		},
		{
			"path": "networth",
			"title": "Net Worth"
		},
		{
			"path": "currentincomestatement",
			"title": "Income Statement - Current Month"
		},
		{
			"path": "previousincomestatement",
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
