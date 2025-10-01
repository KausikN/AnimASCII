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
config = json.load(open("./StreamLitGUI/UIConfig.json", "r"))

# Main Functions
def main():
    # Create Sidebar
    selected_box = st.sidebar.selectbox(
    "Choose one of the following",
        tuple(
            [config["PROJECT_NAME"]] + 
            config["PROJECT_MODES"]
        )
    )
    
    if selected_box == config["PROJECT_NAME"]:
        HomePage()
    else:
        correspondingFuncName = selected_box.replace(" ", "_").lower()
        if correspondingFuncName in globals().keys():
            globals()[correspondingFuncName]()
 

def HomePage():
    st.title(config["PROJECT_NAME"])
    st.markdown("Github Repo: " + "[" + config["PROJECT_LINK"] + "](" + config["PROJECT_LINK"] + ")")
    st.markdown(config["PROJECT_DESC"])

    # st.write(open(config["PROJECT_README"], "r").read())

#############################################################################################################################
# Repo Based Vars
PATHS = {
    "animations": {
        "examples": "Data/Examples/"
    },
    "defaults": {
        "image": "StreamLitGUI/DefaultData/ExampleImage.png",
        "video": "StreamLitGUI/DefaultData/ExampleVideo.mp4"
    },
    "image_ascii_maps": "Data/ImageASCIIData/"
}

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

INDICATOR_IMAGEASCII_IMAGE_SIZE = [256, 256]
INDICATOR_IMAGEASCII_ASCII_SIZE = [8, 8]

# Util Vars
ANIMATION_EXAMPLES = []
ANIMATION_PLAYLIST = [] # Example element => [window, frames, loopCount, finishStatus]
IMAGE_ASCII_MAPS = {}
INDICATOR_IMAGEASCII_IMAGE = None
INDICATOR_IMAGEASCII_ASCII = None

# Util Functions
def AddInbetweenSpace(text, spaces=1):
    '''
    Adds spaces inbetween characters of text
    '''
    textLines = text.split("\n")
    textSpacedLines = [(" "*spaces).join(list(l)) for l in textLines]
    textSpaced = "\n".join(textSpacedLines)
    return textSpaced

def GetNames(data):
    '''
    Gets names from list of dicts with "name" key
    '''
    data_names = []
    for d in data:
        data_names.append(d["name"])
    return data_names

def GetASCIIWidth(asciiData):
    '''
    Gets width of ASCII data
    '''
    return max(list(map(len, asciiData.split("\n"))))

def GenerateIndicatorImage_ImageASCII():
    '''
    Generate Indicator Image - Default gradient image
    '''
    global INDICATOR_IMAGEASCII_IMAGE
    if INDICATOR_IMAGEASCII_IMAGE is None:
        INDICATOR_IMAGEASCII_IMAGE = [list(range(i, i+128)) for i in range(0, 128)]
        INDICATOR_IMAGEASCII_IMAGE = np.array(INDICATOR_IMAGEASCII_IMAGE, dtype=np.uint8)
        INDICATOR_IMAGEASCII_IMAGE = cv2.resize(INDICATOR_IMAGEASCII_IMAGE, tuple(INDICATOR_IMAGEASCII_IMAGE_SIZE))
    return INDICATOR_IMAGEASCII_IMAGE

# Main Functions
def DisplayASCIIAnimationsCombined():
    '''
    Displays all registered ASCII animations in combined manner
    '''
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
    '''
    Load example animations
    '''
    global ANIMATION_EXAMPLES
    for p in os.listdir(PATHS["animations"]["examples"]):
        anim = json.load(open(os.path.join(PATHS["animations"]["examples"], p), "r"))
        ANIMATION_EXAMPLES.append(anim)

def LoadImageASCIIMaps():
    '''
    Load Image ASCII Maps
    '''
    global IMAGE_ASCII_MAPS
    for f in os.listdir(PATHS["image_ascii_maps"]):
        if f.endswith(".json"):
            image_ascii_map = json.load(open(os.path.join(PATHS["image_ascii_maps"], f), "r"))
            IMAGE_ASCII_MAPS[image_ascii_map["name"]] = image_ascii_map

def GetTextDisplayCode(text, imgWidth, maxPixs=750, scale=0.8, compact=True):
    '''
    Get text display code for streamlit
    '''
    if compact: return "```\n" + text + "\n```"

    fontPixRange = [0.01, 35.0]

    PrefixCode = "<pre><p style='font-family:Courier; color:White; font-size: {fontWidthPixs}px;'>"
    PostfixCode = "</p></pre>"
    fontWidthPixs = min(fontPixRange[1], max(fontPixRange[0], (maxPixs / imgWidth)*scale))
    # fontWidthPixs = int(fontWidthPixs)
    PrefixCode = PrefixCode.format(fontWidthPixs=fontWidthPixs)

    text = PrefixCode + text.replace(" ", "&nbsp;").replace("\n", "<br>") + PostfixCode

    return text

# UI Functions
def UI_RegisterDisplayASCIIAnimation(frames, col=st, loopCount=-1):
    '''
    UI - Register Display ASCII Animation
    '''
    AnimDisplay = col.empty()
    ANIMATION_PLAYLIST.append([AnimDisplay, frames, loopCount, False])

def UI_LoadImage():
    '''
    UI - Load Image
    '''
    USERINPUT_ImageData = st.file_uploader("Upload Start Image", ["png", "jpg", "jpeg", "bmp"])

    if USERINPUT_ImageData is not None:
        USERINPUT_ImageData = USERINPUT_ImageData.read()
    if USERINPUT_ImageData is None:
        USERINPUT_ImageData = open(PATHS["defaults"]["image"], "rb").read()

    USERINPUT_Image = cv2.imdecode(np.frombuffer(USERINPUT_ImageData, np.uint8), cv2.IMREAD_COLOR)
    USERINPUT_Image = cv2.cvtColor(USERINPUT_Image, cv2.COLOR_BGR2RGB)
    st.image(USERINPUT_Image, "Input Image")

    USERINPUT_ResizeRatio = st.slider("Resize Ratio", 0.0, 1.0, 0.01, 0.01)
    USERINPUT_Invert = st.checkbox("Invert Image?")

    ResizedSize = (int(USERINPUT_Image.shape[1] * USERINPUT_ResizeRatio), int(USERINPUT_Image.shape[0] * USERINPUT_ResizeRatio))
    USERINPUT_Image = cv2.resize(USERINPUT_Image, ResizedSize)
    if USERINPUT_Invert:
        USERINPUT_Image = 255 - USERINPUT_Image

    return USERINPUT_Image

def UI_LoadVideo():
    '''
    UI - Load Video
    '''
    USERINPUT_VideoInputChoice = st.selectbox("Select Video Input Source", list(INPUTREADERS_VIDEO.keys()))

    USERINPUT_VideoReader = None
    FiniteFrames = False
    # Upload Video File
    if USERINPUT_VideoInputChoice == "Upload Video File":
        USERINPUT_VideoReader = INPUTREADERS_VIDEO[USERINPUT_VideoInputChoice]
        USERINPUT_VideoPath = st.file_uploader("Upload Video", ["avi", "mp4", "wmv"])
        if USERINPUT_VideoPath is None:
            USERINPUT_VideoPath = PATHS["defaults"]["video"]
        USERINPUT_VideoReader = functools.partial(USERINPUT_VideoReader, USERINPUT_VideoPath)
        FiniteFrames = True
    # Webcam
    else:
        USERINPUT_VideoReader = INPUTREADERS_VIDEO[USERINPUT_VideoInputChoice]

    USERINPUT_Video = USERINPUT_VideoReader()

    return USERINPUT_Video, not FiniteFrames

def UI_ChooseStyle():
    '''
    UI - Choose Style
    '''
    global INDICATOR_IMAGEASCII_IMAGE

    USERINPUT_StyleChoice = st.selectbox("Select Style", ["Select Style"] + list(IMAGE_PROCESS_STYLES.keys()))
    if USERINPUT_StyleChoice == "Select Style": return None
    USERINPUT_ProcessStyle = IMAGE_PROCESS_STYLES[USERINPUT_StyleChoice]
    if USERINPUT_StyleChoice == "Borders-Based":
        USERINPUT_BorderThresholds = st.slider("Border Thresholds", 0, 255, (30, 200), 1)
        USERINPUT_ProcessStyle = functools.partial(USERINPUT_ProcessStyle, thresholds=USERINPUT_BorderThresholds)

    USERINPUT_ImageASCIIMapChoice = st.sidebar.selectbox("Select Image ASCII Map", list(IMAGE_ASCII_MAPS.keys()))
    USERINPUT_ImageASCIIMap = IMAGE_ASCII_MAPS[USERINPUT_ImageASCIIMapChoice]

    col1, col2 = st.sidebar.columns(2)
    GenerateIndicatorImage_ImageASCII()
    col1.image(INDICATOR_IMAGEASCII_IMAGE, caption="Indicator Image", use_container_width=True)
    IndicatorImageResized = cv2.resize(INDICATOR_IMAGEASCII_IMAGE, tuple(INDICATOR_IMAGEASCII_ASCII_SIZE))
    IndicatorStyle = functools.partial(IMAGE_PROCESS_STYLES["Fill-Based"], IMAGE_FILL_ASCII=USERINPUT_ImageASCIIMap)
    INDICATOR_IMAGEASCII_ASCII, finalImg = AnimASCII.Convert_Image2ASCIIArt(IndicatorImageResized, IndicatorStyle)
    INDICATOR_IMAGEASCII_ASCII = AddInbetweenSpace(INDICATOR_IMAGEASCII_ASCII, spaces=2)
    INDICATOR_IMAGEASCII_ASCII = GetTextDisplayCode(INDICATOR_IMAGEASCII_ASCII, GetASCIIWidth(INDICATOR_IMAGEASCII_ASCII), scale=0.25, compact=False)
    col2.markdown(INDICATOR_IMAGEASCII_ASCII, unsafe_allow_html=True)

    USERINPUT_ProcessStyle = functools.partial(USERINPUT_ProcessStyle, IMAGE_FILL_ASCII=USERINPUT_ImageASCIIMap)

    return USERINPUT_ProcessStyle

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
    USERINPUT_CompactDisplay = st.sidebar.checkbox("Compact Display", True)

    # Process Inputs
    GenASCIIArt = AnimASCII.Convert_Text2ASCIIArt(USERINPUT_Text, USERINPUT_FontChoice)

    # Display Output
    asciiWidth = GetASCIIWidth(GenASCIIArt)
    GenASCIIArt = GetTextDisplayCode(GenASCIIArt, asciiWidth, compact=USERINPUT_CompactDisplay)

    st.markdown("## Display ASCII Art")
    st.markdown(GenASCIIArt, unsafe_allow_html=True)

def image_to_ascii():
    # Title
    st.header("Image to ASCII")

    LoadImageASCIIMaps()

    # Load Inputs
    USERINPUT_Image = UI_LoadImage()

    USERINPUT_ProcessStyle = UI_ChooseStyle()
    if USERINPUT_ProcessStyle is None: return

    # Process Inputs
    GenASCIIArt, I_final = AnimASCII.Convert_Image2ASCIIArt(USERINPUT_Image, USERINPUT_ProcessStyle)
    GenASCIIArt_Padded = PaddingLibrary.Padding_FramePad([GenASCIIArt])[0]
    GenASCIIArt_Padded = AddInbetweenSpace(GenASCIIArt_Padded, spaces=2)
    USERINPUT_CompactDisplay = st.sidebar.checkbox("Compact Display", True)

    # Display Output
    st.markdown("## Display ASCII Art")

    col1, col2 = st.columns(2)
    col1.image(USERINPUT_Image, caption="Original Image", use_container_width=True)
    col2.image(I_final, caption="Final Image", use_container_width=True)

    asciiWidth = GetASCIIWidth(GenASCIIArt_Padded)
    GenASCIIArt_Padded = GetTextDisplayCode(GenASCIIArt_Padded, asciiWidth, compact=USERINPUT_CompactDisplay)
    st.markdown(GenASCIIArt_Padded, unsafe_allow_html=True)

def video_to_ascii_animation():
    # Title
    st.header("Video to ASCII Animation")

    LoadImageASCIIMaps()

    # Load Inputs
    USERINPUT_Video, WebcamVid = UI_LoadVideo()

    USERINPUT_ProcessStyle = UI_ChooseStyle()
    if USERINPUT_ProcessStyle is None: return

    USERINPUT_Invert = st.checkbox("Invert Video Frames?")
    USERINPUT_ResizeRatio = st.slider("Resize Ratio", 0.0, 1.0, 0.01, 0.01)
    USERINPUT_CompactDisplay = st.sidebar.checkbox("Compact Display", True)

    st.markdown("## Display ASCII Animation")
    LoaderWidget = st.empty()
    col1, col2 = st.columns(2)
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
            if USERINPUT_Invert:
                frame = 255 - frame
            GenASCIIArt, frame_final = AnimASCII.Convert_Image2ASCIIArt(frame, USERINPUT_ProcessStyle)
            GenASCIIArt_Padded = PaddingLibrary.Padding_FramePad([GenASCIIArt])[0]
            GenASCIIArt_Padded = AddInbetweenSpace(GenASCIIArt_Padded, spaces=2)
            GenASCIIAnim.append(GenASCIIArt_Padded)
            Frames_Processed.append(frame_final)
            i+=1
            LoaderWidget.markdown("[" + str(i) + " / " + str(len(USERINPUT_Frames)) + "]" + ": Frames Processed")
        LoaderWidget.markdown("All Frames Processed :smiley:!")

        asciiWidth = GetASCIIWidth(GenASCIIAnim[0])

        frameMaxCount = len(USERINPUT_Frames)
        frameIndex = 0
        while True:
            frame = cv2.cvtColor(USERINPUT_Frames[frameIndex], cv2.COLOR_BGR2RGB)
            frame_processed = Frames_Processed[frameIndex]
            GenASCIIArt_Padded = GenASCIIAnim[frameIndex]
            GenASCIIArt_Padded = GetTextDisplayCode(GenASCIIArt_Padded, asciiWidth, compact=USERINPUT_CompactDisplay)
            AnimWidget_Frame.image(frame, caption="Original", use_container_width=True)
            AnimWidget_FinalImage.image(frame_processed, caption="Final", use_container_width=True)
            AnimWidget_ASCII.markdown("\n"
             + GenASCIIArt_Padded
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
                if USERINPUT_Invert:
                    frame_processed = 255 - frame_processed

                GenASCIIArt, frame_processed = AnimASCII.Convert_Image2ASCIIArt(frame_processed, USERINPUT_ProcessStyle)
                GenASCIIArt_Padded = PaddingLibrary.Padding_FramePad([GenASCIIArt])[0]
                GenASCIIArt_Padded = AddInbetweenSpace(GenASCIIArt_Padded, spaces=2)
                frameCount += 1

                if not sizeFixed:
                    asciiWidth = GetASCIIWidth(GenASCIIArt_Padded)
                    GenASCIIArt_Padded = GetTextDisplayCode(GenASCIIArt_Padded, asciiWidth, compact=USERINPUT_CompactDisplay)
                    sizeFixed = True

                AnimWidget_Frame.image(frame, caption="Original", use_container_width=True)
                AnimWidget_FinalImage.image(frame_processed, caption="Final", use_container_width=True)
                AnimWidget_ASCII.markdown("\n"
                + GenASCIIArt_Padded
                , unsafe_allow_html=True)

#############################################################################################################################
# Driver Code
if __name__ == "__main__":
    main()