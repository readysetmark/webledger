Webledger v0.1
==============

Objective
---------

Long-term, the idea is to replace the command line ledger with my own tool that
does all reporting via a web interface. Editing will still be done by text file,
though in the long-long term, perhaps a front end for adding/editing 
transactions would be a possibility.

Medium-term, I may deviate from the ledger file format to my own file format,
so that I can handle investments better.

Short-term, the focus is on what ledger cannot do right now: tables and charts.


Implementation Details
----------------------

Parsing portion is largely based on the tutorial by Stephen Ferg available at
[http://parsingintro.sourceforge.net/](http://parsingintro.sourceforge.net/ 
"Notes on How Parsers and Compilers Work").

Dependencies:

*	Python v2.7.3
*	Virtualenv v1.8.4
*	Flask v0.9


Project Setup
-------------

Make sure virtualenv is installed using pip:

	pip install virtualenv

Within the project folder, create a new virtual environment:

	virtualenv venv

Activate the virtual environment:

	venv\scripts\activate

Install flask:

	pip install flask


How to Run
----------

*	Setup LEDGER_FILE environment variable
*	Run: venv\scripts\activate
*	Run: python webledger\run.py


Implementation Notes
--------------------

Investments & Commodities:
*	I'm basically ignoring these for the moment. The parser will parse them,
but all processing after that point assumes one commodity and basically assumes
only the "amount" field is used. I'll need to revisit this once I got around
to adding investment/commodity support.



Phase 1 Implementation (Reporting)
----------------------

### Objective

*	Replace the ledger bal and reg commandline options with a web interface.
*	Provide some basic reporting like net worth, income vs expenses, ...
*	See http://bugsplat.info/static/stan-demo-report.html for some examples

### Main Tasks

Parsing Ledger File
[x] Read/Parse ledger file
[x] Autobalance transactions
[x] Ensure transactions balance

Initial Static Balance Reports:
[x] Assets vs Liabilities, ie Net Worth
[x] Income Statement (current & previous month)
[x] Net Worth chart

Dynamic Website:
[] Convert all existing reports to render dynamically instead of a static page
	[x] Get barebones flask working
	[x] map /, /balancesheet, /currentincomestatement, /previousincomestatement to current pages
	[x] fix html/css (use proper elements ie h1, ul, etc...)
	[x] start using bootstrap css
	[x] turn into "one page" app that takes GET parameters for what to show (with command bar)
	[] watch ledger file and reload on change
		will come back to this. look at watchdog library. need to understand python threading and flask environment better to do it.

Register Report
[x] Register report with parameters (ie accounts, date range)
	[x] build register report generator function
	[x] create register report template
	[x] link up to command bar
	[x] link to from balance reports
[x] Sorting:
	[x] Preserve file order for transactions and entries within transactions but output in reverse so most recent is on top
		- Need to do sorting at the end so that running total makes sense
[x] Accounts Payable vs Accounts Receivable

All Reports
[] Refactoring/clean up of all reports

Command Bar Enhancements
[] Clean up and improve date/period parsing
	Additions for period: yyyy, last year, this year
[] Generate "networth" chart from the command bar
[] Autocomplete hints

Charts
[x] Fix broken Net Worth chart (broke with large amount)
[] Income Statement chart (monthly, over time)

Nav
[] Configurable nav list
[] Combine reports and payables / receivables into one dict?
[] Default report?

Expenses
[] Average in last 3 months, in last year
[] Burn rate - using last 3 months expenses average, how long until savings is gone?
[] Top Expenses over last period

Documentation
[] github wiki
	[] how to use / setup


Phase 2 Implementation (Commodities)
----------------------

Commodity Prices
[] (While continuing to use ledger file format) Detect investment transactions and merge transaction lines
[] Identify commodities from ledger file
[] Fetch prices from internet and add to cache
	[] Store commodity prices in a local cache
	[] Prices should go from first date in ledger file to today

Net Worth
[] Update chart with book value line and actual line

Balance Sheet
[] Update Net Worth sheet with actual vs book value columns

Portfolio
[] Overall portfolio return and per investment
[] Expected T3s/T5s to receive for last year (ie had distribution)
[] Rebalancing calculator - for rebalancing investments to proper allocation



Phase 3 Ideas (Entry)
-------------

- Replace bal and reg functions from ledger command line
- Move away from ledger file format
	- Define my own that handles investments better
- Entry/editing of transactions