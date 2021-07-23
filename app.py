"""
Stream lit GUI for hosting AnimASCII
"""

# Imports
import os
import streamlit as st
import json
import time
import functools
import cv2
import numpy as np

import AnimASCII
import Fonts
import GeneratorLibrary
import PaddingLibrary
from Utils import VideoUtils

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
DEFAULT_PATH_EXAMPLEIMAGE = "StreamLitGUI/DefaultData/ExampleImage.png"
DEFAULT_PATH_EXAMPLEVIDEO = "StreamLitGUI/DefaultData/ExampleVideo.mp4"

IMAGE_PROCESS_STYLES = {
    "Fill-Based": GeneratorLibrary.GenerateASCII_ImageBased_Fill,
    "Borders-Based": GeneratorLibrary.GenerateASCII_ImageBased_Border
}

INPUTREADERS_VIDEO = {
    "Upload Video File": VideoUtils.ReadVideo,
    "Webcam": VideoUtils.WebcamVideo
}

ANIMATION_DISPLAYDELAY = 0.1
VIDEO_DISPLAYDELAY = 0.1

# Util Vars
ANIMATION_EXAMPLES = []
ANIMATION_PLAYLIST = [] # Example element => [window, frames, loopCount, finishStatus]

# Util Functions
def AddInbetweenSpace(text, spaces=1):
    textLines = text.split("\n")
    textSpacedLines = [(' '*spaces).join(list(l)) for l in textLines]
    textSpaced = '\n'.join(textSpacedLines)
    return textSpaced

def GetNames(data):
    data_names = []
    for d in data:
        data_names.append(d["name"])
    return data_names

def GetASCIIWidth(asciiData):
    return max(list(map(len, asciiData.split("\n"))))

# Main Functions
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

def LoadExampleAnimations():
    global ANIMATION_EXAMPLES
    for p in os.listdir(ANIMATION_EXAMPLES_PATH):
        anim = json.load(open(os.path.join(ANIMATION_EXAMPLES_PATH, p), 'r'))
        ANIMATION_EXAMPLES.append(anim)

def GetTextPrefixPostfixCode(imgWidth, maxPixs=750, scale=1.0):
    if not st.sidebar.checkbox("Compact Display", True): return "```\n", ""

    fontPixRange = [0.01, 35.0]

    PrefixCode = '<pre><p style="font-family:Courier; color:White; font-size: {fontWidthPixs}px;">'
    PostfixCode = '</p></pre>'
    fontWidthPixs = min(fontPixRange[1], max(fontPixRange[0], (maxPixs / imgWidth)*scale))
    # fontWidthPixs = int(fontWidthPixs)
    PrefixCode = PrefixCode.format(fontWidthPixs=fontWidthPixs)

    print(fontWidthPixs, imgWidth)

    return PrefixCode, PostfixCode

# UI Functions
def UI_RegisterDisplayASCIIAnimation(frames, col=st, loopCount=-1):
    AnimDisplay = col.empty()
    ANIMATION_PLAYLIST.append([AnimDisplay, frames, loopCount, False])

def UI_LoadImage():
    USERINPUT_ImageData = st.file_uploader("Upload Start Image", ['png', 'jpg', 'jpeg', 'bmp'])

    if USERINPUT_ImageData is not None:
        USERINPUT_ImageData = USERINPUT_ImageData.read()
    else:
        USERINPUT_ImageData = open(DEFAULT_PATH_EXAMPLEIMAGE, 'rb').read()

    USERINPUT_Image = cv2.imdecode(np.frombuffer(USERINPUT_ImageData, np.uint8), cv2.IMREAD_COLOR)
    USERINPUT_Image = cv2.cvtColor(USERINPUT_Image, cv2.COLOR_BGR2RGB)

    USERINPUT_ResizeRatio = st.slider("Resize Ratio", 0.0, 1.0, 0.01, 0.01)
    USERINPUT_Invert = st.checkbox("Invert Image?")

    col1, col2 = st.beta_columns(2)
    col1.image(USERINPUT_Image, caption="Original Image", use_column_width=True)
    
    ResizedSize = (int(USERINPUT_Image.shape[1] * USERINPUT_ResizeRatio), int(USERINPUT_Image.shape[0] * USERINPUT_ResizeRatio))
    USERINPUT_Image = cv2.resize(USERINPUT_Image, ResizedSize)
    USERINPUT_Image_gray = cv2.cvtColor(USERINPUT_Image, cv2.COLOR_RGB2GRAY)
    if USERINPUT_Invert:
        USERINPUT_Image_gray = 255 - USERINPUT_Image_gray
    col2.image(USERINPUT_Image_gray, caption="Final Image", use_column_width=True)

    return USERINPUT_Image_gray

def UI_LoadVideo():
    USERINPUT_VideoInputChoice = st.selectbox("Select Video Input Source", list(INPUTREADERS_VIDEO.keys()))

    USERINPUT_VideoReader = None
    FiniteFrames = False
    # Upload Video File
    if USERINPUT_VideoInputChoice == "Upload Video File":
        USERINPUT_VideoReader = INPUTREADERS_VIDEO[USERINPUT_VideoInputChoice]
        USERINPUT_VideoPath = st.file_uploader("Upload Video", ['avi', 'mp4', 'wmv'])
        if USERINPUT_VideoPath is None:
            USERINPUT_VideoPath = DEFAULT_PATH_EXAMPLEVIDEO
        USERINPUT_VideoReader = functools.partial(USERINPUT_VideoReader, USERINPUT_VideoPath)
        FiniteFrames = True
    # Webcam
    else:
        USERINPUT_VideoReader = INPUTREADERS_VIDEO[USERINPUT_VideoInputChoice]

    USERINPUT_Video = USERINPUT_VideoReader()

    return USERINPUT_Video, not FiniteFrames

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
    UI_RegisterDisplayASCIIAnimation(USERINPUT_Animation["data"])

    DisplayASCIIAnimationsCombined()

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
    asciiWidth = GetASCIIWidth(GenASCIIArt)
    PrefixCode, PostfixCode = GetTextPrefixPostfixCode(asciiWidth)

    st.markdown("## Display ASCII Art")
    st.markdown(PrefixCode + GenASCIIArt + PostfixCode, unsafe_allow_html=True)

def image_to_ascii():
    # Title
    st.header("Image to ASCII")

    # Load Inputs
    USERINPUT_StyleChoice = st.selectbox("Select Style", ["Select Style"] + list(IMAGE_PROCESS_STYLES.keys()))
    if USERINPUT_StyleChoice == "Select Style": return
    USERINPUT_ProcessStyle = IMAGE_PROCESS_STYLES[USERINPUT_StyleChoice]
    USERINPUT_Image = UI_LoadImage()

    # Process Inputs
    GenASCIIArt = AnimASCII.Convert_Image2ASCIIArt(USERINPUT_Image, USERINPUT_ProcessStyle)
    GenASCIIArt_Padded = PaddingLibrary.Padding_FramePad([GenASCIIArt])[0]
    GenASCIIArt_Padded = AddInbetweenSpace(GenASCIIArt_Padded, spaces=2)

    # Display Output
    asciiWidth = GetASCIIWidth(GenASCIIArt_Padded)
    PrefixCode, PostfixCode = GetTextPrefixPostfixCode(asciiWidth)

    st.markdown("## Display ASCII Art")
    st.markdown(PrefixCode + GenASCIIArt_Padded + PostfixCode, unsafe_allow_html=True)

def video_to_ascii_animation():
    # Title
    st.header("Video to ASCII Animation")

    # Load Inputs
    USERINPUT_StyleChoice = st.selectbox("Select Style", ["Select Style"] + list(IMAGE_PROCESS_STYLES.keys()))
    if USERINPUT_StyleChoice == "Select Style": return
    USERINPUT_ProcessStyle = IMAGE_PROCESS_STYLES[USERINPUT_StyleChoice]

    USERINPUT_Video, WebcamVid = UI_LoadVideo()

    USERINPUT_Invert = st.checkbox("Invert Video Frames?")
    USERINPUT_ResizeRatio = st.slider("Resize Ratio", 0.0, 1.0, 0.01, 0.01)

    st.markdown("## Display ASCII Animation")
    LoaderWidget = st.empty()
    col1, col2 = st.beta_columns(2)
    AnimWidget_Frame = col1.empty()
    AnimWidget_FinalImage = col2.empty()
    AnimWidget_ASCII = st.empty()

    PrefixCode, PostfixCode = "", ""

    if not WebcamVid:
        USERINPUT_Frames = VideoUtils.GetFramesFromVideo(USERINPUT_Video, max_frames=-1)

        GenASCIIAnim = []
        Frames_Processed = []
        i=0
        for frame in USERINPUT_Frames:
            ResizedSize = (int(frame.shape[1] * USERINPUT_ResizeRatio), int(frame.shape[0] * USERINPUT_ResizeRatio))
            frame = cv2.resize(frame, ResizedSize)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if USERINPUT_Invert:
                frame = 255 - frame
            GenASCIIArt = AnimASCII.Convert_Image2ASCIIArt(frame, USERINPUT_ProcessStyle)
            GenASCIIArt_Padded = PaddingLibrary.Padding_FramePad([GenASCIIArt])[0]
            GenASCIIArt_Padded = AddInbetweenSpace(GenASCIIArt_Padded, spaces=2)
            GenASCIIAnim.append(GenASCIIArt_Padded)
            Frames_Processed.append(frame)
            i+=1
            LoaderWidget.markdown("[" + str(i) + " / " + str(len(USERINPUT_Frames)) + "]" + ": Frames Processed")
        LoaderWidget.markdown("All Frames Processed :smiley:!")

        asciiWidth = GetASCIIWidth(GenASCIIAnim[0])
        PrefixCode, PostfixCode = GetTextPrefixPostfixCode(asciiWidth)

        frameMaxCount = len(USERINPUT_Frames)
        frameIndex = 0
        while True:
            frame = cv2.cvtColor(USERINPUT_Frames[frameIndex], cv2.COLOR_BGR2RGB)
            frame_processed = Frames_Processed[frameIndex]
            GenASCIIArt_Padded = GenASCIIAnim[frameIndex]
            AnimWidget_Frame.image(frame, caption="Original", use_column_width=True)
            AnimWidget_FinalImage.image(frame_processed, caption="Final", use_column_width=True)
            AnimWidget_ASCII.markdown("\n"
             + PrefixCode
             + GenASCIIArt_Padded
             + PostfixCode
            , unsafe_allow_html=True)
            frameIndex = (frameIndex + 1) % frameMaxCount
            time.sleep(VIDEO_DISPLAYDELAY)

    else:
        sizeFixed = False
        
        max_frames = -1
        frameCount = 0
        while(USERINPUT_Video.isOpened() and ((not (frameCount == max_frames)) or (max_frames == -1))):
            # Capture frame-by-frame
            ret, frame = USERINPUT_Video.read()
            if ret:
                ResizedSize = (int(frame.shape[1] * USERINPUT_ResizeRatio), int(frame.shape[0] * USERINPUT_ResizeRatio))
                frame = cv2.cvtColor(frame_processed, cv2.COLOR_BGR2RGB)
                frame_processed = cv2.resize(frame, ResizedSize)
                frame_processed = cv2.cvtColor(frame_processed, cv2.COLOR_RGB2GRAY)
                if USERINPUT_Invert:
                    frame_processed = 255 - frame_processed

                GenASCIIArt = AnimASCII.Convert_Image2ASCIIArt(frame, USERINPUT_ProcessStyle)
                GenASCIIArt_Padded = PaddingLibrary.Padding_FramePad([GenASCIIArt])[0]
                GenASCIIArt_Padded = AddInbetweenSpace(GenASCIIArt_Padded, spaces=2)
                frameCount += 1

                if not sizeFixed:
                    asciiWidth = GetASCIIWidth(GenASCIIArt_Padded)
                    PrefixCode, PostfixCode = GetTextPrefixPostfixCode(asciiWidth)
                    sizeFixed = True

                AnimWidget_Frame.image(frame, caption="Original", use_column_width=True)
                AnimWidget_FinalImage.image(frame_processed, caption="Final", use_column_width=True)
                AnimWidget_ASCII.markdown("\n"
                + PrefixCode
                + GenASCIIArt_Padded
                + PostfixCode
                , unsafe_allow_html=True)

#############################################################################################################################
# Driver Code
if __name__ == "__main__":
    main()