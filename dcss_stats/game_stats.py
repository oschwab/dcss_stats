
import operator
import datetime
from enum import Enum, auto
from os import listdir
from os.path import isfile, join, exists

from dcss_stats.core.dcss_data import get_short_background, get_short_specie
from dcss_stats.core.eventhook import EventHook
from .core import logger,utils
import statistics


class StatColumn(Enum):
    row_number=0
    dungeon = auto()
    game_rank = auto()
    game_id=auto()
    background = auto()
    species = auto()
    datestart= auto()
    datedeath=auto()
    char_name = auto()
    hp = auto()
    surname = auto()
    duration = auto()
    dun_lev = auto()
    xp_level = auto()
    turns = auto()
    god = auto()
    religion_rank = auto()
    filename = auto()
    version = auto()
    endgame_cause = auto()
    poisoned = auto()
    self_kill = auto()
    dungeon_level = auto()
    score = auto()
    escaped = auto()
    orb=auto()
    runes=auto()



    def __str__(self):
       labels=  {
           self.dungeon: 'Dungeon',
           self.background: 'Background',
           self.datestart: 'Start of game',
           self.datedeath: 'Death date',
           self.char_name: 'Name',
           self.hp: 'Hp',
           self.surname: 'Surname',
           self.duration: 'Duration',
           self.dun_lev: 'Dun lev',
           self.xp_level: 'Xp level',
           self.turns: 'Turns',
           self.god: 'God',
           self.religion_rank: 'Religion rank',
           self.filename: 'Filename',
           self.species: 'Species',
           self.version: 'Version',
           self.endgame_cause: 'Endgame cause',
           self.self_kill: 'Self kill',
           self.dungeon_level: 'Branch level',
           self.score: 'Score',
           self.escaped: 'Escaped',
           self.orb: 'Orb',
           self.runes: 'Runes',
           self.row_number: '#',
           self.game_id: 'Game number',
           self.game_rank: 'Overall rank',
           self.poisoned: 'Poisoned'
                   }
       if self in labels.keys():
           return(labels[self])
       else:
           return("?"+str(self._value_))




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
    'char_name': 'Awutz',
    'hp': '30',
    'surname': 'the Chiller',
    'duration': '00:11:56',
    'dun_lev': 'Dungeon:1',
    'xp_level': '4',
    'turns': '2120',
    'god': 'None',
    'religion_rank': 'None',
    'filename': 'morgue-Awutz-20160912-104224.txt',
    'species': 'Merfolk',
    'version': '0.18.1 (tiles)',
    'endgame_cause': 'giant frog',
    'self_kill' : False,
    'dungeon_level': '1',
    'escaped' : True,
    'orb ': True,
    'runes' : 3,
    'score': 63}
    """

    Stats = []

    onChange = EventHook()
    onCompleted = EventHook()
    current_file = 0


    def __init__(self, configuration):
        """
        Constructor
        :param morguepath: Path to crawl morgue files (ex: C:\dcss\morgue )
        """
        self.MorguePath = configuration.get('morgue_repository')


        self.MorgueFiles = []

        if exists(self.MorguePath):
            for f in listdir(self.MorguePath):
                if isfile(join(self.MorguePath, f)) and f[:6] == "morgue" and f[-3:] == "txt":
                    self.MorgueFiles.append(f)

    def analyze(self):

        """
        Analyze morgue files in :MorguePath and fill :Stats
        """
        self.Stats = []
        self.current_file=0
        for morgue in self.MorgueFiles:
            logger.info("Analyzing " + morgue)
            with open(join(self.MorguePath, morgue)) as file:
                content = file.readlines()

            stat = self.get_information(content,morgue)
            if len(stat)>0:
                # Not a Sprint game, for ex.
                stat[StatColumn.filename] = morgue
                self.Stats.append(stat)

                ## control check
                if stat[StatColumn.dungeon_level] == "n/a:n/a":
                    logger.error("invalid dungeon+level in " + stat[StatColumn.filename])
                if stat[StatColumn.endgame_cause].find("cyclops") > 0 or  stat[StatColumn.endgame_cause].startswith("level"):
                    logger.error("invalid endgame_cause in " + stat[StatColumn.filename])

            self.current_file=self.current_file+1
            print("{}/{}".format(self.current_file,len(self.MorgueFiles)))
            self.onChange.fire()


        # Finally, sort and number the games

        # sort by date
        self.Stats = self.sort_stat(StatColumn.datedeath)
        self.current_file=0
        for s in self.Stats:
            self.current_file=self.current_file+1
            s[StatColumn.game_id] = self.current_file

        # sort by score
        self.Stats = self.sort_stat(StatColumn.score,True)
        idx=0
        for s in self.Stats:
            idx=idx+1
            s[StatColumn.game_rank] = idx





        self.onCompleted.fire()

    def sort_stat(self,column,preverse=False,stat=None):
        """
        sort the given stat structure (global one if none)
        :param column: the column for sort
        :param preverse: reverse orcer or not
        :param stat: the stat structure
        :return:  stat structure sorted on column
        """
        if stat is None:
            stat = self.Stats
        stat = sorted(stat, key=operator.itemgetter(column), reverse=preverse)
        idx=0
        for s in stat:
            idx=idx+1
            s[StatColumn.row_number] =idx
        return stat
        
    def get_species_for_job(self,job, stat=None):
        """
        :return: the list of species with selected jobs
        """
        if stat is None:
            stat = self.Stats
        specs=()
        for s in stat:
            if s[StatColumn.background]==job:
                if not s[StatColumn.species] in specs:
                    specs = specs + (s[StatColumn.species],)

        return(specs)


    def get_job_for_species(self,species, stat=None):
        """
        :return: the list of species with selected jobs
        """
        if stat is None:
            stat = self.Stats
        jobs=()
        for s in stat:
            if s[StatColumn.species]==species:
                if not s[StatColumn.background] in jobs :
                    jobs = jobs + (s[StatColumn.background] ,)

        return(jobs)


    def get_number_of_game(self, stat=None):
        """
        :return: the number of game played in global or param stat structure
        """
        if stat is None:
            stat = self.Stats

        return len(stat)

    def get_char_filtered_stat(self, character, stat=None):
        """
        returns a stat structure filtered for character
        :param character: the character (race+job) to filter
        :return: stat structure
        """
        if stat is None:
            stat = self.Stats

        filtstat = []
        for s in stat:
            sb = s[StatColumn.species] + ' ' + s[StatColumn.background]
            if sb == character:
                filtstat.append(s)
        return filtstat

    def get_wins(self, stat=None):
        """
        returns a stat structure filtered for character
        :param character: the character (race+job) to filter
        :return: stat structure
        """
        if stat is None:
            stat = self.Stats
        wins=0
        for s in stat:
            if  s[StatColumn.escaped]:
                wins = wins + 1
        return wins

    def get_filtered_stat(self, stat,value,column=StatColumn.dungeon_level ):
        """
             returns a stat structure filtered for column
        :param column: the column to filter
        :param value:  the value of the column
        :return: stat structure
        """

        if stat is None:
            stat = self.Stats

        filtstat = []
        rowid=0
        for s in stat:
            if s[column] == value:
                rowid=rowid+1
                s[StatColumn.row_number] = rowid
                filtstat.append(s)
        return filtstat

    def get_char_filtered_stat(self, background,species,stat=None):
        """

        :param stat:
        :param value:
        :param background:
        :param species:
        :return:
        """
        if stat is None:
            stat = self.Stats

        filtstat = []
        rowid=0
        for s in stat:
            if (s[StatColumn.background] == background) and (s[StatColumn.species] == species)  :
                rowid=rowid+1
                s[StatColumn.row_number] = rowid
                filtstat.append(s)
        return filtstat

    def get_average_score(self,stat=None):
        if stat is None:
            stat = self.Stats
        if len(stat)==0 :
            return 0
        avg=0
        scores = [c[StatColumn.score] for c in stat]
        return (round((sum(scores) / float(len(scores)))))



    def get_top(self,stat=None,top=10):
        if stat is None:
            stat = self.Stats
        topstat=[]
        cpt = 0
        for s in stat:
            cpt = cpt + 1
            topstat.append(s)
            if cpt == top:
                break
        return topstat


    def get_character_list(self):
        """
        Get the list of characters types (race+job) found in morgue
        :return: a . list . of . characters
        """
        list_char = []
        for s in self.Stats:
            sb = (s[StatColumn.species] ,s[StatColumn.background])
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

    def exclude_result(self,column,stat):
        """
        verify if value for this column must be excluded from stats
        :param column: the stat column
        :param value:  the value to verify
        :return: True if value must be excluded
        """
        result = False
        if column==StatColumn.dun_lev and stat[StatColumn.escaped] == True:
            result =True
        return result

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
            if not self.exclude_result(column,s):
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
            sorted_simplestat = simplestat

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

    def get_playtime(self, stat=None):
        """
        returns the total play time
        :param stat: the stat structure ; if None global one is taken
        :return: the total time (in minutes)
        """
        if stat is None:
            stat = self.Stats
        ttpt = 0
        if len(stat) == 0:
            return 0
        for s in stat:
            d=s[StatColumn.duration]
            ttpt = ttpt + int(d[-2:]) + int(d[-5:-3]) * 60 + int(d[:2]) * 60 * 60


        return(ttpt)


    def get_median_score(self, stat=None):
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

        score = []
        for st in stat:
            score.append(st[StatColumn.score])
        return round(statistics.median(score))


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

    def get_avg_score_per_month(self,stat=None):
        if stat is None:
            stat = self.Stats
        evol={}

        filter="%y-%m"

        for s in stat:
            key=s[StatColumn.datestart].strftime(filter)
            if not key in evol:
                evol[key]=[]
            evol[key].append(s[StatColumn.score])

        ret=[]
        for key, value in sorted(evol.items()):
            ret.append([key,int(sum(value)/len(value))])

        return ret

    def apply_text_filter(self,filter,regex,config,stat=None):
        if stat is None:
            stat = self.Stats
        retstat = []
        for st in stat:
            filename=join(config.get('morgue_repository'), st[StatColumn.filename])
            if utils.file_contains(filename,filter,regex):
                retstat.append(st)
        return retstat


    def get_information(self, morgue,morguefile):
        """
        Create an entry for the stat structure
        :param morgue: the morgue file (array of string)
        :param morguefile : the morgue file char_name
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

        line = line + 1
        while (not morgue[line][0].isdigit()):
            line = line + 1
        curline = morgue[line]

        stat[StatColumn.score] = int(curline[:curline.find(' ')])
        stat[StatColumn.char_name] = curline[curline.find(' ') + 1:curline.find('the') - 1]
        stat[StatColumn.surname] = curline[curline.find('the '):curline.find('(') - 1]
        stat[StatColumn.xp_level] = curline[curline.find('level ') + 6:curline.find(',')]
        stat[StatColumn.hp] = curline[curline.find('/') + 1:curline.find('HP') - 1]
        datestr=morguefile[len(morguefile)-len("YYYYMMDD-HHMMSS")-4:-4]
        stat[StatColumn.datedeath] = datetime.datetime.strptime(datestr,"%Y%m%d-%H%M%S")




        # Race & Background
        # example string :
        # Began as a Minotaur Berserker on Aug 19, 2016.
        line = line + 1
        curline = morgue[line]
        linetab = curline.strip().split(' ')
        stat[StatColumn.species] = linetab[3]
        idx_on = 5
        if stat[StatColumn.species] in ["High","Dark","Deep","Hill","Vine"]:
        # High Elf
            stat[StatColumn.species] = stat[StatColumn.species] +" "+ linetab[4]
            stat[StatColumn.background] = linetab[5]
            idx_on = idx_on + 1
            if linetab[6] != "on":
                # ... Elementalist
                stat[StatColumn.background] = stat[StatColumn.background] + ' ' + linetab[6]
                idx_on = idx_on + 1
        else:
            stat[StatColumn.background] = linetab[4]
        if linetab[idx_on] != "on":
            stat[StatColumn.background] = stat[StatColumn.background] + ' ' + linetab[idx_on]



        # if len(linetab) > 9 and stat[StatColumn.background] != linetab[5] :
        #      stat[StatColumn.background] = stat[StatColumn.background] + ' ' + linetab[5]



        # Date
        dateidx = len(linetab) - 9
        stat[StatColumn.datestart] = self.convert_date(linetab[7+dateidx] , linetab[6+dateidx] ,linetab[8+dateidx])


        # Find religion
        line = line + 1
        curline = morgue[line].strip()
        if curline.startswith('Was') and not curline.startswith('Was drained') :
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


        #
        # Cause of end game
        #

        line = line + 1
        curline = morgue[line]
        stat[StatColumn.escaped] = False
        stat[StatColumn.orb] = False
        stat[StatColumn.self_kill] = False
        stat[StatColumn.runes] = 0

        if morgue[line + 1].strip().startswith("... invoked"):
            linetab = morgue[line + 1].strip().split(' ')
            if linetab[3] in ["a","an"]:
                stat[StatColumn.endgame_cause] = ' '.join(linetab[4:])
            else:
                stat[StatColumn.endgame_cause] = ' '.join(linetab[3:])

        elif curline.strip().lower().startswith('escaped'):
            stat[StatColumn.endgame_cause] = 'Escaped'
            stat[StatColumn.escaped] = True
            stat[StatColumn.orb] = True
            linetab = morgue[line + 1].strip().split(' ')
            #stat[StatColumn.runes] = int(linetab[2])

        elif curline.strip().lower().startswith('asphyxiated'):
            stat[StatColumn.endgame_cause] = 'Asphyxiated'
        elif curline.strip().lower().startswith('drowned'):
            stat[StatColumn.endgame_cause] = 'Drowned'
        elif curline.strip().lower().startswith('was drained'):
            stat[StatColumn.endgame_cause] = 'Drained'
        else:

            linetab = curline.strip().lower().split(' ')

            if len(linetab) <=1:
                line=line+1
                linetab = morgue[line].strip().lower().split(' ')

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

            if linetab[0].lower()=='quit':
                stat[StatColumn.endgame_cause] = 'Quit'
            elif linetab[0].lower()=='got' or linetab[0].lower()=='safely':
                stat[StatColumn.endgame_cause] = 'Escaped'
                stat[StatColumn.escaped] = True
            else:
                #  Impaled on a porcupine's spines (12 damage)
                if linetab[1] in ["by","to","on"]:
                    if linetab[2] == "a" or linetab[2] == "an":
                        stat[StatColumn.endgame_cause] = ' '.join(linetab[3:])
                    else:
                        stat[StatColumn.endgame_cause] = ' '.join(linetab[2:])

                if linetab[1] == "themself":
                    stat[StatColumn.endgame_cause] = 'Himself (' + ' '.join(linetab[4:]) + ')'
                    stat[StatColumn.self_kill] = True
                else:
                    stat[StatColumn.self_kill] = False

                if stat[StatColumn.endgame_cause].find('\'s ghost') > -1:
                    stat[StatColumn.endgame_cause] = "Player" + stat[StatColumn.endgame_cause][
                                                                stat[StatColumn.endgame_cause].find('\'s ghost'):]

        # Check if we must rectify monster effect
        quote = stat[StatColumn.endgame_cause].find("'")
        stat[StatColumn.poisoned] = ""
        if  quote > 0 :
            # stupid creature's poison
            # cacas' flame
            effect=stat[StatColumn.endgame_cause][quote+3:]
            stat[StatColumn.endgame_cause] = stat[StatColumn.endgame_cause][:quote]
            # can be  poison or ghost's poison
            if ((len(effect) >=6) and (effect[-6:]=='poison')):
                stat[StatColumn.poisoned] = "Y"



        thrown = stat[StatColumn.endgame_cause].find("thrown")
        if  thrown > 0 :
            # stone thrown by a kobold
            pos=stat[StatColumn.endgame_cause].find("by an ")
            if pos==-1:
                pos = stat[StatColumn.endgame_cause].find("by a ")
                if pos >=0:
                    pos = pos + len("by a ")
            else:
                pos = pos + len("by an ")

            if pos>=0 :
                stat[StatColumn.endgame_cause] = stat[StatColumn.endgame_cause][pos:]




        #
        # Dungeon & Level
        #

        if stat[StatColumn.escaped]:
             stat[StatColumn.dungeon_level] = "n/a"
             stat[StatColumn.dungeon] = "n/a"
        else:
            if stat[StatColumn.endgame_cause] != 'Quit':
                # dungeon & _level
                while not (morgue[line].strip().lower().startswith('... on level') or morgue[line].strip().lower().startswith('... in ')):
                    line = line + 1

            linetab = morgue[line].strip().lower().split(' ')

            if stat[StatColumn.endgame_cause] == 'Quit':

                if linetab[3] == "on":
                # Quit the game on xp_level 2 of the dungeon
                     stat[StatColumn.dungeon_level] = linetab[5]
                     stat[StatColumn.dungeon] = linetab[8]

                else:
                # Quit the game in the Ecumenical Temple.
                # Quit the game in a sewer.
                    stat[StatColumn.dungeon_level] = "n/a"
                    stat[StatColumn.dungeon] = ' ' .join(linetab [5:])

            else:
                if len(linetab) > 4:
                    if linetab[3]=="ice":
                    # in an ice cave
                        stat[StatColumn.dungeon_level] ="n/a"
                        stat[StatColumn.dungeon] = "ice cave"
                    elif linetab[3]=="desolation":
                        # desolation of salt
                        stat[StatColumn.dungeon_level] ="n/a"
                        stat[StatColumn.dungeon] = "Desolation of Salt"
                    elif linetab[3]=="labyrinth":
                        # desolation of salt
                        stat[StatColumn.dungeon_level] ="n/a"
                        stat[StatColumn.dungeon] = "labyrinth"
                    elif linetab[3] == "ecumenical":
                        # Quit on Treasure trove
                        stat[StatColumn.dungeon_level] = "n/a"
                        stat[StatColumn.dungeon] = "Ecumenical temple"
                    elif linetab[6] == "realm":
                        stat[StatColumn.dungeon_level] = linetab[3]
                        stat[StatColumn.dungeon] = "zot"
                    else:
                        stat[StatColumn.dungeon_level] = linetab[3]
                        stat[StatColumn.dungeon] = linetab[6]
                else:
                    stat[StatColumn.dungeon] = linetab[3]
                    stat[StatColumn.dungeon_level] = 'n/a'

                stat[StatColumn.dungeon] = stat[StatColumn.dungeon][0].upper() + stat[StatColumn.dungeon][1:]



            if stat[StatColumn.dungeon].endswith('.'):
                stat[StatColumn.dungeon] = stat[StatColumn.dungeon][:-1]

        stat[StatColumn.dun_lev] = stat[StatColumn.dungeon]
        if stat[StatColumn.dungeon_level]!="n/a":
            stat[StatColumn.dun_lev] = stat[StatColumn.dun_lev] +":" + stat[StatColumn.dungeon_level]
        # Game duration
        line = 4
        eof=False
        while not morgue[line].strip().startswith('The game lasted'):
            line = line + 1
            if (line == len(morgue[line])):
                eof=True
                break

        if not eof:
            linetab = morgue[line].strip().split(' ')
            stat[StatColumn.duration] = linetab[3]
            stat[StatColumn.turns] = linetab[4][1:]


            # runes
            while not morgue[line].strip().startswith('}:'):
                line = line + 1
                if (line == len(morgue)):
                    eof = True
                    break
            if not eof:
                linetab = morgue[line].strip().split(' ')
                stat[StatColumn.runes] = int(linetab[1].split('/')[0])




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


