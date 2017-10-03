from dcss_stats.game_stats import GameStats,StatColumn
import csv

def generate_report(output,config):


    gamestats = GameStats(config)

    gamestats.analyze()
    
    output.write_header("DUNGEON CRAWL SOUP STATISTICS",1)

    output.write_header("General statistics",2)
    output.write_line("Number of games played : {}".format(gamestats.get_number_of_game()))
    output.write_line("Best game : {}".format(gamestats.get_best_game()))
    output.write_line("Average Score : {}".format(gamestats.get_averagescore()))

    output.write_header("Ranking by Death Cause " ,2)
    stat = gamestats.get_stat_basic(StatColumn.death_cause)
    s = "\n"
    for k in stat:
        s = s + "{} ({} times)\n".format(k[0], k[1])
    output.write_line("Killed most by : {}".format(s))

    output.write_header("Ranking by Dungeon level ", 2)
    stat = gamestats.get_stat_basic(StatColumn.dun_lev)
    s = "\n"
    for k in stat:
        s = s + "{} ({} times)\n".format(k[0], k[1])
    output.write_line("Killed most in : {}".format(s))


    list_character = gamestats.get_character_list()
    write_percharacter_stats(output,gamestats, list_character)
    list_dunlevel=gamestats.get_stat_list(StatColumn.dun_lev)
    write_perdungeonlevel_stats(output,gamestats,list_dunlevel)
    
    
    if config.scoreevol==True:    
        scorevol = gamestats.get_scoreevolution(type='day')
        with open('scorevol.csv', 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=' ',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["Date","Score"])
            writer.writerows(scorevol)

def write_percharacter_stats(output,gamestats, list_character):

    output.write_header("PER CHARACTER STATISTIC",2)
    for lc in list_character:
        lcstat = gamestats.get_char_filtered_stat(lc)
        output.write_separator()
        output.write_line("Statistic for : {}".format(lc))
        output.write_line("Number of games played : {}".format(gamestats.get_number_of_game(lcstat)))
        sorted_simplestat = gamestats.get_stat_basic(StatColumn.death_cause, lcstat)
        s = "\n"
        for k in sorted_simplestat:
            s = s + "{} ({} times)\n".format(k[0], k[1])
        output.write_line("Killed most by : {}".format(s))

        sorted_simplestat = gamestats.get_stat_basic(StatColumn.dun_lev, lcstat)
        s = "\n"
        for k in sorted_simplestat:
            s = s + "{} ({} times)\n".format(k[0], k[1])
        output.write_line("Killed most in : {}".format(s))

        output.write_line("Best game : {}".format(gamestats.get_best_game(lcstat)))
        output.write_line("Average Score : {}".format(gamestats.get_averagescore(lcstat)))


def write_perdungeonlevel_stats(output,gamestats, list_dungeonlevel):
    output.write_header("PER DUNGEON STATISTIC",2)
    for lc in list_dungeonlevel:
        lcstat = gamestats.get_filtered_stat(lc,StatColumn.dun_lev)
        output.write_separator()
        output.write_line("Statistic for : {}".format(lc))
        output.write_line("Number of games played : {}".format(gamestats.get_number_of_game(lcstat)))
        sorted_simplestat = gamestats.get_stat_basic(StatColumn.death_cause, lcstat)
        s = "\n"
        for k in sorted_simplestat:
            s = s + "{} ({} times)\n".format(k[0], k[1])
        output.write_line("Killed most by : {}".format(s))


        output.write_line("Best game : {}".format(gamestats.get_best_game(lcstat)))
        output.write_line("Average Score : {}".format(gamestats.get_averagescore(lcstat)))