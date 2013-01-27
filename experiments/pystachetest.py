import pystache


if __name__ == "__main__":
	template = open("templates\\IncomeStatement.html").read()

	data = {"column_titles": {"this_month": "Apr 2012", "last_month": "Mar 2012", "two_months_ago": "Feb 2012", "three_months_ago": "Jan 2012", "six_months_ago": "Oct 2011", "one_year_ago": "Apr 2011", "two_years_ago": "Apr 2010", "total": "Total"}}
	html = pystache.render(template, data)
	print "%s" % html
