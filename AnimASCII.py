'''
A tool for generating and viewing ASCII animations (from images, text, sound and more!)
'''

# Imports
import cv2
import functools
import json
import art

import GeneratorLibrary
import PaddingLibrary

# Utils Functions
def Convert_ASCIIAnimList2JSONData(animList, name="Animation"):
    jsonData = {
        "name": name,
        "data": animList
    }
    return jsonData

# Conversion Functions
def Convert_Text2ASCIIArt(text, font="random"):
    asciiArt = art.text2art(text, font=font, chr_ignore=True)
    return asciiArt

# Main Functions
def Animation_Generate_Basic(data, savePath, GenertorFunc=GeneratorLibrary.GenerateAnimation_TextBased_BuildUpText):
    # Preprocess Data
    if "preProcessFuncs" in data.keys():
        text = data["text"]
        for func in data["preProcessFuncs"]:
            text = func(text)
        data["text"] = text

    # Get Generated List
    animList = GenertorFunc(data)

    # Postprocess Data
    if "postProcessFuncs" in data.keys():
        for func in data["postProcessFuncs"]:
            animList = func(animList)

    # Convert to JSON data
    jsonData = Convert_ASCIIAnimList2JSONData(animList, data["name"])

    # Save JSON
    json.dump(jsonData, open(savePath, 'w'))

    return jsonData

# # Driver Code
# # Params
# animName = "Loading_3"
# savePath = 'Examples/' + animName + '.json'

# GeneratorFunc = GeneratorLibrary.GenerateAnimation_TextBased_BuildUpText
# inputData = {
#     "name": animName,
#     "text": 
# """ASCII Animator""",
#     "preProcessFuncs": [
#         functools.partial(Convert_Text2ASCIIArt, font="random")
#     ],
#     "postProcessFuncs": [
#         functools.partial(PaddingLibrary.Padding_SimpleStrRepeat, padStr="o", X_count=1, Y_count=1)
#     ]
# }
# # Params

# # RunCode
# Animation_Generate_Basic(inputData, savePath, GeneratorFunc)