try:
    import tkinter as tk  # for python 3
except:
    import Tkinter as tk  # for python 2
import pygubu

class ConfigDialog:

    def __init__(self, parent):
        #1: Create a builder
        self.builder = builder = pygubu.Builder()

        #2: Load an ui file
        builder.add_from_file('dcss_stats_config.ui')
        builder.connect_callbacks(self)


    def ok(self):
        self.destroy()