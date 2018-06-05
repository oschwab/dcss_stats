try:
    import tkinter as tk  # for python 3
except:
    import Tkinter as tk  # for python 2
import pygubu
from dcss_stats.game_stats import StatColumn,GameStats
from dcss_stats.core import logger,config
from os.path import join
from dcss_stats import __version__




class Application:

    game_stats = None
    current_stat = None
    filtered = False
    displayed_cols_filter = [StatColumn.game_number,StatColumn.score, StatColumn.datedeath, StatColumn.dun_lev, StatColumn.endgame_cause,StatColumn.background,StatColumn.species]
    displayed_cols_nofilter = [ StatColumn.score, StatColumn.datedeath, StatColumn.dun_lev, StatColumn.endgame_cause, StatColumn.background, StatColumn.species]
    displayed_cols = []

    def __init__(self, master):

        #1: Create a builder
        self.builder = builder = pygubu.Builder()

        #2: Load an ui file
        builder.add_from_file('dcss_stats_gui.ui')

        #3: Create the widget using a master as parent
        self.mainwindow = builder.get_object('mainframe', master)
        #root.state('zoomed')
        root.resizable(True, False)

        f = self.load_config()

        logger.start(config.core.logging, f)
        logger.info("version {}".format(__version__))

        self.load_data()

        if self.filtered:
            self.displayed_cols = self.displayed_cols_filter
        else:
            self.displayed_cols = self.displayed_cols_nofilter

        tv = builder.get_object('tv', master)

        colnames=[str(c) for c in self.displayed_cols]
        colnames.insert(0,'#')

        tv['columns'] = tuple(colnames)

        sb = builder.get_object('tvScrollbar', master)
        sb.configure(command=tv.yview)
        tv.configure(yscrollcommand=sb.set)
        cpt=0
        for c in colnames:
            tv.heading('#' + str(cpt), text=c)
            tv.column('#'+ str(cpt), anchor='center', width=100)
            cpt=cpt+1

        map(tv.delete, tv.get_children())
        cpt =0
        for s in self.game_stats.Stats:
            cpt += 1
            sb = [s[x] for x in self.displayed_cols]
            tv.insert('', 'end', text=str(cpt), values=tuple(sb))




    def load_config(self):

        f = open("dcss_stats.log", "a", encoding="utf-8")
        config.load('./config.yml')
        if (not "morgue_path" in config.keys()):
            config.morgue_path = join(config.path, 'morgue')
        return f

    def load_data(self):
        self.game_stats = GameStats(config)
        self.game_stats.analyze()


if __name__ == '__main__':
    root = tk.Tk()
    root.title("DCSS Stats")
    app = Application(root)
    root.mainloop()