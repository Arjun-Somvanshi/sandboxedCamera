from kivy.lang import Builder
from kivy.factory import Factory as F
from kivy.utils import platform
from kivy.clock import Clock
import datetime
import calendar
import os
from pprint import pprint
from kivy.app import App
import json
from Crypto.Hash import SHA256
#from icecream import ic


def ic(*args, **kwargs):
    if platform != 'android':
        from icecream import ic
        return ic(*args, **kwargs)
    else:
        return None

kv_path = os.getcwd() + "/screens/main_screen.kv"
if kv_path not in Builder.files:
    Builder.load_file("screens/main_screen.kv")

## File Handaling
def writeJsonFile(dir, fn, data):
    with open(dir+os.sep+fn, "w") as f:
        json.dump(fn, data, indent=2)

class MainScreen(F.Screen):
    def set_entrypoint(self):
        if os.path.isfile("creds"):
            self.ids.sm.current = "Login Screen"
        else:
            self.ids.sm.current = "Signup Screen"

    def save_auth(self):
        if self.ids.passw.text = self.ids.repassw.text and self.ids.passw > 8:
            # save credentials
            passw = self.ids.passw.text
            hash_object = SHA256.new(data=passw.encode("utf-8"))
            print(hash_object.digest())
            # generate key

            # change screen
            self.ids.sm.current = "Login Screen"
        else:
            print("You are not allowed")
    