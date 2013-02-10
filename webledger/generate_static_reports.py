"""
Generate all static reports
"""

#fragment start *
import os
import time
import datetime
import calendar
import pystache
import webledger.parser.ledgertree as ledgertree
import webledger.journal.journal as j
import webledger.report.balance as balance


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



def generate_report(template_path, output_path, data):
	tf = open(template_path)
	template = tf.read()
	tf.close()

	f = open(output_path, "w")
	f.write(pystache.render(template, data))
	f.close()

	print "Generated %s" % (output_path)


def generate_static_reports(journal_data):
	t1 = time.time()
	index_links = list()
	
	# Balance Sheet
	parameters = balance.BalanceReportParameters(
		title="Balance Sheet",
		accounts_with=["assets","liabilities"],
		exclude_accounts_with=["units"],
		period_start=None,
		period_end=None)
	data = balance.generate_balance_report(journal, parameters)
	generate_report("templates\\BalanceReport.html", "output\\BalanceSheet.html", data)
	link = dict()
	link["url"] = "BalanceSheet.html"
	link["title"] = "Balance Sheet"
	index_links.append(link)


	# Income Statement - Current Month
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
	generate_report("templates\\BalanceReport.html", "output\\IncomeStatement-CurrentMonth.html", data)
	link = dict()
	link["url"] = "IncomeStatement-CurrentMonth.html"
	link["title"] = "Income Statement - Current Month"
	index_links.append(link)

	# Income Statement - Previous Month
	two_years_ago = date_add_months(today, -24)
	two_years_ago = datetime.date(
		year=two_years_ago.year,
		month=two_years_ago.month,
		day=calendar.monthrange(two_years_ago.year, two_years_ago.month)[0])
	parameters = balance.MonthlySummaryParameters(
		#title="Income Statement",
		accounts_with=["assets","liabilities"],
		exclude_accounts_with=["units"],
		period_start=two_years_ago,
		period_end=None)
	data = balance.generate_monthly_summary(journal, parameters)
	generate_report("templates\\LineChart.html", "output\\NetWorth.html", data)
	link = dict()
	link["url"] = "NetWorth.html"
	link["title"] = "Net Worth"
	index_links.append(link)

	# Net Worth Chart


	# Index page
	data = dict()
	data["index_links"] = index_links
	generate_report("templates\\Index.html", "output\\Index.html", data)

	t2 = time.time()
	print "Took %0.3f ms" % ((t2-t1)*1000.0)


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
	source_filename = os.getenv("LEDGER_FILE", "input\\ledger.dat")
	
	print "Generating reports against %s." % source_filename

	journal = read_journal_data(source_filename)
	generate_static_reports(journal)
