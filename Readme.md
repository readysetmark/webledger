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

*	Python v2.7.2
*	Virtualenv v1.8.4
*	Flask v0.9
*	Pystache v0.5.0 [to be removed]


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
	[] map /networth, /currentincomestatement, /previousincomestatement to current pages
	[] make a /balance that takes parameters to do the above three pages
	[] what to do with chart...?

Register Report
[] Register report with parameters (ie accounts, date range)
[] Accounts Payable vs Accounts Receivable

Charts
[] Income Statement chart (monthly, over time)

Expenses
[] Average in last 3 months, in last year
[] Burn rate - using last 3 months expenses average, how long until savings is gone?
[] Top Expenses over last period



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