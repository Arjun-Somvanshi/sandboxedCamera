from kivy.factory import Factory as F
from kivy.properties import StringProperty


class ImageViewerScreen(F.Screen):
    file_name = StringProperty("")
