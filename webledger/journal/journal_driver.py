#fragment start *
import webledger.parser.ledgertree as ledgertree
import journal as j
import os
import time

#-------------------------------------------------
# support for writing output to a file
#-------------------------------------------------
def writeln(*args):
	for arg in args:
		f.write(str(arg))
	f.write("\n")

if __name__ == "__main__":
	output_filename = "output\\journal_driver.txt"
	#source_filename = "input\\test.dat"
	#source_filename = "input\\ledger.dat"
	source_filename = os.getenv("LEDGER_FILE", "input\\ledger.dat")
	
	t1 = time.time()
	tree = ledgertree.parse_into_ledgertree(source_filename)
	journal = j.ledgertree_to_journal(tree)
	t2 = time.time()

	print "~"*80
	print "Here is the journal:"
	print "~"*80
	f = open(output_filename,"w")
	for entry in journal:
		f.write(entry.to_string() +"\n")
	f.close()
	print(open(output_filename).read())

	print "Took %0.3f ms to parse" % ((t2-t1)*1000.0)
