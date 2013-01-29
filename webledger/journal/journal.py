"""
Contains the journal data classes:
	Header - an entry header
	Entry - a transaction entry
	Journal - list of all transactions and ways to access the data
"""

import string
import datetime
#import webledger.util.datetime as udt

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
		- entry_type is one of no/balanced/unbalanced (TODO: fix values)
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
#		Utility Functions
#========================================================

def add_amounts_to_dictionary(target_dict, amounts_dict):
	"""
	Adds the commodities and amounts in amounts_dict to target_dict.
	"""
	for commodity, amount in amounts_dict.items():
		if commodity in target_dict:
			target_dict[commodity] += amount
		else:
			target_dict[commodity] = amount


#========================================================
#	LedgerData
#========================================================

class LedgerData:
	"""
	LedgerData class:
	- stores transaction data from the ledger file
	- provides different views of that data
	"""

	def __init__(self, transaction_list):
		self.__transaction_list = transaction_list
		self.__main_accounts = None
		self.__all_accounts = None
		self.__monthly_totals = None
		self.__final_balances = None
		self.__monthly_balances = dict()


	def get_account_list(self, include_parent_accounts):
		"""
		Returns a list of the accounts in the ledger file, with the option of
		including parent accounts.
		"""
		if self.__main_accounts == None:
			self.__main_accounts = set()
			self.__all_accounts = set()

			for transaction in self.__transaction_list:
				if transaction.account not in self.__main_accounts:
					self.__main_accounts.add(transaction.account)

				for account in transaction.account_lineage:
					if account not in self.__all_accounts:
						self.__all_accounts.add(account)

		if include_parent_accounts:
			return self.__all_accounts
		else:
			return self.__main_accounts


	def get_monthly_totals(self):
		"""
		Returns a dictionary of {(account, month): {commodity: amount}} containing
		the sum of transaction amounts per month for each account.
		"""
		if self.__monthly_totals == None:
			self.__monthly_totals = dict()
			
			for transaction in self.__transaction_list:
				transaction_month = dt.date(year=transaction.date.year, month=transaction.date.month, day=1)

				for account in transaction.account_lineage:
					key = (account, transaction_month)

					if key in self.__monthly_totals:
						amounts = self.__monthly_totals[key]
						if transaction.amount_commodity in amounts:
							amounts[transaction.amount_commodity] += transaction.amount
						else:
							amounts[transaction.amount_commodity] = transaction.amount
					else:
						amounts = dict()
						amounts[transaction.amount_commodity] = transaction.amount
						self.__monthly_totals[key] = amounts

		return self.__monthly_totals


	def get_final_balances(self):
		"""
		Returns a dictionary of {account: {commodity: amount}} containing the
		sum of all transaction amounts for each account.
		"""
		if self.__final_balances == None:
			self.__final_balances = dict()
			
			for transaction in self.__transaction_list:
				for account in transaction.account_lineage:
					if account in self.__final_balances:
						amounts = self.__final_balances[account]
						if transaction.amount_commodity in amounts:
							amounts[transaction.amount_commodity] += transaction.amount
						else:
							amounts[transaction.amount_commodity] = transaction.amount
					else:
						amounts = dict()
						amounts[transaction.amount_commodity] = transaction.amount
						self.__final_balances[account] = amounts

		return self.__final_balances



	def get_balances_to_end_of_month(self, month):
		"""
		Returns a dictionary of {account: {commodity: amount}} containing the
		sum of all transaction amounts for each account up to the end of the
		specified month.
		"""
		if month in self.__monthly_balances:
			return self.__monthly_balances[month]
		else:
			balances = dict()
			monthly_totals = self.get_monthly_totals()
			
			for key_account, key_month in monthly_totals.keys():
				key = (key_account, key_month)
				if key_month <= month:
					if key_account in balances:
						amounts = balances[key_account]
						add_amounts_to_dictionary(amounts, monthly_totals[key])
					else:
						amounts = dict()
						add_amounts_to_dictionary(amounts, monthly_totals[key])
						balances[key_account] = amounts

			self.__monthly_balances[month] = balances

			return balances



#-------------------------------------------------------------------
#  ledgertree_to_journal
#-------------------------------------------------------------------

def ledgertree_to_journal(ledgertree_root):
	journal = []

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

			journal.append(entry)

	return journal
