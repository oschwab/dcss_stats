import csv

from dcss_stats.core.dcss_data import jobs
from dcss_stats.morgue_downloader import DCSSDownloader,Server

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
    dcss_downloader=None
    displayed_cols_nofilter = [ StatColumn.score, StatColumn.datedeath, StatColumn.dun_lev, StatColumn.endgame_cause, StatColumn.background, StatColumn.species]
    displayed_cols_filter = [StatColumn.game_number] + displayed_cols_nofilter
    displayed_cols = []

    def __init__(self, master):

        #1: Create a builder
        self.builder = builder = pygubu.Builder()

        #2: Load an ui file
        builder.add_from_file('dcss_stats_gui.ui')

        #3: Create the widget using a master as parent
        self.mainwindow = builder.get_object('mainframe', master)
        root.geometry('1024x768')
        #root.state('zoomed')
        root.resizable(True, True)

        self.load_config()
        self.init_controls(master)
        self.init_morguedl()

    def init_morguedl(self):
        self.dcss_downloader = DCSSDownloader(server=Server[config.server], user=config.user ,path=config.path)
        self.dcss_downloader.onChange += self.update_download
        self.dcss_downloader.onCompleted += self.download_completed

    def fill_treeview(self, master):
        tv = self.builder.get_object('tv', master)
        map(tv.delete, tv.get_children())
        cpt = 0
        for s in self.game_stats.Stats:
            cpt += 1
            sb = [s[x] for x in self.displayed_cols]
            tv.insert('', 'end', text=str(cpt), values=tuple(sb))

    def init_controls(self, master):
        #
        # Treeview
        #
        if self.filtered:
            self.displayed_cols = self.displayed_cols_filter
        else:
            self.displayed_cols = self.displayed_cols_nofilter
        tv = self.builder.get_object('tv', master)
        colnames = [str(c) for c in self.displayed_cols]
        colnames.insert(0, '#')
        tv['columns'] = tuple(colnames)
        sb = self.builder.get_object('tvScrollbar', master)
        sb.configure(command=tv.yview)
        tv.configure(yscrollcommand=sb.set)
        cpt = 0
        for c in colnames:
            tv.heading('#' + str(cpt), text=c)
            tv.column('#' + str(cpt), anchor='w', width=100)
            cpt = cpt + 1
        #
        # Combos
        #
        cmb_back = self.builder.get_object('cmbBackground', master)
        list_jobs = ('--All',) + tuple(sorted(jobs.keys()))
        cmb_back.configure(values=list_jobs)

        #
        # Bindings
        #
        btnDown = self.builder.get_object('cmdDownload', master)
        btnDown.bind("<Button-1>", self.download_morgue_click)

        btnCSV = self.builder.get_object('cmdCSV', master)
        btnCSV.bind("<Button-1>", self.export_csv)

        self.mainwindow.bind("<Map>",self.mainwindow_activate)

    def load_config(self):
        f = open("dcss_stats.log", "a", encoding="utf-8")
        config.load('./config.yml')
        if (not "morgue_path" in config.keys()):
            config.morgue_path = join(config.path, 'morgue')
        logger.start(config.core.logging, f)
        logger.info("version {}".format(__version__))

    def load_data(self):
        self.game_stats = GameStats(config)
        self.game_stats.analyze()
        self.current_stat = self.game_stats.Stats

    def mainwindow_activate(self,event):
        self.load_data()
        self.fill_treeview(self.mainwindow)


    def download_morgue_click(self,event):
        lblstatus =  self.builder.get_object('lblStatus', self.mainwindow)
        lblstatus.configure(text='Downloading...')
        lblstatus.update_idletasks()
        self.dcss_downloader.download()

    def update_download(self):
        progress = self.builder.get_object('progressbar', self.mainwindow)
        progress["value"] = self.dcss_downloader.nb_downloaded
        progress["maximum"] = self.dcss_downloader.nb_files
        progress.update_idletasks()

    def download_completed(self):
        lblstatus =  self.builder.get_object('lblStatus', self.mainwindow)
        lblstatus.configure(text='Completed. ' + str(self.dcss_downloader.nb_files) + " files downloaded" )
        progress = self.builder.get_object('progressbar', self.mainwindow)
        progress["value"] = 0
        progress["maximum"] = 0

    def export_csv(self,event):
        with open('global.csv', 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator="\n")

            header_written = False
            for s in self.current_stat:
                if not header_written:
                    writer.writerow(s.keys())
                    header_written = True

                writer.writerow(s.values())


if __name__ == '__main__':
    root = tk.Tk()
    root.title("DCSS Stats")
    app = Application(root)
    root.mainloop()