from kivy.clock import mainthread
from kivy.metrics import dp
from kivy.graphics import Line, Color, Rectangle
from kivy.factory import Factory as F
from kivy.app import App
from kivy.clock import Clock

from pyzbar import pyzbar
from pyzbar.pyzbar import ZBarSymbol
from gestures4kivy import CommonGestures

from PIL import Image

from camera4kivy import Preview
from screens.qrreaderhelper_screen import QRReaderHelperScreen, show_toast
from screens.gallery_screen import writeJsonFile, readJsonFile

from functools import partial
from security import AES_Encrypt
import os


class QRReader(QRReaderHelperScreen, Preview, CommonGestures):
    app = App.get_running_app()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_enter(self):
        print("Initializing connect_camera em 1.5 segundos")
        Clock.schedule_once(partial(self.connect_camera, 640, True), 1.5)
        self.number_of_image_analyzed = 0
        self.define_real_path()

    def define_real_path(self):
        from android.storage import primary_external_storage_path
        import datetime

        current_date = datetime.datetime.now().strftime("%Y_%m_%d")

        sandboxed_gallery_folder = (
            primary_external_storage_path() + "/DCIM/Sandboxed Gallery"
        )
        images_folder_name = [
            i
            for i in os.listdir(sandboxed_gallery_folder)
            if i.startswith(current_date)
        ]
        if not images_folder_name:
            os.mkdir(os.path.join(sandboxed_gallery_folder, current_date))
            images_folder_name = current_date
        else:
            images_folder_name = images_folder_name[0]

        real_path = os.path.join(
            sandboxed_gallery_folder,
            images_folder_name,
        )
        self.real_path = real_path

        print("real_path: ", real_path)
        print("os.listdir(real_path): ", os.listdir(real_path))

    def print_images(self, message=""):
        if self.number_of_image_analyzed % 5:
            print(
                os.listdir(self.real_path),
                " ",
                message,
                self.number_of_image_analyzed,
            )

    def on_leave(self):
        print("Leaving screen, disconnecting camera")
        self.disconnect_camera()

    ####################################
    # Analyze a Frame - NOT on UI Thread
    ####################################

    def analyze_pixels_callback(self, pixels, image_size, image_pos, scale, mirror):
        # pixels : Kivy Texture pixels
        # image_size   : pixels size (w,h)
        # image_pos    : location of Texture in Preview Widget (letterbox)
        # scale  : scale from Analysis resolution to Preview resolution
        # mirror : true if Preview is mirrored

        self.number_of_image_analyzed += 1

        if self.number_of_image_analyzed >= 30:
            if self.app.should_take_photo_now:
                self.capture_photo()
                self.app.should_take_photo_now = False
                self.number_of_image_analyzed = 0
                Clock.schedule_once(self.load_photo, 2)
            else:
                if self.number_of_image_analyzed % 10 == 0:
                    print("Frame: ", self.number_of_image_analyzed)

    def load_photo(self, *args):
        print("Loading photo")
        from android.permissions import (
            request_permissions,
            check_permission,
            Permission,
        )

        if check_permission(Permission.WRITE_EXTERNAL_STORAGE):
            from jnius import autoclass

            # Environment = autoclass("android.os.Environment")
            # path = Environment.getExternalStorageDirectory().getAbsolutePath()
            # path += os.path.sep + "Sandboxed Gallery/"
            # print("path: ", path)
            # print("os.listdir(path): ", os.listdir(path))
            images_names = os.listdir(self.real_path)
            if len(images_names) > 1:
                print("#" * 100)
                print("ERRO: there are multiple images on folder: ", images_names)
            if images_names:
                image_name = images_names[-1]
                show_toast(f"Loading photo... {len(images_names)}")
            else:
                print("No images found on folder: ", self.real_path)
                show_toast("No images found")
                return

            print("image found: ", image_name)
            image_path = os.path.join(self.real_path, image_name)

            with open(image_path, "rb") as f:
                image_data = f.read()

            # encrypt the image
            encrypted_image = AES_Encrypt(self.app.key, image_data)

            if os.path.exists("images"):
                writeJsonFile("images", image_name + ".json", encrypted_image)
                show_toast("Encryption finished")

            else:
                os.mkdir("images")
                writeJsonFile("images", image_name + ".json", encrypted_image)
                show_toast("Encryption finished")

            Clock.schedule_once(self.delete_all_photos, 4)
            Clock.schedule_once(self.change_to_gallery_screen, 1)

    @mainthread
    def change_to_gallery_screen(self, *args):
        self.app.change_screen("Gallery Screen")

    # @mainthread
    def delete_all_photos(self, *args):
        self.print_images("before deletingggg")
        from android.storage import primary_external_storage_path

        # delete all images inside real_path
        for image in os.listdir(self.real_path):

            show_toast(f"Deleting photo... {image}")
            os.remove(os.path.join(self.real_path, image))

    @mainthread
    def make_thread_safe(self, *args):
        show_toast("actually taking photo")

    ################################
    # Annotate Screen - on UI Thread
    ################################

    def canvas_instructions_callback(self, texture, tex_size, tex_pos, boolean=True):
        ...

    #################################
    # User Touch Event - on UI Thread
    #################################

    def cg_long_press(self, touch, x, y):
        self.open_browser(x, y)

    def cg_double_tap(self, touch, x, y):
        self.open_browser(x, y)
