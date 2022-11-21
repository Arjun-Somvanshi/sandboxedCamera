from kivy.lang import Builder
from kivy.utils import platform
from kivy.factory import Factory as F
import trio
import os

if platform != "android":
    from kivy.core.window import Window

    Window.size = (1312 * 0.306777, 2460 * 0.306777)
    Window._set_window_pos(1040, 100)


kv = Builder.load_string(
    """
<RootScreen>:
    screen_manager: screen_manager.__self__
    server_layout: server_layout.__self__
    server_icon: server_icon.__self__
    ScreenManager:
        id: screen_manager

    FloatLayout:
        id: server_layout
        opacity: 0
        Label:
            text: root.port_selected
            font_size: sp(18)
            pos: server_icon.right+dp(10),0
            color: 1,1,1,1
            size_hint: 1, None
            height: self.texture_size[1]
        
        Label:
            text: root.ip_selected
            font_size: sp(18)
            pos: server_icon.right+dp(10),server_icon.top
            color: 1,1,1,1
            size_hint: 1, None
            height: self.texture_size[1]
        
        Button:
            id: server_icon
            size_hint: None, None
            size: dp(50), dp(50)
            on_release: root.change_opacity(server_layout)
        Widget:
            
"""
)

from custom_reloader import BaseApp, App


class RootScreen(F.Screen):
    port_selected = F.StringProperty("Porta selecionada: 8035")
    ip_selected = F.StringProperty("IP:")

    def __init__(self):
        super().__init__()
        self.app = App.get_running_app()
        # print("initializing server")
        self.initialize_server()

    def initialize_server(self):
        if platform == "android":
            self.app.nursery.start_soon(self.start_async_server)
            self.server_layout.opacity = 0
        else:
            self.update_last_port_used()
            PORT = int(self.get_last_port_used()) + 1
            self.port_selected = f"Livestream ON\nPorta selecionada: {PORT}"
            self.server_layout.opacity = 0

    def get_last_port_used(self) -> int:
        last_port_used = open("configs/last_port_used", "r").read()
        # print("Última porta usada: ", last_port_used)
        return last_port_used

    def update_last_port_used(self) -> None:
        last_port_used = self.get_last_port_used()
        with open("configs/last_port_used", "w") as f:
            f.write(str(int(last_port_used) + 1))

    async def start_async_server(self):
        try:
            print("Before initializing")
            import socket

            print("imported socket")
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))

            self.ip_selected = f"IP: {s.getsockname()[0]}"
            PORT = int(self.get_last_port_used()) + 1
            self.update_last_port_used()
            self.port_selected = f"Livestream ON\nPorta selecionada: {PORT}"
            self.server_icon.text_color = 0, 0.7, 0, 1
            print("imported trio")
            print("running await trio.serve_tcp(self.data_receiver, PORT)")
            await trio.serve_tcp(self.data_receiver, PORT)
        except Exception as e:
            print("não foi posssível iniciar server")
            print(e)

    def change_opacity(self, layout):
        print("changing opacity of ", layout)
        if layout.opacity:
            layout.opacity = 0
        else:
            layout.opacity = 1

    async def data_receiver(self, data_stream):
        print("Server started")
        import shutil

        try:
            with open("app_copy.zip", "wb") as myzip:
                async for data in data_stream:
                    print(f"Server: received data")
                    print(f"Data type: {type(data)}, size {len(data)}")
                    print(f"Server: connection closed")
                    myzip.write(data)

            print("finished receiving all screens from client")
            print("unpacking app")
            shutil.unpack_archive("app_copy.zip")
            print("Updating last port used")
            self.update_last_port_used()

            print("App updated, exiting app for refresh")
            self.app.restart()
        except Exception as e:
            print(f"Server: crashed: {e!r}")


class MainApp(BaseApp):
    should_send_app_to_phone = True
    should_take_photo_now = False

    def __init__(self, nursery):
        super().__init__()
        self.nursery = nursery

    # def on_start(self):
    #     if platform == "android":
    #         if "main.pyc" in os.listdir():
    #             os.remove("main.pyc")
    #             print("removed main.pyc")

    def build_and_reload(self):
        self.root_screen = RootScreen()
        self.screen_manager = self.root_screen.screen_manager
        initial_screen = "Main Screen"
        self.change_screen(initial_screen)
        self.screen_manager.get_screen(initial_screen).set_entrypoint()
        return self.root_screen

    def change_screen(self, screen_name):
        if screen_name not in self.screen_manager.screen_names:
            screen_object = self.get_screen_object_from_screen_name(screen_name)
            self.screen_manager.add_widget(screen_object)

        self.screen_manager.current = screen_name

    def get_screen_object_from_screen_name(self, screen_name):
        # Parsing module 'my_screen.py' and object 'MyScreen' from screen_name 'My Screen'
        screen_module_in_str = "_".join([i.lower() for i in screen_name.split()])
        screen_object_in_str = "".join(screen_name.split())

        # Importing screen object
        exec(f"from screens.{screen_module_in_str} import {screen_object_in_str}")

        # Instantiating the object
        screen_object = eval(f"{screen_object_in_str}()")

        return screen_object

    def restart(self):
        print("Restarting the app on smartphone")
        from jnius import autoclass

        Intent = autoclass("android.content.Intent")
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        System = autoclass("java.lang.System")

        activity = PythonActivity.mActivity
        intent = Intent(activity.getApplicationContext(), PythonActivity)
        intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        intent.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TASK)
        activity.startActivity(intent)
        System.exit(0)


# Start kivy app as an asynchronous task
async def main() -> None:
    async with trio.open_nursery() as nursery:
        server = MainApp(nursery)
        await server.async_run("trio")
        nursery.cancel_scope.cancel()


try:
    trio.run(main)

except Exception as e:
    print(e)
    raise
