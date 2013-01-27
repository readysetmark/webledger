"""
A lexer (aka: Tokenizer, Lexical Analyzer) for ledger files
"""
import genericScanner as scanner
from   genericToken      import *
from   ledgerSymbols        import *

class LexerError(Exception): pass

# enclose string s in double quotes
def dq(s): return '"%s"' %s

#-------------------------------------------------------------------
#
#-------------------------------------------------------------------
def initialize(sourceText):
    """
    """
    global scanner

    # initialize the scanner with the sourceText
    scanner.initialize(sourceText)

    # use the scanner to read the first character from the sourceText
    getChar()

#-------------------------------------------------------------------
#
#-------------------------------------------------------------------
def get():
    """
    Construct and return the next token in the sourceText.
    """

    #--------------------------------------------------------------------------------
    # read past and ignore any whitespace characters or any comments -- START
    #--------------------------------------------------------------------------------
    while c1 in WHITESPACE_CHARS or c1 in NOTE_STARTCHARS:

        # process whitespace
        while c1 in WHITESPACE_CHARS:
            token = Token(character)
            token.type = WHITESPACE
            getChar() 

            while c1 in WHITESPACE_CHARS:
                token.cargo += c1
                getChar() 
                        
            return token  # only if we want the lexer to return whitespace

        # process notes
        while c1 in NOTE_STARTCHARS:
            # we found comment start
            token = Token(character)
            token.type = NOTE
            token.cargo = c1

            getChar()

            while not (c1 in (LINEBREAK_CHARS + ENDMARK)):
                token.cargo += c1
                getChar() 

            token.cargo = token.cargo.lstrip("; ")
            return token  # only if we want the lexer to return comments
    #--------------------------------------------------------------------------------
    # read past and ignore any whitespace characters or any comments -- END
    #--------------------------------------------------------------------------------

    # Create a new token.  The token will pick up
    # its line and column information from the character.
    token = Token(character)

    if c1 == ENDMARK:
        token.type = EOF
        return token

    if c1 in IDENTIFIER_STARTCHARS:
        token.type = IDENTIFIER
        getChar() 

        while c1 in IDENTIFIER_CHARS:
            token.cargo += c1
            getChar() 

        #if token.cargo in Keywords: token.type = token.cargo
        return token

    if c1 in NUMBER_STARTCHARS:
        token.type = NUMBER
        getChar() 
        
        while c1 in NUMBER_CHARS:
            token.cargo += c1
            getChar() 
        return token

    if c1 in LINEBREAK_CHARS:
        token.type = LINEBREAK
        getChar()
        return token
    
    # if c1 in STRING_STARTCHARS:
    #     # remember the quoteChar (single or double quote)
    #     # so we can look for the same character to terminate the quote.
    #     quoteChar   = c1

    #     getChar() 

    #     while c1 != quoteChar:
    #         if c1 == ENDMARK:
    #             token.abort("Found end of file before end of string literal")

    #         token.cargo += c1  # append quoted character to text
    #         getChar()      

    #     token.cargo += c1      # append close quote to text
    #     getChar()          
    #     token.type = STRING
    #     return token


    if c2 in TwoCharacterSymbols:
        token.cargo = c2
        token.type  = token.cargo  # for symbols, the token type is same as the cargo
        getChar() # read past the first  character of a 2-character token
        getChar() # read past the second character of a 2-character token
        return token

    if c1 in OneCharacterSymbols:
        token.type  = token.cargo  # for symbols, the token type is same as the cargo
        getChar() # read past the symbol
        return token

    # else.... We have encountered something that we don't recognize.
    token.abort("I found a character or symbol that I do not recognize: " + dq(c1))

#-------------------------------------------------------------------
#
#-------------------------------------------------------------------
def getChar():
    """
    get the next character
    """
    global c1, c2, character
    character     = scanner.get()
    c1 = character.cargo
    #---------------------------------------------------------------
    # Every time we get a character from the scanner, we also  
    # lookahead to the next character and save the results in c2.
    # This makes it easy to lookahead 2 characters.
    #---------------------------------------------------------------
    c2    = c1 + scanner.lookahead(1)
