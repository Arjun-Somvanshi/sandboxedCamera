from kivy.lang import Builder
from kivy.factory import Factory as F
from kivy.utils import platform
from kivy.clock import Clock
import os

from kivy.app import App

kv_path = os.getcwd() + "/screens/camera_screen.kv"
if kv_path not in Builder.files:
    Builder.load_file("screens/camera_screen.kv")


class CameraScreen(F.Screen):
    def on_enter(self):
        print("Entered camera screen")
        self.app = App.get_running_app()

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
