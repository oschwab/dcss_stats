
import itertools
import re
import os


def file_contains(filename, filter,regex=False):
    '''Determine whether a file contains a string.'''
    if '20180920-115550' in filename:
        a=5

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