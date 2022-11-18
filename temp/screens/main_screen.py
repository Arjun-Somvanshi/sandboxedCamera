from kivy.lang import Builder
from kivy.factory import Factory as F
from kivy.utils import platform
from kivy.clock import Clock
import datetime
import calendar
import os
from pprint import pprint
from kivy.app import App
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

class MainScreen(F.Screen):
    def set_entrypoint(self):
        if os.path.isfile("creds"):
            self.ids.sm.current = "Login Screen"
        else:
            self.ids.sm.current = "Signup Screen"
    