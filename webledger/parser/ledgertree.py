"""
Ledger Tree
- convert a ledger parser AST into a ledger tree
- output ledger tree to text
- export ledger data to sqlite db
"""
import datetime
import ledgerParser as parser
from decimal import *
from ledgerNodeTypes import *
from ledgerSymbols import *


#========================================================
#		Ledger Tree
#========================================================

class LedgerNode:
	def __init__(self, nodeType, parent=None):
		self.level = 0 if parent == None else parent.level + 1
		self.type = nodeType
		self.date = None
		self.cleared = None
		self.description = None
		self.code = None
		self.account = None
		self.virtual = None
		self.amount = None
		self.amountCommodity = None
		self.value = None
		self.valueCommodity = None
		self.note = None
		self.parent = parent
		self.children = []  # a list of my children

		if parent != None:
			parent.children.append(self)

	def toString(self):
		s = "    " * self.level
		s += self.type + ":\n"

		if self.type == ENTRY:
			s += ("    " * (self.level+1)) + "Date:        " + datetime.date.strftime(self.date, "%Y/%m/%d") + "\n"
			s += ("    " * (self.level+1)) + "Cleared:     " + self.cleared + "\n"
			if self.code != None: 
				s += ("    " * (self.level+1)) + "Code:        " + self.code + "\n"
			s += ("    " * (self.level+1)) + "Description: " + self.description + "\n"
		elif self.type == TRANSACTION:
			s += ("    " * (self.level+1)) + "Account: " + self.account + "\n"
			s += ("    " * (self.level+1)) + "Virtual: " + self.virtual + "\n"
			if self.amount != None:
				s += ("    " * (self.level+1)) + "Amount:  " + ("%.2f" % self.amount) + " " + self.amountCommodity + "\n"
			if self.value != None:
				s += ("    " * (self.level+1)) + "Value:   " + ("%.2f" % self.value) + " " + self.valueCommodity + "\n"
			if self.note != None:
				s += ("    " * (self.level+1)) + "Note:    " + self.note + "\n"
			
		for child in self.children:
			s += child.toString()
		return s
		


def parse_into_ledgertree(filename):
	"""
	Uses ledgerParser to parse a ledger file into a ledgertree
	"""
	sourcetext = open(filename).read()
	generic_ast = parser.parse(sourcetext, verbose=False)
	ledgertree = build_ledgertree(generic_ast)
	autoBalanceLedgerTree(ledgertree)

	# removing this as it is buggy (see Trello task)
	#mergeInvestmentEntries(ledgertree)

	return ledgertree



def build_ledgertree(node):
	"""
	Convert the generic AST into a ledger tree
	"""
	root = LedgerNode(LEDGER)

	if node.type == LEDGER:
		for child in node.children:
			if child.type == ENTRY:
				generateEntryNode(root, child)
			elif child.type != NOTE:
				error("I was expecting to find an ENTRY token but I found: "+ child.type)
			
	
	return root


def generateEntryNode(ledgerNode, astNode):
	"""
	Process current astNode and create an ENTRY LedgerNode from it
	"""
	entryNode = LedgerNode(ENTRY, ledgerNode)
	entryNode.cleared = "uncleared"
	
	for child in astNode.children:
		if child.type == DATE:
			entryNode.date = getDate(child)
		elif child.type == CODE:
			entryNode.code = getString(child)
		elif child.type == DESCRIPTION:
			entryNode.description = getString(child)
		elif child.type == TRANSACTION:
			generateTransactionNode(entryNode, child)
		elif child.type == "*":
			entryNode.cleared = "cleared"
		elif child.type == "!":
			entryNode.cleared = "pending"
		else:
			error("Unexpected node type under ENTRY: "+ child.type)


def getDate(astNode):
	"""
	Get the date from a date node
	"""
	s = ""
	
	for child in astNode.children:
		s += child.token.cargo
	
	date = datetime.datetime.strptime(s, "%Y/%m/%d").date()

	return date


def getString(astNode):
	"""
	Get the string from a string node
	"""
	s = ""

	for child in astNode.children:
		s += child.token.cargo
	
	return s.strip()


def generateTransactionNode(entryNode, astNode):
	"""
	Process current astNode and create a TRANSACTION LedgerNode from it
	"""
	transactionNode = LedgerNode(TRANSACTION, entryNode)
	
	for child in astNode.children:
		if child.type == ACCOUNT:
			transactionNode.account = getString(child)

			transactionNode.virtual = "no"

			if transactionNode.account[0] == "(":
				transactionNode.virtual = "unbalanced"
				transactionNode.account = transactionNode.account.strip("()")
			elif transactionNode.account[0] == "[":
				transactionNode.virtual = "balanced"
				transactionNode.account = transactionNode.account.strip("[]")
		elif child.type == AMOUNT:
			transactionNode.amount = getAmount(child)
			transactionNode.amountCommodity = getAmountCommodity(child)
		elif child.type == VALUE:
			if child.children[0].type == "@":
				transactionNode.value = transactionNode.amount * getAmount(child.children[1])
				transactionNode.valueCommodity = getAmountCommodity(child.children[1])
			else:
				transactionNode.value = getAmount(child.children[1])
				transactionNode.valueCommodity = getAmountCommodity(child.children[1])
		elif child.type == NOTE:
			transactionNode.note = child.token.cargo
		else:
			error("Unexpected node type under TRANSACTION: "+ child.type)


def getAmount(astAmountNode):
	"""
	Get the amount out of an astAmountNode
	"""
	amountIndex = 0
	
	if astAmountNode.children[0].type == COMMODITY:
		amountIndex = 1
	
	return Decimal(astAmountNode.children[amountIndex].token.cargo.replace(",", ""))


def getAmountCommodity(astAmountNode):
	"""
	Get the amount commodity out of an astAmountNode
	"""
	commodity = None

	if len(astAmountNode.children) > 1:
		commodityIndex = 1
	
		if astAmountNode.children[0].type == COMMODITY:
			commodityIndex = 0
		
		commodity = getString(astAmountNode.children[commodityIndex])
		commodity.strip('"')
	
	return commodity


#-------------------------------------------------------------------
#  autoBalanceLedgerTree
#-------------------------------------------------------------------

def autoBalanceLedgerTree(root):
	"""
	Auto balance ledger entries where a transaction amount is missing
	"""
	for entryNode in root.children:
		amount = Decimal(0)
		commodity = ""
		count = -1
		updateNode = -1
		for transactionNode in entryNode.children:
			count += 1
			if transactionNode.value != None:
				amount += transactionNode.value
				if commodity == "": commodity = transactionNode.valueCommodity
			elif transactionNode.amount != None:
				amount += transactionNode.amount
				if commodity == "": commodity = transactionNode.amountCommodity
			else:
				updateNode = count
		
		if updateNode != -1 and amount != 0:
			entryNode.children[updateNode].amount = -1 * amount
			entryNode.children[updateNode].amountCommodity = commodity


#-------------------------------------------------------------------
#  mergeInvestmentEntries
#-------------------------------------------------------------------

def mergeInvestmentEntries(root):
	"""
	This is 'fixing' the way I chose to track investments in separate
	BookValue and Units accounts. This will merge the two entries
	into one containing both the units and value.
	"""
	for entryNode in root.children:
		investmentsDict = {}
		removeNodeList = []
		count = -1

		for transactionNode in entryNode.children:
			count += 1

			if transactionNode.virtual == "unbalanced" and transactionNode.account.find("Assets") >= 0 and transactionNode.account.find("Units") > 0 :
				investmentsDict[transactionNode.account] = count
		
		for key in investmentsDict.keys():
			bookValueAccount = key.replace("Units", "BookValue")
			bookValueIndex = -1
			count = 0

			while bookValueIndex < 0 and count < len(entryNode.children):
				if entryNode.children[count].account == bookValueAccount:
					bookValueIndex = count
				count += 1
			
			if bookValueIndex >= 0:
				bookValueNode = entryNode.children[bookValueIndex]
				unitsNode = entryNode.children[investmentsDict[key]]

				bookValueNode.value = unitsNode.amount
				bookValueNode.valueCommodity = unitsNode.amountCommodity

				bookValueNode.account = bookValueNode.account.replace("BookValue:", "")
				removeNodeList.append(unitsNode)
			else:
				raise Exception("Could not find matching investment entries for: \r\n"
						+ "Units Account: " + key + "\r\n"
						+ "BookValue Account: " + bookValueAccount + "\r\n"
						+ "Transaction: "	+ datetime.strftime(entryNode.date, "%Y-%m-%d")	+ " "	+ entryNode.description
					)
		
		for node in removeNodeList:
			entryNode.children.remove(node)
