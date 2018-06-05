import tkinter as tk
from dcss_stats.core import logger,config
from dcss_stats import __version__
from dcss_stats.game_stats import GameStats
from dcss_stats.core.dcss_data import is_background, is_specie,validate_class_background
from dcss_stats.game_stats import StatColumn
from tkinter.ttk import *
from tkinter import *
from os.path import join
import operator


class MainApplication(tk.Frame):

    treeview=None
    header=None
    game_stats = None
    current_stat = None
    displayed_cols = [StatColumn.score, StatColumn.datedeath, StatColumn.dun_lev, StatColumn.endgame_cause,StatColumn.background,StatColumn.species]

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        f = open("dcss_stats.log", "a", encoding="utf-8")
        config.load('./config.yml')
        if (not "morgue_path" in config.keys()):
            config.morgue_path = join(config.path, 'morgue')

        logger.start(config.core.logging, f)
        logger.info("version {}".format(__version__))

        self.create_UI()

        self.grid(sticky=(N, S, W, E))
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        self.load_data()

        #self.current_stat = self.game_stats.get_filtered_stat(self.current_stat, spec, column=StatColumn.sspecies)

        self.current_stat = sorted(self.game_stats.Stats, key=operator.itemgetter(StatColumn.score),reverse=True)
        stat= self.game_stats.get_top(self.current_stat,10)
        self.load_table(stat,'Top 10 games')


    def load_data(self):
        self.game_stats = GameStats(config)
        self.game_stats.analyze()

    def create_UI(self):
        lbl = Label(self, text="")
        lbl.grid(sticky = (W,E))

        tv = Treeview(self)

        colnames=[str(c) for c in self.displayed_cols]
        colnames.insert(0,'#')

        tv['columns'] = tuple(colnames)

        cpt=0
        for c in colnames:
            tv.heading('#' + str(cpt), text=c)
            tv.column('#'+ str(cpt), anchor='center', width=100)
            cpt=cpt+1

        #tv.grid(sticky = (N,S,W,E),padx=10,pady=10)
        tv.grid(sticky=( S,W, E), padx=10, pady=10)
        self.treeview = tv
        self.grid_rowconfigure(0, weight = 1)
        self.grid_columnconfigure(0, weight = 1)

        self.header = lbl

    def load_table(self,stats,label):
        self.header.configure(text= label )
        map(self.treeview.delete, self.treeview.get_children())
        cpt =0
        for s in stats:
            cpt += 1
            sb = [s[x] for x in self.displayed_cols]
            self.treeview.insert('', 'end', text=str(cpt), values=tuple(sb))




if __name__ == "__main__":
    root = tk.Tk()
    root.title("DCSS Stats")
    MainApplication(root).pack(side="top", fill="both", expand=True)
    root.mainloop()