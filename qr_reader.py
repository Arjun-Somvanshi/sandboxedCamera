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

class QRReader(Preview, CommonGestures, F.Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.annotations = []
        self.qr_code_anterior = {}
        self.qr_code_atual = {}

    # def on_pre_enter(self):
        # print('limpando widgets?')
        # self.clear_widgets()
        # print('widgets limpados')
        # print('limpando canvas')
        # self.canvas.clear()
        # print('canvas limpado')


    def on_enter(self):
        print('entrando na tela do qr reader!!!!<<<<')
        print('iniciando connect camera')
        from functools import partial
        print('iniciando connect_camera em 2 segundos')


        Clock.schedule_once(partial(self.connect_camera, 640, True), .5)
        # self.connect_camera(analyze_pixels_resolution = 640, 
        # enable_analyze_pixels = True)

        print('Nenhuma imagem analisada')
        self.numero_da_imagem_analisada = 0

    def on_leave(self):
        print('saindo da tela, forçando desconectar câmera')
        self.disconnect_camera()

        

    # def on_leave(self):
    #     print('desconectando câmera')
    #     self.disconnect_camera()

    ####################################
    # Analyze a Frame - NOT on UI Thread
    ####################################
    
    def analyze_pixels_callback(self, pixels, image_size, image_pos, scale, mirror):
        # pixels : Kivy Texture pixels
        # image_size   : pixels size (w,h)
        # image_pos    : location of Texture in Preview Widget (letterbox)
        # scale  : scale from Analysis resolution to Preview resolution
        # mirror : true if Preview is mirrored

        self.numero_da_imagem_analisada += 1
        print('Número da imagem analisada: ', self.numero_da_imagem_analisada)

        if self.numero_da_imagem_analisada >= 30:
            # print('AGORA SIM vamos procurar por Qr codes')
            pil_image = Image.frombytes(mode='RGBA', size=image_size, data= pixels)
            barcodes = pyzbar.decode(pil_image, symbols=[ZBarSymbol.QRCODE])
            found = []
            for barcode in barcodes:
                text = barcode.data.decode('utf-8')

                x, y, w, h = barcode.rect
                # Map Zbar coordinates to Kivy coordinates
                y = max(image_size[1] -y -h, 0)
                # Map Analysis coordinates to Preview coordinates
                if mirror:
                    x = max(image_size[0] -x -w, 0)
                x = round(x * scale + image_pos[0])
                y = round(y * scale + image_pos[1])
                w = round(w * scale)
                h = round(h * scale)

                qr_code_encontrado = {'x':x, 'y':y, 'w':w, 'h':h, 't':text}
                found.append(qr_code_encontrado)
                self.qr_code_atual = qr_code_encontrado
                break

                
            self.make_thread_safe(list(found)) ## A COPY of the list

            


    @mainthread
    def make_thread_safe(self, found):
        self.annotations = found
        print('Qr code anterior: ', self.qr_code_anterior)
        print('Qr code atual: ', self.qr_code_atual)
        
        if found:
            if self.qr_code_atual != self.qr_code_anterior:
                self.disconnect_camera()
                print('Os qr codes são diferentes')
                print('desconectando câmera')

                print('encontrei qr code!!!!!')
                print('Número de qr codes encontrados: ', len(found))
                print('texto no qr code: ', found[0]['t'])
                print('voltando pra Registrar Balaios Screen')
                screen_manager = App.get_running_app().screen_manager
                screen_manager.current = 'Registrar Balaios Screen'

                print('executando fill worker and group')
                screen_manager.get_screen('Registrar Balaios Screen').fill_worker_and_group(found[0]["t"])
                
                # worker_name = f'Nome do funcionário: \n{found[0]["t"]}'
                self.numero_da_imagem_analisada = 0
                self.qr_code_anterior = self.qr_code_atual

                self.canvas_instructions_callback('a', 'b', 'c', boolean=True)
            else:
                print('Aparentemente é o mesmo QR code')
                print('não vou fazer nada')

    ################################
    # Annotate Screen - on UI Thread
    ################################
        
    def canvas_instructions_callback(self, texture, tex_size, tex_pos, boolean=True):
        # Add the analysis annotations

        # print('algo acontecendo no canvas')
        # print('argumentos texture, tex_size, tex_pos')
        # print(texture, tex_size, tex_pos)
        Color(1,0,0,1)
        for r in self.annotations:
            Line(rectangle=(r['x'], r['y'], r['w'], r['h']), width = dp(2))

        if boolean:
            print('será q eh esse o ultimo canvas call back? %%%%')
            Color(1,1,1,1)
            Rectangle(size=(1080, 1920), pos=[1080.0, 124])

    #################################
    # User Touch Event - on UI Thread
    #################################

    def cg_long_press(self, touch, x, y):
        self.open_browser(x, y)

    def cg_double_tap(self, touch, x, y):
        self.open_browser(x, y)

    def open_browser(self, x, y):
        for r in self.annotations:
            if x >= r['x'] and x <= r['x'] + r['w'] and\
               y >= r['y'] and y <= r['y'] + r['h']:
                webbrowser.open_new_tab(r['t'])
