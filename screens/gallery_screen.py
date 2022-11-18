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

# kivy is already loaded as per: https://stackoverflow.com/a/59011183/16355112
# print("Cgit

kv_path = os.getcwd() + "/screens/gallery_screen.kv"
if kv_path not in Builder.files:
    Builder.load_file("screens/gallery_screen.kv")

class GalleryScreen(F.Screen):
    app = App.get_running_app()
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
        print("sel;f", self)
        if is_selected:
            print("selection changed to {0}".format(rv.data[index]))
        else:
            print("selection removed for {0}".format(rv.data[index]))

    def on_release(self):
        print("WHO WAS PRESSED", self.text)
        app = App.get_running_app()
        sm = app.root_screen.screen_manager
        app.change_screen("ImageViewer Screen")
        image_screen = sm.get_screen("ImageViewer Screen")
        image_screen.file_name = self.text


class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)

        # self.data = []
        if os.path.isfile("index.json"):
            read_data = readJsonFile(".", "index.json")
            print("wtf is read_data", read_data)
            # self.data = [{"text": read_data[x]} for x in read_data.keys()]
            self.data = [read_data[x] for x in read_data.keys()]
            print("datata", self.data)

            # self.data = []  # WORKS
            # self.data = [{"1"}]
            # print("self.data??", self.data)
            # print("what is self.data?", type(self.data), list(self.data))
            # self.data = F.ListProperty(readJsonFile(".", "index.json"))
        else:
            self.data = []
        # self.data = F.ListProperty([])
