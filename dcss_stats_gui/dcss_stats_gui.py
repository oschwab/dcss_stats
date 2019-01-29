import csv
import os

from dcss_stats.core.dcss_data import jobs,species
from dcss_stats.morgue_downloader import DCSSDownloader,Server
from pathlib import Path
import pygubu
from dcss_stats.game_stats import StatColumn,GameStats
from dcss_stats.core import logger,config,utils
from dcss_stats import __version__
import datetime
import leather
import mmap


try:
    import tkinter as tk
    from tkinter import messagebox
except:
    import Tkinter as tk
    import tkMessageBox as messagebox

APP_HOME = os.path.join(str(Path.home()),'dcss_stats')
CONFIG_YML = os.path.join(APP_HOME,'config.cfg')

class Application:

    ALL_VALUES = '--All'

    game_stats = None
    current_stat = None
    filtered = False
    dcss_downloader=None

    numeric_cols=(StatColumn.row_number, StatColumn.game_id, StatColumn.hp, StatColumn.turns, StatColumn.score, StatColumn.runes,StatColumn.game_rank)
    config_dialog = None
    matrix_view= None
    master=None
    great_total=-1

    def __init__(self, master):

        self.master=master
        #1: Create a builder
        self.builder = builder = pygubu.Builder()

        #2: Load an ui file
        builder.add_from_file('dcss_stats_gui.ui')

        #3: Create the widget using a master as parent
        self.mainwindow = builder.get_object('mainframe', master)
        self.mainwindow.pack(expand=True, fill="both")

        root.geometry('1024x768')

        root.resizable(True, True)

        self.load_config()

        self.selected_server = tk.StringVar()
        self.init_controls(master)
        builder.connect_callbacks(self)


    def init_morguedl(self):
        #TODO manage several servers
        config_server = config.get_servers()

        self.dcss_downloader = DCSSDownloader(servers=config_server ,morgue_repo=config.get('morgue_repository'),offline_morgue=config.get('offline_morgue_path'))
        self.dcss_downloader.onChange += self.update_download
        self.dcss_downloader.onCompleted += self.download_completed

    def fill_treeview(self):
        tv = self.builder.get_object('tv', self.mainwindow)

        tv.delete(*tv.get_children())
        for s in self.current_stat:
            sb = [s[x] for x in self.displayed_cols]
            sb.remove(s[StatColumn.row_number])
            gn = s[StatColumn.row_number]
            ttags=()
            if ((s[StatColumn.escaped]) and (s[StatColumn.orb]) ):
                ttags= ttags + ('escaped',)

            else:
                if (s[StatColumn.runes])>0:
                    ttags=('runes'+str(s[StatColumn.runes]),)
            tv.insert('', 'end', text=str(gn), values=tuple(sb),tags=ttags)

    def init_controls(self, master):
        #
        # Treeview
        #

        self.displayed_cols = [e for e in StatColumn]
        tv = self.builder.get_object('tv', master)
        colnames = [str(c) for c in self.displayed_cols]
        colnames.remove(str(StatColumn.row_number))
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
            tv.column(col, anchor='w', width=100)

        tv.column('#0',width=35)


        tv.tag_configure('escaped', background='green')
        tv.bind("<Double-1>", self.on_tv_doubleclick)

        #
        # Stats treeview
        #
        tv_stats = self.builder.get_object('tvMsg', self.mainwindow)
        tv_stats['columns'] = (' ',' ')

        #
        # Filter
        #
        cmb_back = self.builder.get_object('lstBackground', master)
        list_jobs = ('--All',) + tuple(sorted(jobs.keys()))
        cmb_back.bind('<<ListboxSelect>>', self.on_back_select)

        for item in list_jobs:
            cmb_back.insert(tk.END, item)

        cmb_spec = self.builder.get_object('lstSpecies', master)
        list_spec = ('--All',) + tuple(sorted(species.keys()))
        cmb_spec.bind('<<ListboxSelect>>', self.on_job_select)

        for item in list_spec :
            cmb_spec.insert(tk.END, item)

        #
        # Buttons
        #
        btnDown = self.builder.get_object('cmdDownload', master)
        btnDown.bind("<Button-1>", self.download_morgue_click)

        btnCSV = self.builder.get_object('cmdCSV', master)
        btnCSV.bind("<Button-1>", self.export_csv)

        btnSettings= self.builder.get_object('cmdSettings', master)
        btnSettings.bind("<Button-1>", self.show_config_dialog)

        btnMatrix= self.builder.get_object('cmdMatrix', master)
        btnMatrix.bind("<Button-1>", self.show_matrix_view)

        #
        # Main window
        #
        self.mainwindow.bind("<Map>",self.mainwindow_activate)



    def on_btnfilter_click(self):
        self.apply_filter()


    def on_avgscoremonth_clicked(self):
        chart = leather.Chart('Average score per month')
#        chart.add_dots(data)
#        chart.to_svg('examples/charts/simple_pairs.svg')


    def on_back_select(self,event):
        w = event.widget
        index = int(w.curselection()[0])
        value = w.get(index)

        cmb_spec = self.builder.get_object('lstSpecies', self.master)
        if (cmb_spec.curselection() != ()):
            save_val = cmb_spec.get(cmb_spec.curselection())
        else:
            save_val = None
        cmb_spec.delete(0, tk.END)
        list_spec = (self.ALL_VALUES,)

        if (value != self.ALL_VALUES):
            list_spec = list_spec + tuple(sorted(self.game_stats.get_species_for_job(value,self.current_stat) ))
        else:
            list_spec = list_spec + tuple(sorted(species.keys()))

        for item in list_spec:
            cmb_spec.insert(tk.END, item)
            if (item==save_val):
                cmb_spec.selection_set(tk.END)

    def on_job_select(self,event):
        w = event.widget
        index = int(w.curselection()[0])
        value = w.get(index)

        cmb_job = self.builder.get_object('lstBackground', self.master)
        if (cmb_job.curselection() != ()):
            save_val = cmb_job.get(cmb_job.curselection())
        else:
            save_val=None
        cmb_job.delete(0, tk.END)
        list_job= (self.ALL_VALUES,)

        if (value != self.ALL_VALUES):
            list_job = list_job + tuple(sorted(self.game_stats.get_job_for_species(value,self.current_stat) ))
        else:
            list_job = list_job + tuple(sorted(jobs.keys()))

        for item in list_job:
            cmb_job.insert(tk.END, item)
            if (item==save_val):
                cmb_job.selection_set(tk.END)

    def apply_filter(self):
        cmb_job = self.builder.get_object('lstBackground', self.master)
        job = self.ALL_VALUES
        if (cmb_job.curselection() != ()):
            job = cmb_job.get(cmb_job.curselection())

        cmb_spec = self.builder.get_object('lstSpecies', self.master)

        spec=self.ALL_VALUES

        if (cmb_spec.curselection())!=():
            spec = cmb_spec.get(cmb_spec.curselection())

        if (job==self.ALL_VALUES) or (spec==self.ALL_VALUES):
            self.current_stat = self.game_stats.Stats

        if (job != self.ALL_VALUES):
            self.current_stat = self.game_stats.get_filtered_stat(stat=self.current_stat ,value=job,column=StatColumn.background)
        if (spec != self.ALL_VALUES):
            self.current_stat = self.game_stats.get_filtered_stat(stat=self.current_stat ,value=spec,column=StatColumn.species)


        txtWordFilter = self.builder.get_object('txtWordFilter', self.master)
        regex = self.builder.tkvariables.__getitem__('RegexVar').get()

        txt_filter = txtWordFilter.get(1.0, tk.END)
        if (len(txt_filter)>0):
            if (txt_filter[-1:]=='\n'):
                txt_filter = txt_filter[:-1]
            self.current_stat = self.game_stats.apply_text_filter(txt_filter,regex==1,config,self.current_stat)

        self.display_data()


    def display_data(self):
        self.fill_treeview()
        self.fill_stats()

    def fill_stats(self):
        tv_stats = self.builder.get_object('tvMsg', self.mainwindow)

        tv_stats.delete(*tv_stats.get_children())
        tv_stats.insert('', 'end', text='Number of games:', values=(len(self.current_stat),))
        tv_stats.insert('', 'end', text='Average score:', values=(self.game_stats.get_averagescore(self.current_stat),))
        total_play_time =  str(datetime.timedelta(seconds=self.game_stats.get_playtime(self.current_stat)))
        tv_stats.insert('', 'end', text='Total play time', values=(total_play_time,))
        pc_total=(len(self.current_stat)  * 100) / self.great_total
        tv_stats.insert('', 'end', text='% of total', values=(pc_total,))




    def on_tv_doubleclick(self, event):
        tv = self.builder.get_object('tv', self.master)
        item = tv.item(tv.selection()[0])
        filename=item['values'][StatColumn.filename._value_ - 1]
        utils.open_morguefile(config,filename)



    def show_config_dialog(self,event):
        if self.config_dialog is None:
            dialog = self.builder.get_object('dlgConfig', self.mainwindow)
            self.config_dialog = dialog

            cmbServer =self.builder.get_object('cmbServer', self.mainwindow)
            lstserver = list(map(str, Server))
            cmbServer.configure(values=lstserver,textvariable=self.selected_server)
            txtUsername=self.builder.get_object('txtUsername', self.mainwindow)
            morgueRepository=self.builder.get_object('morgueRepository',self.mainwindow)
            morgueOffStorage=self.builder.get_object('morgueOffStorage',self.mainwindow)



            def dlgconfig_activate(event):

                # TODO manage several servers
                config_server, config_user = config.get_servers().popitem()

                set_text(txtUsername,config_user)
                set_text(morgueRepository, config.get('morgue_repository'))
                set_text(morgueOffStorage, config.get('offline_morgue_path'))
                self.selected_server.set(config_server)

            def dialog_btsave_clicked():
                # TODO manage several servers
                config.set_servers({self.selected_server.get():txtUsername.get() })
                config.set('morgue_repository', morgueRepository.get())
                config.set('offline_morgue_path', morgueOffStorage.get())
                config.save()
                dialog.close()

            btnclose = self.builder.get_object('btnSave')
            btnclose['command'] = dialog_btsave_clicked
            self.config_dialog.bind("<Map>", dlgconfig_activate)

            dialog.run()
        else:
            self.config_dialog.show()

    def show_matrix_view(self, event):
        self.matrix_view= self.builder.get_object('frameMatrix', self.mainwindow)

        # get screen width and height
        ws = root.winfo_screenwidth()  # width of the screen
        hs = root.winfo_screenheight()  # height of the screen


        # set the dimensions of the screen
        # and where it is placed
        self.matrix_view.top=0
        self.matrix_view.left=0
        self.matrix_view.width=ws
        self.matrix_view.height=hs


        tv = self.builder.get_object('tvMatrix', self.matrix_view)

        sb = self.builder.get_object('Scrollbar_v', self.master)
        sb.configure(command=tv.yview)
        tv.configure(yscrollcommand=sb.set)
        hb = self.builder.get_object('Scrollbar_h', self.master)
        hb.configure(command=tv.xview)
        tv.configure(xscrollcommand=hb.set)

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
        if not (os.path.exists(CONFIG_YML)):
            if not (os.path.exists(APP_HOME)):
                os.makedirs(APP_HOME)
            config.add_section('settings')
            morgue_path=os.path.join(APP_HOME,'morgue')
            if not (os.path.exists(morgue_path)):
                os.makedirs(morgue_path)
            config.set('morgue_repository',morgue_path)
            config.set('offline_morgue_path','')
            config.set('logging','DEBUG')
            config.set_servers({})
            config._CONFIG_FILE = CONFIG_YML
            config.save()

        config.load(CONFIG_YML)
        logger.start(config.get('logging'), f)
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
        self.great_total = len(self.game_stats.Stats)


    def mainwindow_activate(self,event):
        self.load_data()
        self.display_data()


    def download_morgue_click(self,event):
        self.init_morguedl()
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
        self.display_data()


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
        filename='global.csv'

        with open(filename, 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator="\n")

            header_written = False
            for s in self.current_stat:
                if not header_written:
                    writer.writerow(s.keys())
                    header_written = True

                writer.writerow(s.values())
        os.system(filename)


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
        sstate='normal'
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