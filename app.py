"""
Stream lit GUI for hosting AnimASCII
"""

# Imports
import os
import streamlit as st
import json
import time

import AnimASCII
import Fonts

# Main Vars
config = json.load(open('./StreamLitGUI/UIConfig.json', 'r'))

# Main Functions
def main():
    # Create Sidebar
    selected_box = st.sidebar.selectbox(
    'Choose one of the following',
        tuple(
            [config['PROJECT_NAME']] + 
            config['PROJECT_MODES']
        )
    )
    
    if selected_box == config['PROJECT_NAME']:
        HomePage()
    else:
        correspondingFuncName = selected_box.replace(' ', '_').lower()
        if correspondingFuncName in globals().keys():
            globals()[correspondingFuncName]()
 

def HomePage():
    st.title(config['PROJECT_NAME'])
    st.markdown('Github Repo: ' + "[" + config['PROJECT_LINK'] + "](" + config['PROJECT_LINK'] + ")")
    st.markdown(config['PROJECT_DESC'])

    # st.write(open(config['PROJECT_README'], 'r').read())

#############################################################################################################################
# Repo Based Vars
ANIMATION_EXAMPLES_PATH = "Examples/"

ANIMATION_DISPLAYDELAY = 0.1

# Util Vars
ANIMATION_EXAMPLES = []
ANIMATION_PLAYLIST = [] # Example element => [window, frames, loopCount, finishStatus]

# Util Functions
def GetNames(data):
    data_names = []
    for d in data:
        data_names.append(d["name"])
    return data_names

def DisplayASCIIAnimationsCombined():
    i = 0
    allDone = False
    while not allDone:
        allDone = True
        for anim in ANIMATION_PLAYLIST:
            AnimDisplay = anim[0]
            frames = anim[1]
            loopCount = anim[2]
            if (i < (len(frames)*loopCount)) or (loopCount == -1):
                AnimDisplay.markdown("```\n" + frames[i%len(frames)])
                allDone = False
            else:
                anim[3] = True
        i += 1
        time.sleep(ANIMATION_DISPLAYDELAY)

# Main Functions
def LoadExampleAnimations():
    global ANIMATION_EXAMPLES
    for p in os.listdir(ANIMATION_EXAMPLES_PATH):
        anim = json.load(open(os.path.join(ANIMATION_EXAMPLES_PATH, p), 'r'))
        ANIMATION_EXAMPLES.append(anim)


# UI Functions
def UI_DisplayASCIIAnimation(frames, col=st, loopCount=-1):
    AnimDisplay = col.empty()
    ANIMATION_PLAYLIST.append([AnimDisplay, frames, loopCount, False])


# Repo Based Functions
def example_animations():

    # Title
    st.header("Example Animations")

    LoadExampleAnimations()

    # Load Inputs
    ExampleAnimationNames = GetNames(ANIMATION_EXAMPLES)
    USERINPUT_AnimationChoice = st.selectbox("Select Animation", ["Select Animation"] + ExampleAnimationNames)
    if USERINPUT_AnimationChoice == "Select Animation": return
    USERINPUT_AnimationChoiceIndex = ExampleAnimationNames.index(USERINPUT_AnimationChoice)
    USERINPUT_Animation = ANIMATION_EXAMPLES[USERINPUT_AnimationChoiceIndex]

    # Process Inputs
    

    # Display Output
    st.markdown("## Display Animation")
    st.markdown(USERINPUT_Animation["name"])
    UI_DisplayASCIIAnimation(USERINPUT_Animation["data"])

def text_to_ascii():

    # Title
    st.header("Text to ASCII")

    # Load Inputs
    USERINPUT_Text = st.text_area("Enter Text", "")
    USERINPUT_FontChoice = st.selectbox("Select Font", ["Select Font", "Random"] + Fonts.FONT_NAMES)
    if USERINPUT_FontChoice == "Select Font": return

    # Process Inputs
    GenASCIIArt = AnimASCII.Convert_Text2ASCIIArt(USERINPUT_Text, USERINPUT_FontChoice)

    # Display Output
    st.markdown("## Display ASCII Art")
    st.markdown("```\n" + GenASCIIArt)


#############################################################################################################################
# Driver Code
if __name__ == "__main__":
    main()