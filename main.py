# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import speech_recognition as sr
import pyttsx3
import time


class Patient:
    name: str
    bed: int
    room: int
    condition: str
    risk_level: int

    def __init__(self, name: str, bed: int, room: int, condition: str, risk_level: int):
        self.name = name
        self.bed = bed
        self.room = room
        self.condition = condition
        self.risk_level = risk_level


class Alarm:
    patient: Patient
    timeOfAlarm: time.localtime()
    timeOfAlarmOff: time.localtime()
    nurse: str

    def __init__(self, patient: Patient):
        self.patient = patient


def speech_from_mic(recognizer, microphone):
    """takes speech from microphone turn to text
    returns a directory with one of 3 values
    "success" : boolean saying API request was successful or not
    "error": none if no errors otherwise a string containing the error
    "transcription": none if speech could not be transcribed else a string
    """

    # check that recognizer and microphone are appropriate types
    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("microphone object must be of sr.Microphone")

    # we adjust ambient sensitivity to ambient noise
    # then we record from microphone and save as var audio
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    # setting up response object
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    # try recognizing the speech in the recoding (audio)
    # if a RequestError or unknown value error exception is caught,
    #   update the response object
    try:
        response["transcription"] = recognizer.recognize_google(audio)
    except sr.RequestError:
        # API was unreachable or unresponsive
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        # speech was untranslatable
        response["error"] = "Unable to recognize speech"

    return response


def text_to_speech(text):
    # take text and turn it into speech
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


if __name__ == '__main__':

    # create recognizer and mic instances
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    print("speech to text")

    while True:
        speech = speech_from_mic(recognizer, microphone)

        # if error print error and shutdown
        if speech["error"]:
            print("ERROR: {}".format(speech["error"]))
            # if error is because speech is untranslatable tell user and carry on
            if speech["error"] == "Unable to recognize speech":
                print("I don't understand")
            else:
                break

        # if user says stop stop the program
        elif "i need help" in speech["transcription"].lower():
            text_to_speech("What's wrong?")

        else:
            print("You said: {}".format(speech["transcription"]))
            text_to_speech(speech["transcription"])
