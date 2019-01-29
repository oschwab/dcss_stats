from enum import Enum, auto
import urllib.request
import os

import shutil

from dcss_stats.core.eventhook import EventHook


class Server(Enum):
    CDO = 0
    CAO = auto()
    CUE = auto()
    CBRO = auto()
    LLD = auto()
    CWZ = auto()
    CXC = auto()
    CPO = auto()
    CJR = auto()
    CKO = auto()

    def to_address(self):
        labels = {
            self.CDO: "crawl.develz.org",
            self.CAO: "crawl.akrasiac.org",
            self.CUE: "underhound.eu",
            self.CBRO: "crawl.beRotato.org",
            self.LLD: "lazy-life.ddo.jp",
            self.CWZ: "webzook.net",
            self.CXC: "crawl.xtahua.com",
            self.CPO: "crawl.project357.org",
            self.CJR: "crawl.jorgrun.rocks",
            self.CKO: "crawl.kelbi.org"

        }
        return labels[self]

    def get_morgue(self):
        if (self==self.CKO):
            return "crawl/morgue"
        else:
            return "morgue"
    def __str__(self):
        return self.name.upper()


class DCSSDownloader:
    servers={}
    morgue_repo= ''

    onChange = EventHook()
    onCompleted = EventHook()

    nb_files=0
    nb_downloaded=0


    def __init__(self,servers,morgue_repo,offline_morgue):
        self.servers = servers
        self.morgue_repo=morgue_repo
        self.offline_morgue = offline_morgue



    def download(self):
        if os.path.exists(self.offline_morgue):
            src_files = os.listdir(self.offline_morgue)
            for file_name in src_files:
                full_file_name = os.path.join(self.offline_morgue, file_name)
                dest_file_name = os.path.join(self.morgue_repo, file_name)

                if (os.path.isfile(full_file_name)  and not os.path.exists(dest_file_name) ) :
                    shutil.copy(full_file_name, self.morgue_repo)

        for server in self.servers:
            server_enum = Server[server]
            user=self.servers[server]
            if not os.path.exists(self.morgue_repo):
                print('Creating ' + self.morgue_repo + 'folder')
                os.mkdir(self.morgue_repo)

            url = "https://" + server_enum.to_address() + "/"+ server_enum.get_morgue()  +"/" + user + "/"
        print("URL=" + url)
        response = urllib.request.urlopen(url)
        data = response.read()
        text = data.decode('utf-8')
            text = str.replace(text,"<td","\n<td")
        lines=text.splitlines()

        files = []
        for l in lines:
                if l.find('<a href')!=-1 :
                    file_link = l[l.find('<a href'):l.find('</a')]
                    file=file_link.split('>')[1]
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
                url = "https://" + server_enum.to_address() + "/"+ server_enum.get_morgue()  +"/"  + user + "/" + file_to_dl
            print("URL=" + url)
            response = urllib.request.urlopen(url)
            data = response.read()
            text = data.decode('utf-8')
            with open(os.path.join(self.morgue_repo, file_to_dl), "w", encoding='utf-8') as text_file:
                text_file.write(text)
            self.nb_downloaded = self.nb_downloaded+1
            self.onChange.fire()
        self.onCompleted.fire()




