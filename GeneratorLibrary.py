'''
Generator Library for animation generator functions
'''

# Imports


# Main Functions
def GenerateAnimation_TextBased_BuildUpText(data):
    # Build up the given text letter by letter as animation - left to right - multi lines supported
    text = data["text"]
    textLines = text.split("\n")
    lineLens = list(map(len, textLines))
    textDims = [max(lineLens), len(textLines)]
    animList = []
    for i in range(1, textDims[0]):
        lines = []
        for l in textLines:
            line = l[:i] + " "*(textDims[0]-i)
            lines.append(line)
        frame = "\n".join(lines)
        animList.append(frame)
    return animList

# Driver Code