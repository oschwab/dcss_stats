from dcss_stats.core.dcss_data import is_background, is_specie,validate_class_background
from dcss_stats.game_stats import StatColumn
from prettytable import PrettyTable
import operator

class NotEnoughParamException(Exception):
    pass

class InvalidParamException(Exception):
    pass



class StatsShell:
    configuration = None
    game_stats = None
    current_stat = None

    top_size=10

    def __init__(self, configuration, gamestats):
        self.configuration = configuration
        self.game_stats = gamestats




    def top(self,command):
        # if (len(command) ==1):
        #     raise NotEnoughParamException()

        if (len(command)>1):
            query = command[1]
            if not validate_class_background(query):
                raise InvalidParamException("parameter must be a valid character (ex: Mi) , a valid background (ex:Be) or a valid combination of the two (ex:MiBe)  ")
            spec = query[:2]
            if is_specie(spec):
                if len(query) > 2:
                    job = query[2:]
                else:
                    job=None

            else:
                job=spec
                spec=None
        else:
            query='All'
            job =None
            spec = None
        self.current_stat = self.game_stats.Stats

        if (not spec is None):
            self.current_stat = self.game_stats.get_filtered_stat(self.current_stat,spec,column=StatColumn.sspecies )

        if (not job is None):
            self.current_stat = self.game_stats.get_filtered_stat(self.current_stat, job, column=StatColumn.sbackground)

        sorted_stat = sorted(self.current_stat, key=operator.itemgetter(StatColumn.score),reverse=True)

        columns = [StatColumn.score, StatColumn.datedeath, StatColumn.dun_lev, StatColumn.endgame_cause]

        if (job is None):
            columns.append(StatColumn.sbackground)

        if (spec is None):
            columns.append(StatColumn.sspecies)


        self.printstat(self.top_size,query,columns,sorted_stat)



    def printstat(self,nbrows ,statlabel='',columns=[],stat=None ):
        if (stat is None):
            stat = self.current_stat

        #sorted_simplestat = sorted(stat.items(), key=operator.itemgetter(1), reverse=True)



        x = PrettyTable()

        colnames=[str(c) for c in columns]
        colnames.insert(0,statlabel)
        x.field_names = colnames
        cpt=0
        for s in stat:
            cpt=cpt+1
            sb = [s[x] for x in columns]
            sb.insert(0,cpt)
            x.add_row(sb)
            if cpt == nbrows:
                break


        print(x)



    def start(self):
         print("Interactive shell started")
         quit=False
         debug=True
         while(not quit):
             print("Enter command:")
             if debug:
                 cmd = 'top MiBe'
                 debug=False
             else:
                cmd = input()


             if (cmd=="q"):
                   quit=True
             else:
                 command=cmd.split(" ")
                 try:
                     getattr(self, command[0])(command)
                 except NotEnoughParamException:
                     print("Not enough parameters for command")
                 except InvalidParamException as error:
                     print("Invalid parameter value :" + repr(error))
                 except Exception as error :
                     print("unknown command : " + command[0] + " : "   + repr(error))