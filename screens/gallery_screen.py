from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivy.properties import BooleanProperty, ListProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.button import Button
from kivy.factory import Factory as F
from kivy.lang import Builder
import os
from .main_screen import readJsonFile
from kivy.app import App
from kivy.clock import Clock
from kivy.utils import platform

from security import AES_Encrypt, AES_Decrypt
from screens.main_screen import writeJsonFile, readJsonFile

# kivy is already loaded as per: https://stackoverflow.com/a/59011183/16355112
# print("Cgit

kv_path = os.getcwd() + "/screens/gallery_screen.kv"
if kv_path not in Builder.files:
    Builder.load_file("screens/gallery_screen.kv")


class GalleryScreen(F.Screen):
    app = App.get_running_app()
    data = F.ListProperty()

    def on_enter(self):
        print("Entered gallery screen")
        # load image names on self.data
        Clock.unschedule(self.load_images)
        Clock.schedule_interval(self.load_images, 1)

        # if "QR Screen" in self.app.screen_manager.screen_names:
        #     self.app.screen_manager.remove_widget(
        #         self.app.screen_manager.get_screen("QR Screen")
        #     )

    def load_images(self, *args):
        # print("Loading images")
        if os.path.exists("images"):
            # print("images folder exists")
            image_names = os.listdir("images")
            self.data = [
                {"text": image_name}
                for image_name in image_names
                if ".decrypted" not in image_name
            ]
        else:
            print("images folder does not exist")
            # create images folder
            os.mkdir("images")
            self.data = []

    def initialize_camera(self):
        print("Initializing camera")
        if platform == "android":
            if "qrreader" in self.__dict__:
                print("QR reader has already been created")
            else:
                print("Importing qrreader")
                from qr_reader import QRReader

                print("criando qr Reader widget")
                self.qrreader = QRReader(
                    letterbox_color="steelblue", aspect_ratio="16:9", name="QR Screen"
                )
                print("adicionando qr reader to screen manager")
                self.app.screen_manager.add_widget(self.qrreader)

            from android.permissions import (
                check_permission,
                request_permissions,
                Permission,
            )

            permission = check_permission(Permission.CAMERA)
            if permission:
                print("permissao ok, criando abrindo camera")
                self.connect_camera()
            else:
                print("permissão não concedida")
                request_permissions([Permission.CAMERA], self.connect_camera)
        else:
            self.app.change_screen("QRReaderHelper Screen")

    def encrypt_image(self, image_path):
        encrypted_image_name = f"{image_path.split('/')[-1].split('.')[0]}.json"

        # open the image
        with open(image_path, "rb") as f:
            image_data = f.read()

        # encrypt the image
        encrypted_image = AES_Encrypt(self.app.key, image_data)

        if os.path.exists("images"):
            print("images folder exists")
            writeJsonFile("images", encrypted_image_name, encrypted_image)

        else:
            print("images folder does not exist")
            os.mkdir("images")
            writeJsonFile("images", encrypted_image_name, encrypted_image)

    def connect_camera(self, *args):
        if platform == "android":
            from android.permissions import check_permission, Permission

            permission = check_permission(Permission.CAMERA)
            if permission:
                print("permissions are ok")
                Clock.schedule_once(self.change_to_qr_screen, 0.5)

    def change_to_qr_screen(self, *args):
        print("conectando câmera finalmente")
        print("mudando de screen para qr screen")
        self.app.screen_manager.current = "QR Screen"


class SelectableRecycleBoxLayout(
    LayoutSelectionBehavior, FocusBehavior, RecycleBoxLayout
):
    """Adds selection and focus behaviour to the view."""

    pass


class SelectableLabel(RecycleDataViewBehavior, Button):
    # """Add selection support to the Label"""

    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        """Catch and handle the view changes"""
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        """Add selection on touch down"""
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        """Respond to the selection of items in the view."""
        self.selected = is_selected

    def on_release(self):
        print("WHO WAS PRESSED", self.text)
        app = App.get_running_app()
        sm = app.root_screen.screen_manager
        app.change_screen("ImageViewer Screen")
        image_screen = sm.get_screen("ImageViewer Screen")
        image_screen.file_name = self.text
