from kivy.lang import Builder
from kivy.factory import Factory as F
from kivy.utils import platform
from kivy.clock import Clock
from kivy.app import App
import os

kv_path = os.getcwd() + "/screens/user_screen.kv"
if kv_path not in Builder.files:
    Builder.load_file("screens/user_screen.kv")

class UserScreen(F.Screen):
    def on_enter(self):
        print("Welcome to the user screen")