# -- coding: utf-8 --   

import json
from os.path import join, dirname
import sys
import time
import os
import subprocess as sp
import urllib3
import urllib


class TJBot:
    def __init__(self, ip):
        self.http = urllib3.PoolManager()
        self.socket = ip + ":3000"
        
    def request(self, elements):
        method = ""
        for e in elements:
            method += "/" + e
        path = self.socket + urllib.parse.quote(method)
        print("CONNECTING TO " + path)
        self.http.request("GET", path)
      
    def arm(self, angle):
        self.request(["arm", angle])
        
    def led(self, color):
        self.request(["led", color])
        
    def converse(self, user_input, workspace):
        return self.request(["converse", user_input, workspace])
        
    def set_volume(self, volume):
        self.request(["set-volume", volume])

    def speak(self, text="prova", voice="default", wait="true"):
        self.request(["speak", text, voice, wait])

    def listen(self, language):
        return self.request(["listen", language])

    def recognize(self, classifier="default", threshold="0.6"):
        return self.request(["vrec", classifier, threshold])
        
    def translate(self, text, source, target):
        return self.request(["translate", text, source, target])

    def analyze_tone(self, text):
        return self.request(["tone", text])
