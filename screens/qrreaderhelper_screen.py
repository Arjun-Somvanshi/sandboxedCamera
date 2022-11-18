from kivy.lang import Builder
from kivy.factory import Factory as F
from kivy.utils import platform
from kivy.clock import Clock
import os

from kivy.app import App


kv_path = os.getcwd() + "/screens/qrreaderhelper_screen.kv"
if kv_path not in Builder.files:
    Builder.load_file("screens/qrreaderhelper_screen.kv")


class QRReaderHelperScreen(F.Screen):
    app = App.get_running_app()

    def take_photo(self):
        # delete all photos inside the folder
        # Clock.schedule_once(self.delete_all_photos)

        print("Taking photo")
        qr_screen = self.app.screen_manager.get_screen("QR Screen")
        qr_screen.capture_photo()

        # load the photo taken
        self.load_photo()

        # change screen to gallery screen
        Clock.schedule_once(self.change_to_gallery_screen, 5)

        # # delete the photo taken
        # self.delete_all_photos()

    def change_to_gallery_screen(self, *args):
        self.app.change_screen("Gallery Screen")

    def delete_all_photos(self, *args):
        from android.storage import primary_external_storage_path

        sandboxed_gallery_folder = (
            primary_external_storage_path() + "/DCIM/Sandboxed Gallery"
        )
        if os.path.exists(sandboxed_gallery_folder):
            # get the first item of the file inside os.listdir this folder
            images_folder_name = os.listdir(sandboxed_gallery_folder)[0]
            real_path = os.path.join(
                sandboxed_gallery_folder,
                images_folder_name,
            )
            print("real_path: ", real_path)
            print("os.listdir(real_path): ", os.listdir(real_path))

            # delete all images inside real_path
            for image in os.listdir(real_path):
                os.remove(os.path.join(real_path, image))

    def load_photo(self):
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
            from android.storage import primary_external_storage_path

            # real_path = os.path.join(
            #     primary_external_storage_path(), self.app.image_path
            # )

            sandboxed_gallery_folder = (
                primary_external_storage_path() + "/DCIM/Sandboxed Gallery"
            )
            if os.path.exists(sandboxed_gallery_folder):
                # get the first item of the file inside os.listdir this folder
                images_folder_name = os.listdir(sandboxed_gallery_folder)[0]
                real_path = os.path.join(
                    sandboxed_gallery_folder,
                    images_folder_name,
                )
                print("real_path: ", real_path)
                print("os.listdir(real_path): ", os.listdir(real_path))

                # get the last photo in this folder
                images_names = os.listdir(real_path)
                if images_names:
                    image_name = images_names[-1]
                else:
                    print("No images found on folder: ", real_path)
                    return

                print("image found: ", image_name)
                image_path = os.path.join(real_path, image_name)

                # open the image
                with open(image_path, "rb") as f:
                    image_data = f.read()

                from security import AES_Encrypt

                # encrypt the image
                encrypted_image = AES_Encrypt(self.app.key, image_data)

                # from icecream import ic

                # ic(encrypted_image)

                from screens.gallery_screen import writeJsonFile, readJsonFile

                if os.path.exists("images"):
                    print("images folder exists")
                    writeJsonFile("images", image_name + ".json", encrypted_image)

                else:
                    print("images folder does not exist")
                    os.mkdir("images")
                    writeJsonFile("images", image_name + ".json", encrypted_image)

            # print(
            #     "os.listdir(primary_external_storage_path() + '/DCIM/Sandboxed Gallery'): ",
            #     os.listdir(primary_external_storage_path() + "/DCIM/Sandboxed Gallery"),
            # )

            # print("os.listdir(self.app.image_path): ", os.listdir(self.app.image_path))
            # print(
            #     "os.listdir(primary_external_storage_path): ",
            #     os.listdir(primary_external_storage_path),
            # )
            # print("os.listdir(real_path): ", os.listdir(real_path))

            # # real_path = os.path.join("/storage/emulated/0", self.app.image_path)
            # if os.path.exists(real_path):
            #     print(real_path, ": image path exists")
            #     # load the image
            #     # self.ids.image.source = self.app.image_path
            #     # self.ids.image.reload()
            # else:
            #     print(real_path, "image path does not exist")

            # # log("PATH", app.path)

        # from screens.gallery_screen import encrypt_image
        # import os

        # print("encrypting image")

        # full_name = os.path.join(subdir, name)
        # encrypt_image(full_name)

        # # delete the file
        # print("deleting the file")
        # os.remove(full_name)

        # from kivy.app import App

        # app = App.get_running_app()
        # app.change_screen("Gallery Screen")
