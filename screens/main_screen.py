from kivy.lang import Builder
from kivy.factory import Factory as F
from kivy.utils import platform
from kivy.clock import Clock
import datetime
import calendar
import os
from pprint import pprint
from kivy.app import App
#from icecream import ic


def ic(*args, **kwargs):
    if platform != 'android':
        from icecream import ic
        return ic(*args, **kwargs)
    else:
        return None

kv_path = os.getcwd() + "/screens/main_screen.kv"
if kv_path not in Builder.files:
    Builder.load_file("screens/main_screen.kv")

month_to_mes = {
            "January": "Janeiro",
            "February": "Fevereiro",
            "March": "Março",
            "April": "Abril",
            "May": "Maio",
            "June": "Junho",
            "July": "Julho",
            "August": "Agosto",
            "September": "Setembro",
            "October": "Outubro",
            "November": "Novembro",
            "December": "Dezembro"
        }

class Calendar(F.BoxLayout):
    dias_do_mes = F.ListProperty([[0, 0, 1, 2, 3, 4, 5],
             [6, 7, 8, 9, 10, 11, 12],
             [13, 14, 15, 16, 17, 18, 19],
             [20, 21, 22, 23, 24, 25, 26],
             [27, 28, 29, 30, 0, 0, 0]])
    month_name = F.StringProperty()
    current_month_number = F.NumericProperty()
    current_year = F.NumericProperty()

    def update_to_previous_month(self):
        current_month_number = self.current_month_number - 1
        if current_month_number == 0:
            current_month_number = 12
            current_year = self.current_year - 1
        else:
            current_year = self.current_year

        month_name = month_to_mes[calendar.month_name[current_month_number]]
        dias_do_mes = calendar.monthcalendar(current_year, current_month_number)

        app = App.get_running_app()
        main_screen = app.screen_manager.get_screen("Main Screen")
        main_screen.data = [
            {
                "month_name": month_name,
                "dias_do_mes": dias_do_mes,
                "current_month_number": current_month_number,
                "current_year": current_year
            }
        ]

    def update_to_next_month(self):
        current_month_number = self.current_month_number + 1
        if current_month_number == 13:
            current_month_number = 1
            current_year = self.current_year + 1
        else:
            current_year = self.current_year

        month_name = month_to_mes[calendar.month_name[current_month_number]]
        dias_do_mes = calendar.monthcalendar(current_year, current_month_number)

        app = App.get_running_app()
        main_screen = app.screen_manager.get_screen("Main Screen")
        main_screen.data = [
            {
                "month_name": month_name,
                "dias_do_mes": dias_do_mes,
                "current_month_number": current_month_number,
                "current_year": current_year
            }
        ]

    def update_to_previous_year(self):
        current_year = self.current_year - 1
        month_name = month_to_mes[calendar.month_name[self.current_month_number]]
        dias_do_mes = calendar.monthcalendar(current_year, self.current_month_number)

        app = App.get_running_app()
        main_screen = app.screen_manager.get_screen("Main Screen")
        main_screen.data = [
            {
                "month_name": month_name,
                "dias_do_mes": dias_do_mes,
                "current_month_number": self.current_month_number,
                "current_year": current_year
            }
        ]

    def update_to_next_year(self):
        current_year = self.current_year + 1
        month_name = month_to_mes[calendar.month_name[self.current_month_number]]
        dias_do_mes = calendar.monthcalendar(current_year, self.current_month_number)

        app = App.get_running_app()
        main_screen = app.screen_manager.get_screen("Main Screen")
        main_screen.data = [
            {
                "month_name": month_name,
                "dias_do_mes": dias_do_mes,
                "current_month_number": self.current_month_number,
                "current_year": current_year
            }
        ]

    def update_calendar(self):
        self.month_name = month_to_mes[calendar.month_name[self.current_month_number]]
        self.dias_do_mes = calendar.monthcalendar(self.current_year, self.current_month_number)
        self.update_main_screen_data()

    def update_main_screen_data(self):
        app = App.get_running_app()
        main_screen = app.screen_manager.get_screen("Main Screen")
        main_screen.data = [
            {
                "dias_do_mes": self.dias_do_mes,
                "month_name": self.month_name,
                "current_month_number": self.current_month_number,
                "current_year": self.current_year
            }
        ]

class WorkerInfo(F.BoxLayout):
    dias_do_mes = F.ListProperty([[0, 0, 1, 2, 3, 4, 5],
             [6, 7, 8, 9, 10, 11, 12],
             [13, 14, 15, 16, 17, 18, 19],
             [20, 21, 22, 23, 24, 25, 26],
             [27, 28, 29, 30, 0, 0, 0]])
    month_name = F.StringProperty()
    current_month_number = F.NumericProperty()
    current_year = F.NumericProperty()

class MainScreen(F.Screen):
    data = F.ListProperty()
    colors = F.ListProperty()

    def on_enter(self):
        print('oi')
        current_date = datetime.date.today()
        self.current_month = current_date.month
        self.current_year = current_date.year
        self.month = calendar.monthcalendar(current_date.year, self.current_month)
        bg_color = (0.8,0.8,0.8,1)
        self.colors = [bg_color]*35

        month_to_mes = {
            "January": "Janeiro",
            "February": "Fevereiro",
            "March": "Março",
            "April": "Abril",
            "May": "Maio",
            "June": "Junho",
            "July": "Julho",
            "August": "Agosto",
            "September": "Setembro",
            "October": "Outubro",
            "November": "Novembro",
            "December": "Dezembro"
        }

        self.data.append(
            {
                "dias_do_mes": self.month,
                "month_name": month_to_mes[current_date.strftime("%B")],
                "current_month_number": current_date.month,
                "current_year": current_date.year
            }
        )

        # pprint(self.data)
        

        # ic(self.month)
        # print("MainScreen on_enter")
        # from pprint import pprint
        # pprint(os.listdir())
        # pprint(os.listdir("screens"))

        if platform == 'android':
            if "main.pyc" in os.listdir():
                os.remove("main.pyc")
                print('removed main.pyc')
        # print('Checking files in 3 seconds')
        # files = os.listdir()

        # from functools import partial
        # Clock.schedule_interval(partial(self.check_files, files), 3)

    # def check_files(self, files, dt):
    #     print('Checking files')
    #     if platform == 'android':
    #         print('Checking files: ', files)
        

        # if platform == 'android':
        #     files_to_remove = ["compile_app.pyc", "custom_reloader.pyc", "send_app_to_phone.pyc", "main.pyc", 'sitecustomize.pyc', "screens/main_screen.pyc"]
        #     for file in files_to_remove:
        #         if file in os.listdir():
        #             os.remove(file)
        
        #     folders_to_remove = ["__pycache__", "screens/__pycache__"]
        #     for folder in folders_to_remove:
        #         if folder in os.listdir():
        #             from shutil import rmtree
        #             rmtree(folder)

        #     # check files and folders
        #     from pprint import pprint
            
        #     pprint(os.listdir())
        #     pprint(os.listdir("screens"))

    def previous_month(self):
        """
        Updates the calendar to the previous month.
        """
        self.current_month -= 1
        if self.current_month == 0:
            self.current_month = 12
            self.current_year -= 1
        self.month = calendar.monthcalendar(self.current_year, self.current_month)
        
        print("Dias do mês: ", self.data[0]["dias_do_mes"])
        self.data[0]["dias_do_mes"] = self.month



    def next_month(self):
        pass
