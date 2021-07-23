'''
Generator Library for animation generator functions
'''

# Imports
import cv2
import numpy as np

# Main Vars
IMAGE_FILL_ASCII = [
    {
        "fillStr": " ",
        "valRange": [0, 10]
    },
    {
        "fillStr": "o",
        "valRange": [10, 100]
    },
    {
        "fillStr": "v",
        "valRange": [100, 200]
    },
    {
        "fillStr": "@",
        "valRange": [200, 256]
    }
]

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

def GenerateASCII_ImageBased_Fill(I_g):
    asciiArray = np.array([[""]*I_g.shape[1]]*I_g.shape[0])
    for fillVals in IMAGE_FILL_ASCII:
        I_mask = (I_g >= fillVals["valRange"][0]) * (I_g < fillVals["valRange"][1])
        asciiArray[I_mask] = fillVals["fillStr"]
    asciiData = "\n".join(["".join(list(row)) for row in asciiArray])
    return asciiData

def GenerateASCII_ImageBased_Border(I_g):
    asciiArray = np.array([[""]*I_g.shape[1]]*I_g.shape[0])
    for fillVals in IMAGE_FILL_ASCII:
        I_mask = (I_g >= fillVals["valRange"][0]) * (I_g < fillVals["valRange"][1])
        asciiArray[I_mask] = fillVals["fillStr"]
    asciiData = "\n".join(["".join(list(row)) for row in asciiArray])
    return asciiData

# Driver Code
# # Params
# imgPath = "TestImgs/Test.jpg"
# # Params

# # RunCode
# I = cv2.imread(imgPath)
# print(I.shape)
# I = cv2.resize(I, (64, 48))
# cv2.imshow("Test", cv2.cvtColor(I, cv2.COLOR_RGB2GRAY))
# cv2.waitKey(0)
# asciiData = GenerateASCII_ImageBased_Fill(I)
# print(asciiData)