
import itertools
import re


def file_contains(filename, filter,regex=False):
    '''Determine whether a file contains a string.'''
    if '20180419-135230' in filename:
        a=5
        b=2


    #filter=filter.encode('string-escape')

    with open(filename) as f:
        for num, line in zip(itertools.count(1), f.readlines()):
            if not regex:
                if filter in line:
                    return filename, num, line
            else:
                if re.search(filter, line):
                    return filename, num, line
    return False
