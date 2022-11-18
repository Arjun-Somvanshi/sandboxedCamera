import webbrowser
from kivy.clock import mainthread
from kivy.metrics import dp
from kivy.graphics import Line, Color, Rectangle

from pyzbar import pyzbar
from pyzbar.pyzbar import ZBarSymbol
from PIL import Image

from gestures4kivy import CommonGestures
from camera4kivy import Preview
from kivy.factory import Factory as F
from kivy.app import App
from kivy.clock import Clock
from screens.qrreaderhelper_screen import QRReaderHelperScreen

import os


class QRReader(QRReaderHelperScreen, Preview, CommonGestures):
    app = App.get_running_app()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.annotations = []
        self.qr_code_anterior = {}
        self.qr_code_atual = {}

    # def capture_photo(self, location=".", subdir="", name=""):
    #     if self.preview._camera and self.preview._camera.texture:
    #         print(os.getcwd())
    #         images_folder = os.path.join(os.getcwd(), "images")
    #         if os.path.exists(images_folder) == False:
    #             os.mkdir(images_folder)
    #         else:
    #             print("pasta images já existe")
    #             tex = self.preview._camera.texture.get_region(*self.tex_crop)
    #             print("tex_crop: ", self.tex_crop)
    #             # tex.save(path, flipped = False)

    #         # path = self.capture_path(location, subdir, name)
    #         # if self.callback:
    #         #     self.callback(path)

    # def on_pre_enter(self):
    # print('limpando widgets?')
    # self.clear_widgets()
    # print('widgets limpados')
    # print('limpando canvas')
    # self.canvas.clear()
    # print('canvas limpado')

    def on_enter(self):
        print("entrando na tela do qr reader!!!!<<<<")
        print("iniciando connect camera")
        from functools import partial

        print("iniciando connect_camera em 2 segundos")

        Clock.schedule_once(partial(self.connect_camera, 640, True), 1.5)
        # self.connect_camera(analyze_pixels_resolution = 640,
        # enable_analyze_pixels = True)

        print("Nenhuma imagem analisada")
        self.numero_da_imagem_analisada = 0

        from android.storage import primary_external_storage_path

        sandboxed_gallery_folder = (
            primary_external_storage_path() + "/DCIM/Sandboxed Gallery"
        )
        images_folder_name = os.listdir(sandboxed_gallery_folder)[0]
        real_path = os.path.join(
            sandboxed_gallery_folder,
            images_folder_name,
        )
        self.real_path = real_path

        print(os.listdir(self.real_path))

    def on_leave(self):
        print("saindo da tela, forçando desconectar câmera")
        print(os.listdir(self.real_path))
        self.disconnect_camera()
        print(os.listdir(self.real_path))

    # def on_leave(self):
    #     print('desconectando câmera')
    #     self.disconnect_camera()

    ####################################
    # Analyze a Frame - NOT on UI Thread
    ####################################

    def check_if_photo_is_on_folder(self):
        print(os.listdir(self.real_path))
        from android.storage import primary_external_storage_path

        sandboxed_gallery_folder = (
            primary_external_storage_path() + "/DCIM/Sandboxed Gallery"
        )
        if os.path.exists(sandboxed_gallery_folder):
            images_folder_name = os.listdir(sandboxed_gallery_folder)[0]
            real_path = os.path.join(
                sandboxed_gallery_folder,
                images_folder_name,
            )
            images_names = os.listdir(real_path)
            if len(images_names) > 0:
                print(os.listdir(self.real_path))
                return True
            else:
                print(os.listdir(self.real_path))
                return False

    def analyze_pixels_callback(self, pixels, image_size, image_pos, scale, mirror):
        # pixels : Kivy Texture pixels
        # image_size   : pixels size (w,h)
        # image_pos    : location of Texture in Preview Widget (letterbox)
        # scale  : scale from Analysis resolution to Preview resolution
        # mirror : true if Preview is mirrored

        self.numero_da_imagem_analisada += 1
        print(os.listdir(self.real_path))
        print("Número da imagem analisada: ", self.numero_da_imagem_analisada)
        print(os.listdir(self.real_path))

        if self.numero_da_imagem_analisada >= 30:
            if self.app.should_take_photo_now:

                print(os.listdir(self.real_path), "before delete")
                self.delete_all_photos()
                print(os.listdir(self.real_path), "after delete")
                # while not self.check_if_photo_is_on_folder:
                message = "taking photo now"
                self.make_thread_safe(message)

                print(os.listdir(self.real_path), "before take photo")
                self.capture_photo()
                print(os.listdir(self.real_path), "after take photo")

                message = "photo taken"
                self.make_thread_safe(message)

                self.make_thread_safe("photo on folder")
                self.app.should_take_photo_now = False
                self.numero_da_imagem_analisada = 0

                self.load_photo_from_qr_helper()
            return
            # print('AGORA SIM vamos procurar por Qr codes')
            pil_image = Image.frombytes(mode="RGBA", size=image_size, data=pixels)
            barcodes = pyzbar.decode(pil_image, symbols=[ZBarSymbol.QRCODE])
            found = []
            for barcode in barcodes:
                text = barcode.data.decode("utf-8")

                x, y, w, h = barcode.rect
                # Map Zbar coordinates to Kivy coordinates
                y = max(image_size[1] - y - h, 0)
                # Map Analysis coordinates to Preview coordinates
                if mirror:
                    x = max(image_size[0] - x - w, 0)
                x = round(x * scale + image_pos[0])
                y = round(y * scale + image_pos[1])
                w = round(w * scale)
                h = round(h * scale)

                qr_code_encontrado = {"x": x, "y": y, "w": w, "h": h, "t": text}
                found.append(qr_code_encontrado)
                self.qr_code_atual = qr_code_encontrado
                break

            self.make_thread_safe(list(found))  ## A COPY of the list

    # @mainthread
    def load_photo_from_qr_helper(self, *args):
        # qrhelper_screen = self.app.screen_manager.get_screen("QRReaderHelper Screen")
        self.load_photo2()

    # @mainthread
    def load_photo2(self):
        from screens.qrreaderhelper_screen import show_toast

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
                if len(images_names) != 1:
                    print("#" * 100)
                    print("ERRO: não tem apenas uma imagem na pasta")
                if images_names:
                    image_name = images_names[-1]
                    show_toast(f"Loading photo... {len(images_names)}")
                else:
                    print("No images found on folder: ", real_path)
                    show_toast("No images found")
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
                    show_toast("encryption finished")

                else:
                    print("images folder does not exist")
                    os.mkdir("images")
                    writeJsonFile("images", image_name + ".json", encrypted_image)
                    show_toast("encryption finished aaa")

                Clock.schedule_once(self.delete_all_photos, 4)
                Clock.schedule_once(self.change_to_gallery_screen, 1)

    @mainthread
    def change_to_gallery_screen(self, *args):
        self.app.change_screen("Gallery Screen")

    # @mainthread
    def delete_all_photos(self, *args):
        print(os.listdir(self.real_path), "before deletingggg")
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
                from screens.qrreaderhelper_screen import show_toast

                show_toast(f"Deleting photo... {image}")
                os.remove(os.path.join(real_path, image))

            print(os.listdir(self.real_path), "afterrr deletingggg")

    @mainthread
    def make_thread_safe(self, *args):

        from screens.qrreaderhelper_screen import show_toast

        show_toast("actually taking foto")
        return
        self.annotations = found
        print("Qr code anterior: ", self.qr_code_anterior)
        print("Qr code atual: ", self.qr_code_atual)

        if found:
            if self.qr_code_atual != self.qr_code_anterior:
                self.disconnect_camera()
                print("Os qr codes são diferentes")
                print("desconectando câmera")

                print("encontrei qr code!!!!!")
                print("Número de qr codes encontrados: ", len(found))
                print("texto no qr code: ", found[0]["t"])
                print("voltando pra Registrar Balaios Screen")
                screen_manager = App.get_running_app().screen_manager
                screen_manager.current = "Registrar Balaios Screen"

                print("executando fill worker and group")
                screen_manager.get_screen(
                    "Registrar Balaios Screen"
                ).fill_worker_and_group(found[0]["t"])

                # worker_name = f'Nome do funcionário: \n{found[0]["t"]}'
                self.numero_da_imagem_analisada = 0
                self.qr_code_anterior = self.qr_code_atual

                self.canvas_instructions_callback("a", "b", "c", boolean=True)
            else:
                print("Aparentemente é o mesmo QR code")
                print("não vou fazer nada")

    ################################
    # Annotate Screen - on UI Thread
    ################################

    def canvas_instructions_callback(self, texture, tex_size, tex_pos, boolean=True):
        ...
        # Add the analysis annotations

        # print('algo acontecendo no canvas')
        # print('argumentos texture, tex_size, tex_pos')
        # print(texture, tex_size, tex_pos)
        # Color(1, 0, 0, 1)
        # for r in self.annotations:
        #     Line(rectangle=(r["x"], r["y"], r["w"], r["h"]), width=dp(2))

        # if boolean:
        #     print("será q eh esse o ultimo canvas call back? %%%%")
        #     Color(1, 1, 1, 1)
        #     Rectangle(size=(1080, 1920), pos=[1080.0, 124])

    #################################
    # User Touch Event - on UI Thread
    #################################

    def cg_long_press(self, touch, x, y):
        self.open_browser(x, y)

    def cg_double_tap(self, touch, x, y):
        self.open_browser(x, y)

    def open_browser(self, x, y):
        for r in self.annotations:
            if (
                x >= r["x"]
                and x <= r["x"] + r["w"]
                and y >= r["y"]
                and y <= r["y"] + r["h"]
            ):
                webbrowser.open_new_tab(r["t"])
