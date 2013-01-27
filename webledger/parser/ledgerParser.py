#fragment start *
"""
A recursive descent parser for ledger files
"""
import ledgerLexer as lexer
from   ledgerSymbols import *
from   genericToken import *
from   genericAstNode import Node
from   ledgerNodeTypes import *

class ParserError(Exception): pass

def dq(s): return '"%s"' %s

token   = None
verbose = False
indent  = 0
numberOperator = ["+","-","/","*"]


#-------------------------------------------------------------------
#		 getToken
#-------------------------------------------------------------------
def getToken():
	global token 
	if verbose: 
		if token: 
			# print the current token, before we get the next one
			#print (" "*40 ) + token.show() 
			print(("  "*indent) + "   (" + token.show(align=False) + ")")
	token  = lexer.get()

#-------------------------------------------------------------------
#    push and pop
#-------------------------------------------------------------------
def push(s):
	global indent
	indent += 1
	if verbose: print(("  "*indent) + " " + s)

def pop(s):
	global indent
	if verbose: 
		#print(("  "*indent) + " " + s + ".end")
		pass
	indent -= 1

#-------------------------------------------------------------------
#  decorator track0
#-------------------------------------------------------------------
def track0(func):
	def newfunc():
		push(func.__name__)
		func()
		pop(func.__name__)
	return newfunc

#-------------------------------------------------------------------
#  decorator track
#-------------------------------------------------------------------
def track(func):
	def newfunc(node):
		push(func.__name__)
		func(node)
		pop(func.__name__)
	return newfunc

#-------------------------------------------------------------------
#
#-------------------------------------------------------------------
def error(msg):
	token.abort(msg)


#-------------------------------------------------------------------
#        foundOneOf
#-------------------------------------------------------------------
def foundOneOf(argTokenTypes):
	"""
	argTokenTypes should be a list of argTokenType
	"""
	for argTokenType in argTokenTypes:
		#print "foundOneOf", argTokenType, token.type
		if token.type == argTokenType:
			return True
	return False


#-------------------------------------------------------------------
#        found
#-------------------------------------------------------------------
def found(argTokenType):
	if token.type == argTokenType:
		return True
	return False

#-------------------------------------------------------------------
#       consume
#-------------------------------------------------------------------
def consume(argTokenType):
	"""
	Consume a token of a given type and get the next token.
	If the current token is NOT of the expected type, then
	raise an error.
	"""
	if token.type == argTokenType:
		getToken()
	else:
		error("I was expecting to find "
			  + dq(argTokenType)
			  + " but I found " 
			  + token.show(align=False)
			)

#-------------------------------------------------------------------
#       eatWhile
#-------------------------------------------------------------------
def eatWhile(argTokenType):
	"""
	Keep consuming a token of a given type until a token of a different
	type is encountered.
	"""

	while token.type == argTokenType:
		getToken()


#-------------------------------------------------------------------
#    parse
#-------------------------------------------------------------------
def parse(sourceText, **kwargs):
	global lexer, verbose
	verbose = kwargs.get("verbose",False)
	# create a Lexer object & pass it the sourceText
	lexer.initialize(sourceText)
	getToken()
	ledger()
	if verbose:
		print "~"*80
		print "Successful parse!"
		print "~"*80
	return ast

#--------------------------------------------------------
#                   ledger
#--------------------------------------------------------
@track0
def ledger():
	"""
ledger = statement {statement} EOF.
	"""
	global ast
	node = Node(None, LEDGER)

	statement(node)
	while not found(EOF):
		statement(node)

	consume(EOF)
	ast = node


#--------------------------------------------------------
#                   statement
#--------------------------------------------------------
@track
def statement(node):
	"""
statement = NOTE | LINEBREAK | WHITESPACE | entry .
	"""
	if found(NOTE):
		note(node)
	elif found(LINEBREAK):
		eatWhile(LINEBREAK)
	elif found(WHITESPACE):
		eatWhile(WHITESPACE)
	else:  
		entryStatement(node)


#--------------------------------------------------------
#                   entryStatement
#--------------------------------------------------------
@track
def entryStatement(node):
	"""
entryStatement = date WS [*|!] WS [(code)] desc LB transaction {transaction} LB
	"""
	entryNode = Node(None, ENTRY)
	node.addNode(entryNode)

	date(entryNode)
	eatWhile(WHITESPACE)

	if found("*") or found("!"):
		entryNode.add(token)
		getToken()
	
	eatWhile(WHITESPACE)

	if found("("):
		code(entryNode)
	
	eatWhile(WHITESPACE)

	description(entryNode)

	consume(LINEBREAK)

	transaction(entryNode)

	while not found(LINEBREAK) and not found(EOF):
		if found(NOTE):
			consume(NOTE)
			consume(LINEBREAK)
		else:
			transaction(entryNode)


#--------------------------------------------------------
#                          date
#--------------------------------------------------------
@track
def date(node):
	"""
date = NUMBER / NUMBER / NUMBER .
	"""

	dateNode = Node(None, DATE)
	node.addNode(dateNode)

	dateNode.add(token)
	consume(NUMBER)
	dateNode.add(token)
	consume("/")
	dateNode.add(token)
	consume(NUMBER)
	dateNode.add(token)
	consume("/")
	dateNode.add(token)
	consume(NUMBER)


#--------------------------------------------------------
#                   				code
#--------------------------------------------------------
@track
def code(node):
	"""
code = ( anything {anything} )
	"""

	codeNode = Node(None, CODE)
	node.addNode(codeNode)

	consume("(")

	while not found(")"):
		codeNode.add(token)
		getToken()
	
	consume(")")


#--------------------------------------------------------
#                   description
#--------------------------------------------------------
@track
def description(node):
	"""
description =  anything {anything} LB .
	"""

	descNode = Node(None, DESCRIPTION)
	node.addNode(descNode)

	while not found(LINEBREAK):
		descNode.add(token)
		getToken()


#--------------------------------------------------------
#                   transaction
#--------------------------------------------------------
@track
def transaction(node):
	"""
transaction = WS account WS amount [value] [NOTE] LB .
	"""

	consume(WHITESPACE)
	eatWhile(WHITESPACE)

	if not found(LINEBREAK):
		transactionNode = Node(None, TRANSACTION)
		node.addNode(transactionNode)

		account(transactionNode)

		eatWhile(WHITESPACE)

		if not found(LINEBREAK):
			amount(transactionNode)

			eatWhile(WHITESPACE)

			if found("@") or found("@@"):
				value(transactionNode)

			eatWhile(WHITESPACE)
			
			if found(NOTE):
				note(transactionNode)
			
		consume(LINEBREAK)


#--------------------------------------------------------
#                   account
#--------------------------------------------------------
@track
def account(node):
	"""
account =  anything {anything}
	"""

	accountNode = Node(None, ACCOUNT)
	node.addNode(accountNode)

	while not found(WHITESPACE) and not found(LINEBREAK):
		accountNode.add(token)
		getToken()
	

#--------------------------------------------------------
#                   amount
#--------------------------------------------------------
@track
def amount(node):
	"""
amount =  NUMBER | commodity [WS] NUMBER | NUMBER commodity
	"""

	amountNode = Node(None, AMOUNT)
	node.addNode(amountNode)

	if found(NUMBER):
		amountNode.add(token)
		consume(NUMBER)

		eatWhile(WHITESPACE)
		
		if not found("@") and not found("@@") and not found(LINEBREAK) and not found(NOTE):
			commodity(amountNode)
		
	else:
		commodity(amountNode)

		eatWhile(WHITESPACE)

		amountNode.add(token)
		consume(NUMBER)


#--------------------------------------------------------
#                   commodity
#--------------------------------------------------------
@track
def commodity(node):
	"""
commodity =  anything | "any thing"
	"""

	commodityNode = Node(None, COMMODITY)
	node.addNode(commodityNode)

	if found('"'):
		commodityNode.add(token)
		consume('"')

		while not found('"'):
			commodityNode.add(token)
			getToken()
		
		commodityNode.add(token)
		consume('"')
	else:
		commodityNode.add(token)
		getToken()
	

#--------------------------------------------------------
#                   value
#--------------------------------------------------------
@track
def value(node):
	"""
value =  @ amount | @@ amount
	"""

	valueNode = Node(None, VALUE)
	node.addNode(valueNode)

	if found("@@"):
		valueNode.add(token)
		consume("@@")
	else:
		valueNode.add(token)
		consume("@")
	
	eatWhile(WHITESPACE)
	amount(valueNode)


#--------------------------------------------------------
#                       note
#--------------------------------------------------------
def note(node):
	node.add(token)
	consume(NOTE)



