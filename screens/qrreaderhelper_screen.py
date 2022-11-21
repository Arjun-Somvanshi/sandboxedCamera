from kivy.lang import Builder
from kivy.factory import Factory as F
from kivy.utils import platform
import os

from kivy.app import App


kv_path = os.getcwd() + "/screens/qrreaderhelper_screen.kv"
if kv_path not in Builder.files:
    Builder.load_file("screens/qrreaderhelper_screen.kv")

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


class QRReaderHelperScreen(F.Screen):
    app = App.get_running_app()

    def take_photo(self):
        print("Taking photo")
        self.app.should_take_photo_now = True
