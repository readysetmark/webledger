Webledger v0.0.5
================

[2013/01/27] Most of this is old and needs to be revised....

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
*	Pystache v0.5.0



Implementation Notes
--------------------

Investments & Commodities:
*	I'm basically ignoring these for the moment. The parser will parse them,
but all processing after that point assumes one commodity and basically assumes
only the "amount" field is used. I'll need to revisit this once I got around
to adding investment/commodity support.



Phase 1 Implementation (Reporting)
----------------------------------

### Objective

Generate a fixed number of parameterized HTML reports from the ledger file.

### TODO

-	Net worth chart using d3.js
	[] combine onto balance sheet


### Main Tasks

Parsing Ledger File
+ Define ledger record types
+ Parse ledger file and build records
	- (While continuing to use ledger file format) Detect investment transactions and merge transaction lines
+ Ensure transactions balance

Commodity Prices
- Identify commodities from ledger file
- Store commodity prices in a local cache
- Fetch prices from internet and add to cache
	- Prices should go from first date in ledger file to today

Rendering HTML Tables and Charts
- This is where I need to do some experimentation and find a good HTML 
templating engine
- tables for tabular data
- plot charts using...? gnuplot? jqplot? flot?
- using jquery datatables and jqplot?
- twitter bootstrap?

Reporting
- (see http://bugsplat.info/static/stan-demo-report.html for some examples)
- Balance Sheet -- assets vs liabilities [table] this is basically net worth (if summed) -- should be over time
- Income statement (Income vs Expenses)
	Do I want to have parent levels (i.e. Expenses:Food)? 
	Eg:
							2 Years Ago, 1 Year Ago, 3 Months Ago, 2 Months Ago, Last Month, This Month, Total
		Income
			*
			Total
		Expense
			*
			Total
		Net Income
- Expenses over $100 this month/last month
- Expenses average in last 3 months, in last year
- Burn rate: using 3 month average, how many months before savings is gone?
- Expenses vs budget (will need to be defined elsewhere?)
- Savings projections?
- Investments		
- Overall Portfolio Return (see NotesOnInvestments.txt)
- Rebalance spreadsheet (for rebalancing investments to proper allocation)
- Expected T3s/T5s
	


Phase 2 Ideas (Query)
-------------

- Replace bal and reg functions from ledger command line
- Move away from ledger file format
	- Define my own that handles investments better


Phase 3 Ideas (Entry)
-------------

- Entry/editing of transactions