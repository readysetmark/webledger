import ledgerLexer   as     lexer
from   ledgerSymbols import EOF

#-------------------------------------------------
# support for writing output to a file
#-------------------------------------------------
def writeln(*args):
    for arg in args:
        f.write(str(arg))
    f.write("\n")

#-----------------------------------------------------------------------
#
#                    main
#
#-----------------------------------------------------------------------
def main(sourceText):
    global f
    f = open(outputFilename, "w")
    writeln("Here are the tokens returned by the lexer:")

    # create an instance of a lexer
    lexer.initialize(sourceText)

    #------------------------------------------------------------------
    # use the lexer.getlist() method repeatedly to get the tokens in
    # the sourceText. Then print the tokens.
    #------------------------------------------------------------------
    while True:
        token = lexer.get()
        writeln(token.show(True))
        if token.type == EOF: break
    f.close()


if __name__ == "__main__":
    outputFilename = "output\\ledgerLexerDriver.txt"
    sourceFilename = "input\\test.dat"
    #sourceFilename = "input\\ledger.dat"
    sourceText = open(sourceFilename).read()
    main(sourceText)
    print(open(outputFilename).read())