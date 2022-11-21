from kivy.lang import Builder
from kivy.factory import Factory as F
from kivy.utils import platform
from kivy.clock import Clock
import os
from pprint import pprint
from kivy.app import App
import json
from Crypto.Hash import SHA256
from security import kdf, make_salt

if platform == "android":
    from android.runnable import run_on_ui_thread
    from jnius import autoclass, cast

    Toast = autoclass("android.widget.Toast")
    String = autoclass("java.lang.String")
    CharSequence = autoclass("java.lang.CharSequence")
    PythonActivity = autoclass("org.kivy.android.PythonActivity")
    context = PythonActivity.mActivity

    @run_on_ui_thread
    def show_toast(text):
        t = Toast.makeText(
            context, cast(CharSequence, String(text)), Toast.LENGTH_SHORT
        )
        t.show()


kv_path = os.getcwd() + "/screens/main_screen.kv"
if kv_path not in Builder.files:
    Builder.load_file("screens/main_screen.kv")


def writeJsonFile(dir, fn, data):
    with open(dir + os.sep + fn, "w") as f:
        json.dump(data, f, indent=2)


def readJsonFile(dir, fn):
    with open(dir + os.sep + fn, "r") as f:
        data = json.load(f)
    return data


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
        try:
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
                writeJsonFile(".", "salt", {"salt": str(salt)})
                # generate key
                writeJsonFile(".", "creds", {"hash": hex})
                # change screen
                self.ids.sm.current = "Login Screen"
            else:
                print("You are not allowed")
        except Exception as e:
            print(e)
            if platform == "android":
                show_toast("Try again")

    def auth(self):
        try:
            with open("salt", "r") as f:
                salt = json.load(f)["salt"]
            print(salt)
            # set master key
            self.app.key = kdf(self.ids.passw.text, salt)
            print("key: ", self.app.key)
            print("type(key): ", type(self.app.key))
            hex1 = hashit(self.ids.password.text)
            hex2 = readJsonFile(".", "creds")["hash"]
            if hex1 == hex2:
                self.app.change_screen("Gallery Screen")
            else:
                print("Wrong Password")
        except Exception as e:
            print(e)
            if platform == "android":
                show_toast("Try again")
