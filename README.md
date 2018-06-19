# dcss_stats

## Introduction

An utility to get statistics on [Dungeon Crawl Stone Soup ](http://crawl.develz.org/) games.

[Example output (HTML)](https://gistpreview.github.io/?ce50e2667dd57da04299e37999eabaf2)


## Development

- Developped in Python 3.6 using Jetbrains PyCharm
- Project template generated using [CookieCutter](https://github.com/kragniz/cookiecutter-pypackage-minimal)
- GUI using TKinter and [Pygubu](https://github.com/alejandroautalan/pygubu/)


## GUI

WORK IN PROGRESS


## Command line interface

`python dcss_stats_cli\dcss_stats_cli.py`


 - -c --config : set the path for the config file (default ./config.yml)    
 - -v --version : print version and exit
 - -w --warn : logger warning level (default INFO)
 - -p --path : DCSS installation path
 - -o --output : output  : text/console/markdown ( default text)
 - -i : interactive mode _(work in progress)_
 - -s --scorevol : generate CSV with score evolution values (default False)

### Configuration file

by default dcss_stats_cli\config.yml




## Information retrieved from parsing

For each morgue file : (unrealistic example)

 -   'dungeon': 'Dungeon',
 -   'date_start' : '2015-07-12'
 -   'background': 'Ice Elementalist',
 -   'name': 'Awutz',
 -   'hp': '30',
 -   'surname': 'the Chiller',
 -   'duration': '00:11:56',
 -   'dun_lev': 'Dungeon:1',
 -   'level': '4',
 -   'turns': '2120',
 -   'god': 'Trog',
 -   'religion_rank': 'Champion',
 -   'filename': 'morgue-Awutz-20160912-104224.txt',
 -   'species': 'Merfolk',
 -   'version': '0.18.1 (tiles)',
 -   'endgame_cause': 'giant frog',
 -   'self_kill' : False,
 -   'dungeon_level': '1',
 -   'escaped' : True,
 -   'orb ': True,
 -   'runes' : 3,
 -   'score': 656453
    







