import json
import time

import pyttsx3
import requests
import speech_recognition as sr

import main

# create function to change BED_ID


alarm = False
BED_ID = 1


class Alarm:
    """
    class for creating new alarm.
    alarm is sent to server to create a new alarm model
    """
    reason: str
    nurse: str

    def __init__(self, reason: str):
        """
        :param reason:
        """
        self.bed_id = BED_ID
        self.reason = reason

    def to_json(self) -> str:
        """

        :return:
        """
        return json.dumps(self.__dict__)

    def send_new_alarm(self):
        """

        :return:
        """
        st = 'http://localhost:8000/api/alarms/new'
        requests.post(st, {'bed_id': BED_ID, 'reason': self.reason})
        main.alarm = True


def listen():
    """
    sets up recognizer and microphone and call speech_from_mic
    :return: speech_from_mic dictionary with transcript
    """
    # create recognizer and mic instances
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    return speech_from_mic(recognizer, microphone)


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
        response["transcription"] = audio_recognizer.recognize_google(audio, language="en-GB")
    except sr.RequestError:
        # API was unreachable or unresponsive
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        # speech was untranslatable
        response["error"] = "Unable to recognize speech"

    return response


def text_to_speech(text):
    """
    takes a string and plays said string in speech
    :param text: string of what will be said
    :return: nothing
    """
    # take text and turn it into speech
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def turn_off_alarm():
    """
    Allows nurse to turn off alarm
    tells server to also turn off alarm
    :return: nothing
    """
    if not main.alarm:
        text_to_speech("alarm not on")
        return
    else:
        text_to_speech("Please state your name")
        name = listen()
        data = {'bed_id': BED_ID, 'nurse': name["transcription"]}

        st = 'http://localhost:8000/api/alarms/off'
        r = requests.post(st, data=json.dumps(data))
        if r.status_code == 200:
            main.alarm = False
            print("alarm off")


def call_nurse():
    """
    creates new alarm for calling a nurse
    tells server nurse is needed
    """
    reason = listen()
    if reason["error"]:
        text_to_speech("I don't understand could you repeat")
    else:
        if simple_response(reason["transcription"]):
            pass
        else:
            text_to_speech("im calling a nurse")
            print(reason["transcription"])
            new_alarm = Alarm(reason["transcription"])
            new_alarm.send_new_alarm()
        return True


def simple_response(transcript):
    """
    called by call_nurse().
    checks reason against pre defined questions
    will respond if possible else create an alarm
    :param transcript: string of what user said
    :return: True if function responded to question, else False create new alarm.
    """
    if transcript == "what time is it" or transcript == "what is the time" or transcript == "time is it":
        text_to_speech("The time is {}".format(time.strftime("%H:%M", time.localtime())))
        return True
    elif transcript == "when is visiting hours":
        text_to_speech("Visiting hours are between 1 pm and 3 pm")
        return True
    else:
        return False


if __name__ == '__main__':
    """
    Main function, constant loop listing for trigger word and responding to patient.
    """
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

        elif "i need help" in speech["transcription"].lower() or "i need a nurse" in speech["transcription"].lower():
            text_to_speech("What's wrong?")
            while True:
                if call_nurse():
                    break
        elif "turn off the alarm" in speech["transcription"].lower() or "turn off alarm" in speech["transcription"].lower():
            turn_off_alarm()

        else:
            simple_response(speech["transcription"])
            print("You said: {}".format(speech["transcription"]))
