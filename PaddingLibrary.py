'''
Padding Library for ascii animation padding functions
'''

# Imports


# Main Functions
def Padding_SimpleStrRepeat(textList, padStr="o", X_count=1, Y_count=1):
    # Pad the data in X and Y as specified with mentioned string for mentioned times
    # ---
    # -0-       =>  Padding 1, 1
    # ---

    Counts = [X_count, Y_count]

    processedList = []
    for text in textList:
        textLines = text.split("\n")
        lineLens = list(map(len, textLines))
        textDims = [max(lineLens), len(textLines)]
        
        padLenMid_X = [int(textDims[0]/len(padStr)), textDims[0]%len(padStr)]
        pad_X = [padStr*Counts[0], (padStr*padLenMid_X[0]) + padStr[:padLenMid_X[1]], padStr*Counts[0]]
        padLine = ''.join(pad_X)
        
        paddedLines = []
        paddedLines = paddedLines + [padLine]*Counts[1]
        for l in textLines:
            textLineMatchPadCount = textDims[0] - len(l)
            pad_L = [padStr*Counts[0], l + " "*(textLineMatchPadCount), padStr*Counts[0]]
            textLine = ''.join(pad_L)
            paddedLines.append(textLine)
        paddedLines = paddedLines + [padLine]*Counts[1]
        processedList.append("\n".join(paddedLines))

    return processedList


# Driver Code
