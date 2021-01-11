# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import speech_recognition as sr

def speech_from_mic(recognizer, microphone):
    """takes speech from microphone turn to text
    returns a directory with one of 3 values
    "success" : boolean saying API request was sucessful or not
    "error": none if no errors otherwise a string containg the error
    "transcription": none if speech could not be transcibed else a string
    """

    #check that recognizer and mariphone are appropriate types
    if not isinstance(recognizer,sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("microphone object must be of sr.Microphone")

    #we ajust amibant sensinstanty to ambient noise
    #then we record from microphone and save as var audio
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    #seting up response object
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    


# Press the green button in the gutter to run the script.
if __name__ == '__main__':


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
