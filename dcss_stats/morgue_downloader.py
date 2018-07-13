from enum import Enum, auto
import urllib.request
import os

import shutil

from dcss_stats.core.eventhook import EventHook


class Server(Enum):
    cdo = 0
    cao = auto()
    cue = auto()
    cbro = auto()
    lld = auto()
    cwz = auto()
    cxc = auto()
    cpo = auto()
    cjr = auto()

    def to_address(self):
        labels = {
            self.cdo: "crawl.develz.org",
            self.cao: "crawl.akrasiac.org",
            self.cue: "underhound.eu",
            self.cbro: "crawl.beRotato.org",
            self.lld: "lazy-life.ddo.jp",
            self.cwz: "webzook.net",
            self.cxc: "crawl.xtahua.com",
            self.cpo: "crawl.project357.org",
            self.cjr: "crawl.jorgrun.rocks"
        }
        return labels[self]

    def __str__(self):
        return self.name.upper()


class DCSSDownloader:
    server=Server.cpo
    user=''
    morgue_repo= ''

    onChange = EventHook()
    onCompleted = EventHook()

    nb_files=0
    nb_downloaded=0


    def __init__(self,server,user,morgue_repo,offline_morgue):
        self.server = server
        self.user=user
        self.morgue_repo=morgue_repo
        self.offline_morgue = offline_morgue



    def download(self):
        user = self.user
        if not os.path.exists(self.morgue_repo):
            print('Creating ' + self.morgue_repo + 'folder')
            os.mkdir(self.morgue_repo)

        src_files = os.listdir(self.offline_morgue)
        for file_name in src_files:
            full_file_name = os.path.join(self.offline_morgue, file_name)
            dest_file_name = os.path.join(self.morgue_repo, file_name)

            if (os.path.isfile(full_file_name)  and not os.path.exists(dest_file_name) ) :
                shutil.copy(full_file_name, self.morgue_repo)



        url = "https://" + self.server.to_address() + "/morgue/" + user + "/"
        print("URL=" + url)
        response = urllib.request.urlopen(url)
        data = response.read()
        text = data.decode('utf-8')

        lines=text.splitlines()

        files = []
        for l in lines:
            if l.startswith('<a href') :
                file=l.split('"')[1]
                ext = file[-4:]
                #TODO see what are other extension for ..
                #if (ext in ['.txt','.lst','.map']):
                if (ext in ['.txt']):
                    files.append(file)

        for dirname, dirnames, filenames in os.walk(self.morgue_repo):
            for filename in filenames:
                if filename in files:
                    files.remove(filename)
        self.nb_files = len(files)
        print(str(self.nb_files)+ " files to download")

        self.nb_downloaded = 0
        for file_to_dl in files:
            url = "https://" + self.server.to_address() + "/morgue/" + user + "/" + file_to_dl
            print("URL=" + url)
            response = urllib.request.urlopen(url)
            data = response.read()
            text = data.decode('utf-8')
            with open(os.path.join(self.morgue_repo, file_to_dl), "w", encoding='utf-8') as text_file:
                text_file.write(text)
            self.nb_downloaded = self.nb_downloaded+1
            self.onChange.fire()
        self.onCompleted.fire()




