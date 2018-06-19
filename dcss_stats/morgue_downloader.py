from enum import Enum, auto
import urllib.request
import os

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
    path=''

    onChange = EventHook()
    onCompleted = EventHook()

    nb_files=0
    nb_downloaded=0


    def __init__(self,server,user,path):
        self.server = server
        self.user=user
        self.path=path



    def download(self):
        user = self.user
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
                if (ext in ['.txt','.lst','.map']):
                    files.append(file)

        for dirname, dirnames, filenames in os.walk(self.path):
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
            with open(os.path.join(self.path,file_to_dl), "w", encoding='utf-8') as text_file:
                text_file.write(text)
            self.nb_downloaded = self.nb_downloaded+1
            self.onChange.fire()
        self.onCompleted.fire()


# if __name__ == '__main__':
#     d = DCSSDownloader(server=Server.cpo,user='lepoulpe303',path='K:\Perso\dcss\morgue')
#     d.download()


