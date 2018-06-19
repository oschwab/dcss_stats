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
from tkinter import messagebox




class Application:

    game_stats = None
    current_stat = None
    filtered = False
    dcss_downloader=None
#    displayed_cols_nofilter = [ StatColumn.score, StatColumn.datedeath, StatColumn.dun_lev, StatColumn.endgame_cause, StatColumn.background, StatColumn.species]
    displayed_cols_nofilter = [e for e in StatColumn]
    displayed_cols_filter = displayed_cols_nofilter
    displayed_cols = []
    chkfilter_state = None
    config_dialog = None


    def __init__(self, master):

        #1: Create a builder
        self.builder = builder = pygubu.Builder()

        #2: Load an ui file
        builder.add_from_file('dcss_stats_gui.ui')
        builder.connect_callbacks(self)
        #3: Create the widget using a master as parent
        self.mainwindow = builder.get_object('mainframe', master)
        self.mainwindow.pack(expand=True, fill="both")

        root.geometry('1024x768')

        root.resizable(True, True)

        self.load_config()
        self.init_controls(master)
        self.init_morguedl()

    def init_morguedl(self):
        self.dcss_downloader = DCSSDownloader(server=Server[config.server], user=config.user ,path=config.morgue_path)
        self.dcss_downloader.onChange += self.update_download
        self.dcss_downloader.onCompleted += self.download_completed

    def fill_treeview(self, master):
        tv = self.builder.get_object('tv', master)
        map(tv.delete, tv.get_children())
        for s in self.game_stats.Stats:
            sb = [s[x] for x in self.displayed_cols]
            sb.remove(s[StatColumn.game_number])
            gn = s[StatColumn.game_number]
            if ((s[StatColumn.escaped]) and (s[StatColumn.orb]) ):
                ttags=('escaped',)
            else:
                ttags=()
            tv.insert('', 'end', text=str(gn), values=tuple(sb),tags=ttags)

    def init_controls(self, master):
        #
        # Treeview
        #
        if self.filtered:
            self.displayed_cols = self.displayed_cols_nofilter
        else:
            self.displayed_cols = self.displayed_cols_filter
        tv = self.builder.get_object('tv', master)
        colnames = [str(c) for c in self.displayed_cols]
        colnames.remove(str(StatColumn.game_number))
        colnames.insert(0, '#')
        tv['columns'] = tuple(colnames)

        sb = self.builder.get_object('tvScrollbar', master)
        sb.configure(command=tv.yview)
        tv.configure(yscrollcommand=sb.set)
        hb = self.builder.get_object('hzScrollbar', master)
        hb.configure(command=tv.xview)
        tv.configure(xscrollcommand=hb.set)

        tv.tag_configure('escaped', background='green')


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

        btnSettings= self.builder.get_object('cmdSettings', master)
        btnSettings.bind("<Button-1>", self.show_config_dialog)

        self.mainwindow.bind("<Map>",self.mainwindow_activate)
        chkfilter = self.builder.get_object('chkfilter', master)
        self.chkfilter_state = tk.IntVar()
        chkfilter.configure(command=self.chkfilter_clicked,variable=self.chkfilter_state)

    def show_config_dialog(self,event):
        if self.config_dialog is None:
            dialog = self.builder.get_object('dlgConfig', self.mainwindow)
            self.config_dialog = dialog

            cmbServer =self.builder.get_object('cmbServer', self.mainwindow)
            lstserver = list(map(str, Server))
            cmbServer.configure(values=lstserver)

            def dlgconfig_activate(event):
                txtUsername=self.builder.get_object('txtUsername', self.mainwindow)
                txtUsername.delete(0, tk.END)
                txtUsername.insert(0,config.user)

            def dialog_btsave_clicked():
                dialog.close()

            btnclose = self.builder.get_object('btnSave')
            btnclose['command'] = dialog_btsave_clicked
            self.config_dialog.bind("<Map>", dlgconfig_activate)

            dialog.run()
        else:
            self.config_dialog.show()

    def load_config(self):
        f = open("dcss_stats.log", "a", encoding="utf-8")
        config.load('./config.yml')
        if (not "morgue_path" in config.keys()):
            config.morgue_path = join(config.path, 'morgue')
        logger.start(config.core.logging, f)
        logger.info("version {}".format(__version__))

    def load_data(self):
        lblstatus =  self.builder.get_object('lblStatus', self.mainwindow)
        lblstatus.configure(text='Reading data...')
        lblstatus.update_idletasks()
        self.game_stats = GameStats(config)
        self.game_stats.onChange += self.loaddata_onchange
        self.game_stats.onCompleted += self.loaddata_oncompleted
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
        self.load_data()
        self.fill_treeview(self.mainwindow)


    def loaddata_onchange(self):
        progress = self.builder.get_object('progressbar', self.mainwindow)
        progress["value"] = self.game_stats.current_file
        progress["maximum"] = len(self.game_stats.MorgueFiles)
        progress.update_idletasks()

    def loaddata_oncompleted(self):
        lblstatus =  self.builder.get_object('lblStatus', self.mainwindow)
        lblstatus.configure(text='Completed. ' + str(len(self.game_stats.MorgueFiles)) + " games loaded")
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

    def chkfilter_clicked(self):
        chkfilter = self.builder.get_object('chkfilter', self)
        chkfilter.configure(command=self.chkfilter_clicked)

        framefilter = self.builder.get_object('FilterFrame', self)

        res= self.chkfilter_state.get()
        if (res==1):
            set_enabled(framefilter.winfo_children(),True)
        else:
            set_enabled(framefilter.winfo_children(),False)


def set_enabled(childList, enabled):
    if enabled==True:
        sstate='enabled'
    else:
        sstate='disabled'
    for child in childList:
        child.configure(state=sstate)


if __name__ == '__main__':
    root = tk.Tk()
    root.title("DCSS Stats")
    app = Application(root)

    root.mainloop()