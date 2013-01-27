#fragment start *
import ledgerParser as parser
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
	OutputFilename = "output\\ledgerParserDriver.txt"
	#sourceFilename = "input\\test.dat"
	#sourceFilename = "input\\ledger.dat"
	sourceFilename = os.getenv("LEDGER_FILE", "input\\ledger.dat")
	print "Parsing %s." % sourceFilename
	sourceText = open(sourceFilename).read()

	t1 = time.time()
	ast = parser.parse(sourceText, verbose=False)
	t2 = time.time()

	print "~"*80
	print "Here is the abstract syntax tree:"
	print "~"*80
	f = open(OutputFilename,"w")
	f.write(ast.toString())
	f.close()
	print(open(OutputFilename).read())

	print "Took %0.3f ms to parse" % ((t2-t1)*1000.0)
