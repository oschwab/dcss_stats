
import operator
import datetime
from enum import Enum, auto
from os import listdir
from os.path import isfile, join
from .core import logger



class StatColumn(Enum):
    dungeon = 0
    background = auto()
    datestart= auto()
    name = auto()
    hp = auto()
    surname = auto()
    duration = auto()
    dun_lev = auto()
    level = auto()
    turns = auto()
    god = auto()
    religion_rank = auto()
    filename = auto()
    species = auto()
    version = auto()
    death_cause = auto()
    self_kill = auto()
    dungeon_level = auto()
    score = auto()
    escaped = auto()
    orb=auto()
    runes=auto()

class GameStats:
    """
    Class that parses morgue folder and generate a stat structure
    that can be interrogated through get... methods
    """

    MorguePath = ''

    MorgueFiles = []

    """
    Example of line in Stats :
    {'dungeon': 'Dungeon',
    'background': 'Ice Elementalist',
    'name': 'Awutz',
    'hp': '30',
    'surname': 'the Chiller',
    'duration': '00:11:56',
    'dun_lev': 'Dungeon:1',
    'level': '4',
    'turns': '2120',
    'god': 'None',
    'religion_rank': 'None',
    'filename': 'morgue-Awutz-20160912-104224.txt',
    'species': 'Merfolk',
    'version': '0.18.1 (tiles)',
    'death_cause': 'giant frog',
    'self_kill' : False,
    'dungeon_level': '1',
    'escaped' : True,
    'orb ': True,
    'runes' : 3,
    'score': 63}
    """

    Stats = []

    def __init__(self, configuration):
        """
        Constructor
        :param morguepath: Path to crawl morgue files (ex: C:\dcss\morgue )
        """
        self.MorguePath = configuration.morgue_path
        self.MorgueFiles = []
        for f in listdir(self.MorguePath):
            if isfile(join(self.MorguePath, f)) and f[:6] == "morgue" and f[-3:] == "txt":
                self.MorgueFiles.append(f)

    def analyze(self):

        """
        Analyze morgue files in :MorguePath and fill :Stats
        """
        self.Stats = []

        for morgue in self.MorgueFiles:
            logger.info("Analyzing " + morgue)
            with open(join(self.MorguePath, morgue)) as file:
                content = file.readlines()

            stat = self.get_information(content)
            if len(stat)>0:
                stat[StatColumn.filename] = morgue
                self.Stats.append(stat)

    def get_number_of_game(self, stat=None):
        """
        :return: the number of game played in global or param stat structure
        """
        if stat is None:
            stat = self.Stats

        return len(stat)

    def get_char_filtered_stat(self, character):
        """
        returns a stat structure filtered for character
        :param character: the character (race+job) to filter
        :return: stat structure
        """
        filtstat = []
        for s in self.Stats:
            sb = s[StatColumn.species] + ' ' + s[StatColumn.background]
            if sb == character:
                filtstat.append(s)
        return filtstat

    def get_filtered_stat(self, value,column=StatColumn.dungeon_level, ):
        """
             returns a stat structure filtered for column
        :param column: the column to filter
        :param value:  the value of the column
        :return: stat structure
        """
        filtstat = []
        for s in self.Stats:

            if s[column] == value:
                filtstat.append(s)
        return filtstat

    def get_character_list(self):

        """
        Get the list of characters types (race+job) found in morgue
        :return: a . list . of . characters
        """
        list_char = []
        for s in self.Stats:
            sb = s[StatColumn.species] + ' ' + s[StatColumn.background]
            if sb not in list_char:
                list_char.append(sb)

        return list_char

    def get_stat_list(self,statcolumn=StatColumn.dungeon_level):
        """
        Get the list of different statcolumn values
        :param statcolumn: the column
        :return: the list pof possible values of column
        """
        list_stat = []
        for s in self.Stats:
            if s[statcolumn] not in list_stat:
                list_stat.append(s[statcolumn])

        return list_stat
    def get_stat_basic(self, column, stat=None, retsorted=True):
        """
i       From the stat structure in param , get the count of each possible value of *column*
        :param column: the StatColumn value
        :param stat: the stat structure ; if None global one is taken
        :return: a list of tuples (column value,count)
        """
        if stat is None:
            stat = self.Stats
        simplestat = {}
        for s in stat:
            try:
                if s[column] in simplestat:
                    simplestat[s[column]] += 1
                else:
                    simplestat[s[column]] = 1
            except KeyError:
                # hope that filename has been filled, otherwise expect a complete crash ....
                logger.error("Cannot find stat {} in file {}".format(column,s[StatColumn.filename]))

        if retsorted:
            sorted_simplestat = sorted(simplestat.items(), key=operator.itemgetter(1), reverse=True)
        else:
            sorted_simplestat = simplestat.items()

        return sorted_simplestat

    def get_best_game(self, stat=None):
        """
        returns the game with higher score
        :param stat: the stat structure ; if None global one is taken
        :return: the highest score
        """
        if stat is None:
            stat = self.Stats
        bestgame = stat[0]
        for s in stat:
            if s[StatColumn.score] > bestgame[StatColumn.score]:
                bestgame = s
        return bestgame[StatColumn.score]

    def get_averagescore(self, stat=None):
        """
        returns the average score
        :param stat: the stat structure ; if None global one is taken
        :return: the average score
        """
        if stat is None:
            stat = self.Stats
        avg = 0.0
        if len(stat) == 0:
            return 0
        for s in stat:
            avg = avg + s[StatColumn.score]
        return int(avg / len(stat))

    def get_scoreevolution(self,type='month',stat=None):
        if stat is None:
            stat = self.Stats
        evol={}

        if type=="month":
            filter="%y-%m"
        else:
            filter="%y-%m-%d"


        for s in stat:
            key=s[StatColumn.datestart].strftime(filter)
            if not key in evol:
                evol[key]=[]
            evol[key].append(s[StatColumn.score])

        ret=[]
        for key, value in sorted(evol.items()):
            ret.append([key,int(sum(value)/len(value))])

        return ret




    def get_information(self, morgue):
        """
        Create an entry for the stat structure
        :param morgue: the morgue file
        :return: the information contained in the morge file
        """


        """
        Example :
        
        65618 XXXX the Impaler (level 15, -2/184 HPs)
             Began as a Merfolk Monk on Oct 10, 2014.
             Was the Champion of Fedhas.
             Slain by a frost giant
             ... wielding a +0 battleaxe of freezing
              (6 damage)
             ... in an ice cave.
             The game lasted 02:28:38 (35567 turns).
        
        
        """

        stat = {}
        line = 0
        if self.get_typegame(morgue[line])=="Sprint":
            # TODO Manage sprint game (different stat ?)
            return stat
        stat[StatColumn.version] = self.get_version(morgue[line])

        # Score & main Stats
        # example string :
        # 64 Olivier the Skirmisher (level 3, -1/34 HPs)
        line = line + 2
        curline = morgue[line]
        stat[StatColumn.score] = int(curline[:curline.find(' ')])
        stat[StatColumn.name] = curline[curline.find(' ') + 1:curline.find('the') - 1]
        stat[StatColumn.surname] = curline[curline.find('the '):curline.find('(') - 1]
        stat[StatColumn.level] = curline[curline.find('level ') + 6:curline.find(',')]
        stat[StatColumn.hp] = curline[curline.find('/') + 1:curline.find('HP') - 1]

        # Race & Background
        # example string :
        # Began as a Minotaur Berserker on Aug 19, 2016.
        line = line + 1
        curline = morgue[line]
        linetab = curline.strip().split(' ')
        stat[StatColumn.species] = linetab[3]
        if stat[StatColumn.species] == "High":
        # High Elf
            stat[StatColumn.species] = stat[StatColumn.species] +" "+ linetab[4]
            stat[StatColumn.background] = linetab[5]
        else:
            stat[StatColumn.background] = linetab[4]
        dateidx=len(linetab)-9
        if len(linetab) > 9:
            stat[StatColumn.background] = stat[StatColumn.background] + ' ' + linetab[5]
        # Date
        stat[StatColumn.datestart] = self.convert_date(linetab[7+dateidx] , linetab[6+dateidx] ,linetab[8+dateidx])


        # Find religion
        line = line + 1
        curline = morgue[line].strip()
        if curline.startswith('Was'):
            if curline.find('Was an') > -1:
                stat[StatColumn.religion_rank] = curline[curline.find('Was an') + 6: curline.find(' of ')]
            elif curline.find('Was the') > -1:
                stat[StatColumn.religion_rank] = curline[curline.find('Was the') + 7: curline.find(' of ')]
            else:
                stat[StatColumn.religion_rank] = curline[curline.find('Was a') + 5: curline.find(' of ')]

            stat[StatColumn.god] = curline[curline.find(' of ') + 4:curline.find('.')]
        else:
            stat[StatColumn.religion_rank] = 'None'
            stat[StatColumn.god] = 'None'
            line = line - 1

        # Cause of death
        line = line + 1
        curline = morgue[line]
        stat[StatColumn.escaped] = False
        stat[StatColumn.orb] = False
        stat[StatColumn.runes] = 0


        if morgue[line + 1].strip().startswith("... invoked"):
            linetab = morgue[line + 1].strip().split(' ')
            stat[StatColumn.death_cause] = ' '.join(linetab[4:])
        elif curline.strip().lower().startswith('escaped'):
            stat[StatColumn.death_cause] = 'Not Dead'
            stat[StatColumn.escaped] = True
            stat[StatColumn.orb] = True
        else:

            linetab = curline.strip().lower().split(' ')
            if linetab[len(linetab) - 1].endswith(")"):
                del linetab[len(linetab) - 1]
                del linetab[len(linetab) - 1]

            if linetab[2] == "afar":
                del linetab[1]
                del linetab[1]

            if linetab[0]== "blown":
                del linetab[1]
            if linetab[1] == "with"  :
                while linetab[1] != "by":
                    del linetab[1]

            if linetab[0].startswith('...'):
                stat[StatColumn.death_cause] = 'Not Dead'
            elif linetab[0].lower()=='quit':
                stat[StatColumn.death_cause] = 'Quit'
            elif linetab[0].lower()=='got' or linetab[0].lower()=='safely':
                stat[StatColumn.death_cause] = 'Not Dead'
                stat[StatColumn.escaped] = True
            else:
                if linetab[1] == "by" or linetab[1] == "to":
                    if linetab[2] == "a" or linetab[2] == "an":
                        stat[StatColumn.death_cause] = ' '.join(linetab[3:])
                    else:
                        stat[StatColumn.death_cause] = ' '.join(linetab[2:])

                if linetab[1] == "themself":
                    stat[StatColumn.death_cause] = 'Himself (' + ' '.join(linetab[4:]) + ')'
                    stat[StatColumn.self_kill] = True
                else:
                    stat[StatColumn.self_kill] = False

                if stat[StatColumn.death_cause].find('\'s ghost') > -1:
                    stat[StatColumn.death_cause] = "Player" + stat[StatColumn.death_cause][
                                                              stat[StatColumn.death_cause].find('\'s ghost'):]
        if stat[StatColumn.escaped]:
             stat[StatColumn.dungeon_level] = "n/a"
             stat[StatColumn.dungeon] = "n/a"
        else:
            if stat[StatColumn.death_cause] != 'Quit':
                # dungeon & level
                while not (morgue[line].strip().lower().startswith('... on level') or morgue[line].strip().lower().startswith('... in a')):
                    line = line + 1

            linetab = morgue[line].strip().lower().split(' ')

            if stat[StatColumn.death_cause] == 'Quit':
                if linetab[5]=="treasure":
                    # Quit on Treasure trove
                    stat[StatColumn.dungeon_level] = "n/a"
                    stat[StatColumn.dungeon] = "Treasure trove"
                elif linetab[5]=="ecumenical":
                    # Quit on Treasure trove
                    stat[StatColumn.dungeon_level] = "n/a"
                    stat[StatColumn.dungeon] = "Ecumenical temple"
                else:
                    stat[StatColumn.dungeon_level] = linetab[5]
                    stat[StatColumn.dungeon] = linetab[8]
            if len(linetab) > 4:
                if linetab[3]=="ice":
                # in an ice cave
                    stat[StatColumn.dungeon_level] ="n/a"
                    stat[StatColumn.dungeon] = "ice cave"
                else:
                    stat[StatColumn.dungeon_level] = linetab[3]
                    stat[StatColumn.dungeon] = linetab[6]
            else:
                stat[StatColumn.dungeon] = linetab[3]
                stat[StatColumn.dungeon_level] = 'n/a'

            if stat[StatColumn.dungeon].endswith('.'):
                stat[StatColumn.dungeon] = stat[StatColumn.dungeon][:-1]

        stat[StatColumn.dun_lev] = stat[StatColumn.dungeon] + ":" + stat[StatColumn.dungeon_level]
        # Game duration
        line = 4
        while not morgue[line].strip().startswith('The game lasted'):
            line = line + 1

        linetab = morgue[line].strip().split(' ')
        stat[StatColumn.duration] = linetab[3]
        stat[StatColumn.turns] = linetab[4][1:]

        return stat

    @staticmethod
    def get_version(line):
        # example line :
        # Dungeon Crawl Stone Soup version 0.18.1 (tiles) character file.
        """
        Extract version information from the line
        :param line: the line of the morgue file
        :return: the version
        """
        idxv = line.find('version ') + 8
        idxc = line.find(' character')
        return line[idxv:idxc]
    @staticmethod
    def get_typegame(line):
        header=line.split()
        return header[1]
    @staticmethod
    def convert_date(day,month,year):
        # from DCSS source: hiscores.cc line 532
        months=[ "Jan", "Feb", "Mar", "Apr", "May", "June","July", "Aug", "Sept", "Oct", "Nov", "Dec"]
        rdate = datetime.date(int(year[:-1]),months.index(month)+1,int(day[:-1]))
        return rdate


