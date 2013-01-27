from genericCharacter import *

"""
A Scanner object reads through the sourceText
and returns one character at a time.
"""
#-------------------------------------------------------------------
#
#-------------------------------------------------------------------
def initialize(sourceTextArg):
    global sourceText, lastIndex, sourceIndex, lineIndex, colIndex
    sourceText = sourceTextArg
    lastIndex    = len(sourceText) - 1
    sourceIndex  = -1
    lineIndex    =  0
    colIndex     = -1


#-------------------------------------------------------------------
#
#-------------------------------------------------------------------
def get():
    """
    Return the next character in sourceText.
    """
    global lastIndex, sourceIndex, lineIndex, colIndex

    sourceIndex += 1    # increment the index in sourceText

    # maintain the line count
    if sourceIndex > 0:
        if sourceText[sourceIndex - 1] == "\n":
            #-------------------------------------------------------
            # The previous character in sourceText was a newline
            # character.  So... we're starting a new line.
            # Increment lineIndex and reset colIndex.
            #-------------------------------------------------------
            lineIndex +=1
            colIndex  = -1

    colIndex += 1

    if sourceIndex > lastIndex:
        # We've read past the end of sourceText.
        # Return the ENDMARK character.
        char = Character(ENDMARK, lineIndex, colIndex, sourceIndex,sourceText)
    else:
        c    = sourceText[sourceIndex]
        char = Character(c, lineIndex, colIndex, sourceIndex, sourceText)

    return char


#-------------------------------------------------------------------
#
#-------------------------------------------------------------------
def lookahead(numChars):
    """
    Look ahead numChars number of characters
    """

    lookaheadIndex = sourceIndex + numChars

    if lookaheadIndex > lastIndex:
        c = ENDMARK
    else:
        c = sourceText[lookaheadIndex]
    
    return c