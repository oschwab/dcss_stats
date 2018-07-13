import configparser
import ast

class Config(configparser.RawConfigParser):
    _CONFIG_FILE=""
    def load(self,file):
        self._CONFIG_FILE = file
        self.read(file)

    def save(self):
        with open(self._CONFIG_FILE, 'w') as configfile:
            self.write(configfile)

    def get(self,setting):
        return(configparser.RawConfigParser.get(self,'settings',setting))

    def get_servers(self):
        d1 = ast.literal_eval(configparser.RawConfigParser.get(self,'settings', 'servers'))
        return(d1)

    def set_servers(self,servers):
        configparser.RawConfigParser.set(self, 'settings', 'servers',str(servers))



config = Config()
