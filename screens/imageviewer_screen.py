from kivy.factory import Factory as F
from kivy.properties import StringProperty
import os
from screens.main_screen import readJsonFile
from security import AES_Decrypt
from kivy.app import App
from kivy.lang import Builder

kv_path = os.getcwd() + "/screens/imageviewer_screen.kv"
if kv_path not in Builder.files:
    Builder.load_file("screens/imageviewer_screen.kv")


class ImageViewerScreen(F.Screen):
    file_name = StringProperty("")
    app = App.get_running_app()

    def on_enter(self):
        print("Entered image viewer screen")
        print(self.file_name)

        # build the image from the encrypted file
        self.decrypt_image(self.file_name)

    def on_pre_leave(self):
        print("Left image viewer screen")
        # delete the decrypted image
        decrypted_image_path = os.path.join(
            os.getcwd(), "images", self.file_name + ".decrypted"
        )
        if os.path.isfile(decrypted_image_path):
            os.remove(decrypted_image_path)

    def decrypt_image(self, encrypted_image_name):
        encrypted_image_path = os.path.join(os.getcwd(), "images", encrypted_image_name)

        image_data = readJsonFile("images", encrypted_image_name)

        # decrypt the image
        decrypted_image = AES_Decrypt(self.app.key, image_data)

        # save the decrypted image
        decrypted_image_path = os.path.join(
            os.getcwd(), "images", encrypted_image_name + ".decrypted"
        )

        with open(decrypted_image_path, "wb") as f:
            f.write(decrypted_image)

        # load the decrypted image
        self.image.source = decrypted_image_path
