# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import speech_recognition as sr
import pyttsx3
import time
import json


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

    def to_json(self) -> str:
        return json.dumps(self, default=lambda x: x.__dict__)


patient2 = Patient("Miles Singleton", 1, 1, "Colitis", 1)


class Alarm:
    patient: Patient
    reason: str
    timeOfAlarm: time.localtime()
    timeOfAlarmOff: time.localtime()
    nurse: str

    def __init__(self, patient: Patient, reason: str):
        self.patient = patient
        self.reason = reason
        self.timeOfAlarm = time.localtime()

    def to_json(self) -> str:
        return json.dumps(self, default=lambda x: x.__dict__)


def speech_from_mic(audio_recognizer, usb_microphone):
    """takes speech from microphone turn to text
    returns a directory with one of 3 values
    "success" : boolean saying API request was successful or not
    "error": none if no errors otherwise a string containing the error
    "transcription": none if speech could not be transcribed else a string
    """

    # check that recognizer and microphone are appropriate types
    if not isinstance(audio_recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(usb_microphone, sr.Microphone):
        raise TypeError("microphone object must be of sr.Microphone")

    # we adjust ambient sensitivity to ambient noise
    # then we record from microphone and save as var audio
    with usb_microphone as source:
        audio_recognizer.adjust_for_ambient_noise(source)
        audio = audio_recognizer.listen(source)

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
        response["transcription"] = audio_recognizer.recognize_google(audio)
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


def call_nurse():
    reason = listen()
    if reason["error"]:
        text_to_speech("I don't understand could you repeat")
    else:
        text_to_speech("im calling a nurse")
        print(reason["transcription"])
        new_alarm = Alarm(patient2, reason["transcription"])
        print(new_alarm.to_json())
        return True


def listen():
    # create recognizer and mic instances
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    print("speech to text")

    return speech_from_mic(recognizer, microphone)


if __name__ == '__main__':

    speech = listen()
    # if error print error and shutdown
    if speech["error"]:
        print("ERROR: {}".format(speech["error"]))
        # if error is because speech is untranslatable tell user and carry on
        if speech["error"] == "Unable to recognize speech":
            print("I don't understand")
        else:
            pass

    elif "i need help" in speech["transcription"].lower():
        text_to_speech("What's wrong?")
        while True:
            if call_nurse():
                break

    else:
        print("You said: {}".format(speech["transcription"]))
        text_to_speech(speech["transcription"])
