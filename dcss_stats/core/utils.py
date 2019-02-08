
import itertools
import re
import os


def file_contains(filename, filter,regex=False):
    '''Determine whether a file contains a string.'''
    if not regex:
        filter=filter.lower()
    with open(filename) as f:
        for num, line in zip(itertools.count(1), f.readlines()):
            if not regex:
                if filter in line.lower():
                    return filename, num, line
            else:
                if re.search(filter, line):
                    return filename, num, line
    return False

def open_morguefile(config,filename):
        gamefile = os.path.join(config.get('morgue_repository'), filename )
        if os.name == 'nt':
            gamefile = '"' + gamefile + '"'
        os.system(gamefile)


def load_config(config,CONFIG_YML,APP_HOME):

    if not (os.path.exists(CONFIG_YML)):
        if not (os.path.exists(APP_HOME)):
            os.makedirs(APP_HOME)
        config.add_section('settings')
        morgue_path = os.path.join(APP_HOME, 'morgue')
        if not (os.path.exists(morgue_path)):
            os.makedirs(morgue_path)
        config.set('morgue_repository', morgue_path)
        config.set('offline_morgue_path', '')
        config.set('logging', 'DEBUG')
        config.set_servers({})
        config._CONFIG_FILE = CONFIG_YML
        config.save()

    config.load(CONFIG_YML)
