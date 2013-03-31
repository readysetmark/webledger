"""
Contains the journal data classes:
	Header - an entry header
	Entry - a transaction entry
	Journal - list of all transactions and ways to access the data
"""

import string
import datetime

#========================================================
#	Structs
#========================================================

class Header:
	"""
	A ledger transaction entry header (can be common for multiple entries)
	"""

	def __init__(self, date, status, code, description, note):
		self.date = date
		self.status = status
		self.code = code
		self.description = description
		self.note = note

	def to_string(self):
		s = "(" + self.date.strftime("%Y/%m/%d") + ", "
		s += (self.status if self.status != None else "None") + ", "
		s += (self.code if self.code != None else "None") + ", "
		s += self.description + ", "
		s += (self.note if self.note != None else "None") + ")"
		return s


class Entry:
	"""
	A ledger transaction entry
		- entry_type is one of no/balanced/unbalanced (TODO: fix values -- this field used to be called "virtual")
		- amount and value are both tuples of (amount, commodity)
	"""

	def __init__(self, header, account, entry_type, amount, value, note):
		self.header = header
		self.account = account
		self.account_lineage = self.get_account_lineage()
		self.entry_type = entry_type
		self.amount = amount
		self.value = value
		self.note = note


	def to_string(self):
		s = "(" + self.header.to_string() + ", "
		s += self.account + ", "
		s += self.entry_type + ", "
		s += "(" + ("%.2f" % self.amount[0]) + ", "
		s += (self.amount[1] if self.amount[1] != None else "None") + "), "
		if self.value != None:
			s += "(" + (("%.2f" % self.value[0]) if self.value[0] != None else "None") + ", "
			s += (self.value[1] if self.value[1] != None else "None") + "), "
		else:
			s += "None, "
		s += (self.note if self.note != None else "None") + ")"
		return s


	def get_account_lineage(self):
		"""
		Returns a list with the account and all parent accounts
		"""
		lineage = list()
		parts = self.account.split(":")

		while len(parts) > 0:
			lineage.append(string.join(parts, ":"))
			parts.pop()

		return lineage



#========================================================
#	Journal
#========================================================

class Journal:
	"""
	Journal class:
		- entries: list of all entries in the ledger file
		- main_accounts: list of all accounts that have amounts
		- all_accounts: list of all accounts, including parent accounts

		- provides different views of that data
	"""

	def __init__(self, entry_list):
		self.entries = entry_list
		self.main_accounts = set()
		self.all_accounts = set()

		for entry in self.entries:
			if entry.account not in self.main_accounts:
				self.main_accounts.add(entry.account)

			for account in entry.account_lineage:
				if account not in self.all_accounts:
					self.all_accounts.add(account)

		#self.__monthly_totals = None
		#self.__final_balances = None
		#self.__monthly_balances = dict()


	def to_string(self):
		s = ""
		for entry in self.entries:
			s += entry.to_string() + "\n"
		return s


#-------------------------------------------------------------------
#  ledgertree_to_journal
#-------------------------------------------------------------------

def ledgertree_to_journal(ledgertree_root):
	entries = []

	for entry_node in ledgertree_root.children:
		header = Header(
			date=entry_node.date,
			status=entry_node.cleared,
			code=entry_node.code,
			description=entry_node.description,
			note=None
		)

		for transaction_node in entry_node.children:
			entry = Entry(
				header=header,
				account=transaction_node.account,
				entry_type=transaction_node.entry_type,
				amount=(transaction_node.amount, transaction_node.amountCommodity),
				value=
					(transaction_node.value, transaction_node.valueCommodity)
					if transaction_node.value != None 
						or transaction_node.valueCommodity != None 
					else None,
				note=transaction_node.note
			)

			entries.append(entry)

	return Journal(entries)
