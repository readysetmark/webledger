# import os
# import time

# import webledger.parser.ledgertree as ledgertree
# import webledger.journal.journal as j
# import webledger.report.balance as balance


# from flask import Flask



# app = Flask(__name__)
# app.debug = True


# @app.route("/")
# def hello_world():
# 	return "Hello World!"



# def read_journal_data(source_filename):
# 	"""
# 	Read in and return the journal data
# 	"""
# 	t1 = time.time()
# 	tree = ledgertree.parse_into_ledgertree(source_filename)
# 	journal = j.ledgertree_to_journal(tree)
# 	t2 = time.time()

# 	print "Parsed ledger file in %0.3f ms" % ((t2-t1)*1000.0)

# 	return journal



# # if __name__ == "__main__":
# # 	#source_filename = "input\\test.dat"
# # 	#source_filename = "input\\ledger.dat"
# # 	source_filename = os.getenv("LEDGER_FILE", "")
	
# # 	if source_filename == "":
# # 		print "Could not find path to ledger file in LEDGER_FILE enviornment variable."
# # 	else:
# # 		journal = read_journal_data(source_filename)
		
# # 		app.run()
