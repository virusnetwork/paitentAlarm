# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import speech_recognition as sr
import pyttsx3
import time
import json
import requests

# to how webserver use command php -S localhost:8000 -t public/

alarm = False
bed_id = 1


class Alarm:
    # which room and bed is the voice assistant located in
    # used on sever side to get the patient
    bed_id = 1
    reason: str
    nurse: str

    def __init__(self, reason: str):
        self.bed_id = self.bed_id
        self.reason = reason

    def to_json(self) -> str:
        return json.dumps(self.__dict__)

    def send_new_alarm(self):
        st = 'http://localhost:8000/api/alarms/new'
        r = requests.post(st, self.to_json())
        print(r.status_code)


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


def play_radio():
    pass


def turn_off_alarm():
    if not alarm:
        text_to_speech("alarm not on")
        return
    else:
        text_to_speech("Please state your name")
        name = listen()
        data = {'bed_id': bed_id, 'nurse': name['transcript']}

        st = 'http://localhost:8000/api/alarms/new'
        r = requests.post(st, json.dumps(data))
        print(r.status_code)


def call_nurse():
    reason = listen()
    if reason["error"]:
        text_to_speech("I don't understand could you repeat")
    else:
        if simple_response(reason["transcription"]):
            play_radio()
        else:
            text_to_speech("im calling a nurse")
            print(reason["transcription"])
            new_alarm = Alarm(reason["transcription"])
            new_alarm.send_new_alarm()
        return True


def simple_response(transcript):
    if transcript == "what time is it" or transcript == "what is the time" or transcript == "time is it":
        text_to_speech("The time is {}".format(time.strftime("%H:%M", time.localtime())))
        return True
    elif transcript == "when is visiting hours":
        text_to_speech("Visiting hours are between 1 pm and 3 pm")
        return True
    else:
        return False


def listen():
    # create recognizer and mic instances
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    print("speech to text")

    return speech_from_mic(recognizer, microphone)


if __name__ == '__main__':
    while True:
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
            simple_response(speech["transcription"])
            print("You said: {}".format(speech["transcription"]))
