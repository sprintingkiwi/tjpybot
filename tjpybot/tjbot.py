from __future__ import print_function
import json
from os.path import join, dirname
from watson_developer_cloud import *
import speech_recognition as sr
from gtts import gTTS
import sys
import time
import os
import subprocess as sp
from utils import *

try:
    import RPi.GPIO as GPIO
except:
    print("Not on Raspberry")


class TJBot:

    def __init__(self):

        self.config = json.load(open("/home/pi/.tjbot-asphi/tjbot_config.json"))
        print(self.config)

        # Audio device MAC address
        #self.audioMAC = str(open("/home/pi/.tjbot-asphi/audiodev_macaddress").readlines()[0])
        #print(self.audioMAC)

        ####################################################
        # INITIALIZE Speech to Text
        ####################################################
        self.recognizer = sr.Recognizer()

        ####################################################
        # INITIALIZE WATSON TTS
        ####################################################
        self.text_to_speech = TextToSpeechV1(
            username=self.config["text to speech"]["username"],
            password=self.config["text to speech"]["password"],
            x_watson_learning_opt_out=False)  # Optional flag
        # print(json.dumps(text_to_speech.voices(), indent=2))

        ####################################################
        # INITIALIZE TONE ANALYZER
        ####################################################
        self.tone_analyzer = ToneAnalyzerV3(
            username=self.config["tone analyzer"]["username"],
            password=self.config["tone analyzer"]["password"],
            version="2017-09-26")

        ####################################################
        # INITIALIZE LANGUAGE TRANSLATOR
        ####################################################
        self.language_translator = LanguageTranslatorV2(
            username=self.config["language translator"]["username"],
            password=self.config["language translator"]["password"])

        ####################################################
        # INITIALIZE CONVERSATION
        ####################################################
        self.conversation = ConversationV1(
            username=self.config["conversation"]["username"],
            password=self.config["conversation"]["password"],
            version="2017-04-21")
        # response = conversation.message(workspace_id=workspace_id, input={"text": "What\"s the weather like?"})

        ####################################################
        # OTHER ATTRIBUTES
        ############################################################
        self.contexts = {}


    ############################################################
    # WATSON METHODS
    ############################################################
    def speak(self, text="prova", service="watson"):
        tagged = False
        options = []

        print(text)

        # Check for options command tags
        a = text.lower().split("tjbot(")
        if len(a) > 1:
            tagged = True
            options = a[1].replace(")", "").replace(" ", "").split(";")
            text = a[0]

        if service == "watson":
            if os.path.exists("tts_output.wav"):
                os.remove("tts_output.wav")
            audio_file = open(join(dirname(__file__), "tts_output.wav"), "wb")
            audio_file.write(self.text_to_speech.synthesize(text, accept="audio/wav", voice="it-IT_FrancescaVoice"))
            # os.system("cvlc --play-and-exit tts_output.wav")
            os.system("aplay -D bluealsa:HCI=hci0,DEV=" + self.config["audio device"] + ",PROFILE=a2dp tts_output.wav")
        elif service == "google":
            if os.path.exists("tts_output.mp3"):
                os.remove("tts_output.mp3")
            tts = gTTS(text=text, lang="it", slow=False)
            tts.save("tts_output.mp3")
            os.system("cvlc --play-and-exit tts_output.mp3")

        # Execute command tags
        print("Tag commands found: " + str(options))
        if tagged:
            for tag in options:
                if tag != "":
                    try:
                        getattr(self, tag)()
                    except:
                        print("Non-valid tag command received: " + tag)

    def analyze_tone(self, text):
        raw_tone = self.tone_analyzer.tone(tone_input=text,
                                           content_type="text/plain")
        tone = ""
        for t in raw_tone["document_tone"]["tones"]:
            tone += t["tone_name"] + ": " + str(t["score"]) + ", "
        return tone

    def translate(self, text, source="it", target="en"):
        return self.language_translator.translate(text, source=source, target=target)["translations"][0]["translation"]

    def converse(self, user_input, workspace):

        # Only for the first message of a new conversation
        if workspace not in self.contexts:
            self.contexts[workspace] = None

        answer = ""
        while answer == "":
            try:
                raw_answer = self.conversation.message(workspace_id=workspace,
                                                       input={"text": user_input},
                                                       context=self.contexts[workspace])
                # print(raw_answer)
                for a in raw_answer["output"]["text"]:
                    answer += a + ";"
                # answer = raw_answer["output"]["text"][0]
                self.contexts[workspace] = raw_answer["context"]
                # print(context)
            except IndexError:
                print("Conversation returned no text")

        return answer

    # for now done with google...
    def listen(self):
        # Record audio
        print("Dimmi qualcosa")
        rec = sp.Popen(["sox", "-t", "alsa", "plughw:1", "stt_input.wav", "silence", "1", "0.01", "3%", "1", "3.0", "3%"])
        waitchild(rec)

        # Understand words
        with sr.AudioFile("stt_input.wav") as source:
            audio = self.recognizer.record(source)
        try:
            user_input = str(self.recognizer.recognize_google(audio, language="it-IT")).lower()
            # user_input = raw_input()
        except:
            user_input = "..."

        print("User input: " + user_input)
        return user_input

    ############################################################
    # GPIO METHODS
    ############################################################
    def set_angle(self, angle):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(26, GPIO.OUT)
        pwm = GPIO.PWM(26, 50)
        pwm.start(0)

        duty = angle / 18 + 2
        GPIO.output(26, True)
        pwm.ChangeDutyCycle(duty)
        time.sleep(1)
        GPIO.output(26, False)
        pwm.ChangeDutyCycle(0)

        pwm.stop()
        GPIO.cleanup()

    ####################################################
    # TAGS FUNCTIONS
    ####################################################
    def stop(self):
        os.system("sudo poweroff")

    def reboot(self):
        os.system("reboot")

    def wave(self):
        print("Waving servo motor")
        self.set_angle(180)
        time.sleep(1)
        self.set_angle(90)
        time.sleep(1)
