import csv

import os

from dcss_stats.core.dcss_data import jobs,species
from dcss_stats.morgue_downloader import DCSSDownloader,Server

try:
    import tkinter as tk  # for python 3
except:
    import Tkinter as tk  # for python 2
import pygubu
from dcss_stats.game_stats import StatColumn,GameStats
from dcss_stats.core import logger,config
from dcss_stats import __version__
from tkinter import messagebox




class Application:

    game_stats = None
    current_stat = None
    filtered = False
    dcss_downloader=None

    numeric_cols=(StatColumn.row_number, StatColumn.game_id, StatColumn.hp, StatColumn.turns, StatColumn.score, StatColumn.runes)
    chkfilter_state = None
    config_dialog = None
    matrix_view= None
    master=None

    def __init__(self, master):

        self.master=master
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
        self.dcss_downloader = DCSSDownloader(server=Server[config.server], user=config.user ,morgue_repo=config.morgue_repository,offline_morgue=config.offline_morgue_path)
        self.dcss_downloader.onChange += self.update_download
        self.dcss_downloader.onCompleted += self.download_completed

    def fill_treeview(self, master):
        tv = self.builder.get_object('tv', master)
        map(tv.delete, tv.get_children())
        for s in self.game_stats.Stats:
            sb = [s[x] for x in self.displayed_cols]
            sb.remove(s[StatColumn.row_number])
            gn = s[StatColumn.row_number]
            if ((s[StatColumn.escaped]) and (s[StatColumn.orb]) ):
                ttags=('escaped',)
            else:
                ttags=()
            tv.insert('', 'end', text=str(gn), values=tuple(sb),tags=ttags)

    def init_controls(self, master):
        #
        # Treeview
        #

        self.displayed_cols = [e for e in StatColumn]
        tv = self.builder.get_object('tv', master)
        colnames = [str(c) for c in self.displayed_cols]
        tv['columns'] = tuple(colnames)

        sb = self.builder.get_object('tvScrollbar', master)
        sb.configure(command=tv.yview)
        tv.configure(yscrollcommand=sb.set)
        hb = self.builder.get_object('hzScrollbar', master)
        hb.configure(command=tv.xview)
        tv.configure(xscrollcommand=hb.set)

        for col in colnames:
            tv.heading(col, text=col, command=lambda _col=col: \
                self.treeview_sort_column(tv, _col, False))


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

        btnMatrix= self.builder.get_object('cmdMatrix', master)
        btnMatrix.bind("<Button-1>", self.show_matrix_view)

        tv.bind("<Double-1>", self.on_tv_doubleclick)

        self.mainwindow.bind("<Map>",self.mainwindow_activate)
        chkfilter = self.builder.get_object('chkfilter', master)
        self.chkfilter_state = tk.IntVar()
        chkfilter.configure(command=self.chkfilter_clicked,variable=self.chkfilter_state)

    def on_tv_doubleclick(self, event):
        tv = self.builder.get_object('tv', self.master)
        item = tv.item(tv.selection()[0])
        gamefile = os.path.join(config.morgue_repository, item['values'][StatColumn.filename._value_-1])
        os.system(gamefile)


    def show_config_dialog(self,event):
        if self.config_dialog is None:
            dialog = self.builder.get_object('dlgConfig', self.mainwindow)
            self.config_dialog = dialog

            cmbServer =self.builder.get_object('cmbServer', self.mainwindow)
            lstserver = list(map(str, Server))
            cmbServer.configure(values=lstserver)

            def dlgconfig_activate(event):
                txtUsername=self.builder.get_object('txtUsername', self.mainwindow)
                set_text(txtUsername,config.user)
                morgueRepository=self.builder.get_object('morgueRepository',self.mainwindow)
                set_text(morgueRepository, config.morgue_repository)
                morgueOffStorage=self.builder.get_object('morgueOffStorage',self.mainwindow)
                set_text(morgueOffStorage, config.offline_morgue_path)


            def dialog_btsave_clicked():
                dialog.close()

            btnclose = self.builder.get_object('btnSave')
            btnclose['command'] = dialog_btsave_clicked
            self.config_dialog.bind("<Map>", dlgconfig_activate)

            #TODO Load paths from config

            dialog.run()
        else:
            self.config_dialog.show()

    def show_matrix_view(self, event):
        self.matrix_view= self.builder.get_object('frameMatrix', self.mainwindow)
        #self.matrix_view.pack(expand=True, fill="both")
        tv = self.builder.get_object('tvMatrix', self.mainwindow)
        colnames = [str(c) for c in species]
        colnames.insert(0, '#')
        tv['columns'] = tuple(colnames)
        vals=()
        ttags=()
        for j in jobs:
            tv.insert('', 'end', text=str(j),  values=tuple(vals), tags=ttags)



        self.matrix_view.show()


    def load_config(self):
        f = open("dcss_stats.log", "a", encoding="utf-8")
        config.load('./config.yml')
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
        lblstatus =  self.builder.get_object('lblStatus', self.mainwindow)
        lblstatus.configure(text=f'Downloading... {self.dcss_downloader.nb_downloaded} / {self.dcss_downloader.nb_files}')
        lblstatus.update_idletasks()



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

    def treeview_sort_column(self,tv, col, reverse):

        numeric_cols_lbl = list(str(c) for c in self.numeric_cols)
        if (col in numeric_cols_lbl):
            l = [(int(tv.set(k, col)), k) for k in tv.get_children('')]
        else:
            l = [(tv.set(k, col), k) for k in tv.get_children('')]

        l.sort(reverse=reverse)

        # rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            tv.move(k, '', index)

        # reverse sort next time
        tv.heading(col, command=lambda: \
                   self.treeview_sort_column(tv, col, not reverse))


def set_enabled(childList, enabled):
    if enabled==True:
        sstate='enabled'
    else:
        sstate='disabled'
    for child in childList:
        child.configure(state=sstate)


def set_text(control,text):
    control.delete(0, tk.END)
    control.insert(0,text)





if __name__ == '__main__':
    root = tk.Tk()
    root.title("DCSS Stats")
    app = Application(root)

    root.mainloop()