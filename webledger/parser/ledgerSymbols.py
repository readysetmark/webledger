#----------------------------------------------------------
# a list of symbols that are one character long
#----------------------------------------------------------
OneCharacterSymbols = """
=
( )
< >
/ * + -
! & $ @ : ? # %
, . ' "
"""
OneCharacterSymbols = OneCharacterSymbols.split()

#----------------------------------------------------------
# a list of symbols that are two characters long
#----------------------------------------------------------
TwoCharacterSymbols = """
@@
"""
TwoCharacterSymbols = TwoCharacterSymbols.split()

import string

IDENTIFIER_STARTCHARS = string.letters
IDENTIFIER_CHARS      = string.letters + string.digits + "_"

NUMBER_STARTCHARS     = string.digits + "-"
NUMBER_CHARS          = string.digits + ".,"

NOTE_STARTCHARS = ";"
LINEBREAK_CHARS = "\r\n"
WHITESPACE_CHARS  = " \t"

#-----------------------------------------------------------------------
# TokenTypes for things other than symbols and keywords
#-----------------------------------------------------------------------
STRING             = "String"
IDENTIFIER         = "Identifier"
NUMBER             = "Number"
LINEBREAK 				 = "Linebreak"
WHITESPACE         = "Whitespace"
NOTE               = "Note"
EOF                = "EOF"