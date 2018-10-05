# System imports
import os
from pathlib import Path
from threading import Thread

# Kivy imports
import kivy
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import StringProperty,ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.core.window import Window

kivy.require('1.10.1')

# Project imports
from dcss_stats.core import logger,config,utils
from dcss_stats import __version__
from dcss_stats.game_stats import StatColumn,GameStats


APP_HOME = os.path.join(str(Path.home()),'dcss_stats')
CONFIG_YML = os.path.join(APP_HOME,'config.cfg')


class MainScreen(Screen):
    text = StringProperty('')
    def change_text(self):
        self.text = "The text you want to set"
        self.manager.current = "MainScreen"

class SettingsScreen(Screen):
    label_text = StringProperty('')


class ProgressPopup(Popup):
    bar = ObjectProperty(None)


class DCSS_Stats_GUIApp(App):
    game_stats = None
    current_stat = None
    filtered = False
    dcss_downloader=None
    progress_popup = None
    main_screen = None


    def on_start(self):
        f = open("dcss_stats.log", "a", encoding="utf-8")
        utils.load_config(config,CONFIG_YML,APP_HOME)
        logger.start(config.get('logging'), f)
        logger.info("version {}".format(__version__))

        Window.maximize()

        self.main_screen = MainScreen()
        self.progress_popup = ProgressPopup()
        self.progress_popup.open()
        Thread(target=self.load_data).start()


    def load_data(self):
        self.game_stats = GameStats(config)
        self.game_stats.onChange += self.loaddata_onchange
        self.game_stats.onCompleted += self.loaddata_oncompleted
        self.game_stats.analyze()
        self.current_stat = self.game_stats.Stats

    def loaddata_onchange(self):
        self.progress_popup.bar.max = len(self.game_stats.MorgueFiles)
        self.progress_popup.bar.value = self.game_stats.current_file
        self.progress_popup.bar.canvas.ask_update()
        self.progress_popup.canvas.ask_update()
        self.main_screen.canvas.ask_update()



    def loaddata_oncompleted(self):
        self.progress_popup.dismiss()


DCSS_Stats_GUIApp().run()