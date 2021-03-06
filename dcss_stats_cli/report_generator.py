from dcss_stats.game_stats import GameStats,StatColumn
from dcss_stats import __version__
from datetime import datetime
from collections import OrderedDict

import csv
import operator

def generate_report(output,config,gamestats):


    output.start()
    output.write_title("DUNGEON CRAWL STONE SOUP STATISTICS")
    output.write_line("Generated by dcss_stats version "+__version__)
    output.write_line("the " + datetime.now().strftime("%d/%m/%y"))
    output.write_header("General statistics",2)
    write_general_stats(output, gamestats, gamestats.Stats)

    output.write_header("Ranking by outcome" ,2)
    stat = gamestats.get_stat_basic(StatColumn.endgame_cause)

    output.write_line(output.get_bold("End game by :"))
    for k in stat:
        output.write_line(("{} ({} time" + "s"*int(k[1]>1) + ")\n").format(k[0], k[1]))

    output.write_header("Ranking by Dungeon level ", 2)
    stat = gamestats.get_stat_basic(StatColumn.dun_lev)

    output.write_line(output.get_bold("End game in :"))
    for k in stat:
        output.write_line(("{} ({} time" + "s"*int(k[1]>1) + ")\n").format(k[0], k[1]))


    list_character = gamestats.get_character_list()
    write_percharacter_stats(output,gamestats, list_character)
    list_dunlevel=gamestats.get_stat_list(StatColumn.dun_lev)
    write_perdungeonlevel_stats(output,gamestats,list_dunlevel)

    output.complete()


    if config.globalstat==True:
        with open('global.csv', 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL,lineterminator="\n")

            header_written = False
            for s in gamestats.Stats:
                if not header_written:
                    writer.writerow(s.keys())
                    header_written = True


                writer.writerow(s.values())


    if config.scoreevol==True:    
        scorevol = gamestats.get_scoreevolution(type='day')
        with open('scorevol.csv', 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=' ',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL,lineterminator="\n")
            writer.writerow(["Date","Score"])
            writer.writerows(scorevol)

def write_percharacter_stats(output,gamestats, list_character):

    output.write_header("Per character statistic",2)
    # TODO Sort by char_name / games / orb ..?
    sorted_listchar = list_character.sort()

    for lc in list_character:
        lcstat = gamestats.get_char_filtered_stat(lc)
        output.write_header("Statistic for : {}".format(lc),3)
        write_general_stats(output,gamestats,lcstat)

        sorted_simplestat = gamestats.get_stat_basic(StatColumn.endgame_cause, lcstat)
        output.write_line(output.get_bold("End game by :"))
        for k in sorted_simplestat:
            output.write_line(("{} ({} time" + "s" * int(k[1] > 1) + ")\n").format(k[0], k[1]))

        sorted_simplestat = gamestats.get_stat_basic(StatColumn.dun_lev, lcstat)
        output.write_line(output.get_bold("End game in :"))
        for k in sorted_simplestat:
            output.write_line(("{} ({} time" + "s" * int(k[1] > 1) + ")\n").format(k[0], k[1]))




def write_perdungeonlevel_stats(output,gamestats, list_dungeonlevel):
    output.write_header("Per dungeon statistic",2)

    # TODO Sort by char_name / games / orb ..?
    list_dungeonlevel.sort()

    for lc in list_dungeonlevel:
        lcstat = gamestats.get_filtered_stat(None,lc,StatColumn.dun_lev)


        output.write_separator()
        output.write_header("{}".format(lc),3)

        write_general_stats(output,gamestats,lcstat)

        simplestat = gamestats.get_stat_basic(StatColumn.endgame_cause, lcstat)

        output.write_line(output.get_bold("End game by :"))
        for k in simplestat:
            output.write_line(("{} ({} time" + "s" * int(k[1] > 1) + ")\n").format(k[0], k[1]))

def write_general_stats(output,gamestats,lcstat):
    output.write_separator()
    output.write_line("Number of games played : {}".format(gamestats.get_number_of_game(lcstat)))
    output.write_line("Best game : {}".format(gamestats.get_best_game(lcstat)))
    output.write_line("Average Score : {}".format(gamestats.get_averagescore(lcstat)))

    orbstat = gamestats.get_filtered_stat(lcstat,True,StatColumn.orb)

    output.write_line(output.get_bold("Escaped with orb: {}".format(len(orbstat))))
    output.write_separator()