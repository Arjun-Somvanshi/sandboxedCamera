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
from security import kdf, make_salt

# from icecream import ic


def ic(*args, **kwargs):
    if platform != "android":
        from icecream import ic

        return ic(*args, **kwargs)
    else:
        return None


kv_path = os.getcwd() + "/screens/main_screen.kv"
if kv_path not in Builder.files:
    Builder.load_file("screens/main_screen.kv")

## File Handaling
def writeJsonFile(dir, fn, data):
    with open(dir + os.sep + fn, "w") as f:
        json.dump(data, f, indent=2)


def readJsonFile(dir, fn):
    with open(dir + os.sep + fn, "r") as f:
        data = json.load(f)
    return data


## Hashing


def hashit(passw):
    hash_object = SHA256.new(data=passw.encode("utf-8"))
    hex = hash_object.hexdigest()
    return hex


class MainScreen(F.Screen):
    app = App.get_running_app()

    def on_enter(self):
        print("Entered main screen")
        if platform == "android":
            from android.permissions import request_permissions, Permission

            request_permissions(
                [Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE]
            )

    def set_entrypoint(self):
        if os.path.isfile("creds"):
            self.ids.sm.current = "Login Screen"
        else:
            self.ids.sm.current = "Signup Screen"

    def save_auth(self):
        if (
            self.ids.passw.text == self.ids.repassw.text
            and len(self.ids.passw.text) > 8
        ):
            # save credentials
            passw = self.ids.passw.text
            hex = hashit(passw)
            # make salt
            salt = make_salt()
            print(salt)
            writeJsonFile(".", "salt", {"salt": salt.decode("utf-16")})
            # generate key
            writeJsonFile(".", "creds", {"hash": hex})
            # change screen
            self.ids.sm.current = "Login Screen"
        else:
            print("You are not allowed")

    def auth(self):
        # get salt
        salt = readJsonFile(".", "salt")["salt"].encode("utf-16")[2:]
        print(salt)
        # set master key
        self.app.key = kdf(self.ids.passw.text, salt)
        print(self.app.key)
        hex1 = hashit(self.ids.password.text)
        hex2 = readJsonFile(".", "creds")["hash"]
        if hex1 == hex2:
            self.app.change_screen("Gallery Screen")
        else:
            print("Wrong Password")
