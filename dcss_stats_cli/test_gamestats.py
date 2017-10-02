import csv
from os import  remove, path,getcwd
from enum import Enum
from os.path import isfile, join
from argparse import ArgumentParser
from dcss_stats.game_stats import GameStats,StatColumn
from dcss_stats.core import logger,config
from inspect import getargspec
from dcss_stats import __version__



###############
# MAIN Stuff
################

class OutputType(Enum):
    Console = 1
    TextFile = 2
    Markdown = 3
    HTML = 4


# TODO manage program output type
Output = OutputType.Console
OutputFile = r'game_stats.txt'


def write_file(data):
    """
    this function write data to file
    :param data:
    :return:
    """
    # TODO manage program output type
    file_name = OutputFile
    with open(file_name, 'a') as x_file:
        x_file.write(data + "\n")


def write_percharacter_stats(gamestats, list_character):
    write_file("-" * 50)
    write_file("-" * 50)
    write_file("                   PER CHARACTER STATISTIC")
    write_file("-" * 50)
    write_file("-" * 50)
    for lc in list_character:
        lcstat = gamestats.get_char_filtered_stat(lc)
        write_file("-" * 50)
        write_file("Statistic for : {}".format(lc))
        write_file("Number of games played : {}".format(gamestats.get_number_of_game(lcstat)))
        sorted_simplestat = gamestats.get_stat_basic(StatColumn.death_cause, lcstat)
        s = "\n"
        for k in sorted_simplestat:
            s = s + "{} ({} times)\n".format(k[0], k[1])
        write_file("Killed most by : {}".format(s))

        sorted_simplestat = gamestats.get_stat_basic(StatColumn.dun_lev, lcstat)
        s = "\n"
        for k in sorted_simplestat:
            s = s + "{} ({} times)\n".format(k[0], k[1])
        write_file("Killed most in : {}".format(s))

        write_file("Best game : {}".format(gamestats.get_best_game(lcstat)))
        write_file("Average Score : {}".format(gamestats.get_averagescore(lcstat)))


def write_perdungeonlevel_stats(gamestats, list_dungeonlevel):
    write_file("-" * 50)
    write_file("-" * 50)
    write_file("                   PER DUNGEON STATISTIC")
    write_file("-" * 50)
    write_file("-" * 50)
    for lc in list_dungeonlevel:
        lcstat = gamestats.get_filtered_stat(lc,StatColumn.dun_lev)
        write_file("-" * 50)
        write_file("Statistic for : {}".format(lc))
        write_file("Number of games played : {}".format(gamestats.get_number_of_game(lcstat)))
        sorted_simplestat = gamestats.get_stat_basic(StatColumn.death_cause, lcstat)
        s = "\n"
        for k in sorted_simplestat:
            s = s + "{} ({} times)\n".format(k[0], k[1])
        write_file("Killed most by : {}".format(s))


        write_file("Best game : {}".format(gamestats.get_best_game(lcstat)))
        write_file("Average Score : {}".format(gamestats.get_averagescore(lcstat)))


def _args(argv=None):
    """ Parse command line arguments.
    """
    parser = ArgumentParser()
    parser.add_argument("-c", "--config", action="append",
            help="config file [./config.yml]")
    parser.add_argument("-v", "--version", action="version",
            version="dcss-stats {:s}".format(__version__),
            help="print version and exit")
    parser.add_argument("-w", "--warn", default="INFO",
            help="logger warning level [WARN]")
    parser.add_argument("-p", "--path", type=str, help="DCSS path")

    args = parser.parse_args(argv)
    if not args.config:
        # Don't specify this as an argument default or else it will always be
        # included in the list.
        args.config = join(getcwd(), "config.yml")
    return args


def main(argv=None):
    """
    Main function (heh :)
    """
    args = _args(argv)
    #args.morgue_path = join(args.path, 'morgue')
    f = open("dcss_stats.log", "a", encoding="utf-8")
    logger.start(args.warn,f)
    logger.info("version {}".format(__version__))
    config.load(args.config)
    config.core.logging = args.warn

    if (args.path is None) and (config.path is None):
        msg="DCSS Path must be provided, either by command line (-p) either by editing config.yml"
        print(msg)
        logger.error(msg)
        return 2

    if (config.path is None):
        config.path = args.path
    config.morgue_path = join(config.path, 'morgue')

    try:
        FileOuput(config)
    except RuntimeError as err:
        logger.critical(err)
        return 1
    logger.debug("successful completion")
    return 0


def FileOuput(config):



    if isfile(OutputFile):
        remove(OutputFile)

    gamestats = GameStats(config)

    gamestats.analyze()

    write_file("-" * 50)
    write_file("-" * 50)
    write_file("Number of games played : {}".format(gamestats.get_number_of_game()))
    write_file("-" * 50)
    write_file("-" * 50)

    stat = gamestats.get_stat_basic(StatColumn.death_cause)
    s = "\n"
    for k in stat:
        s = s + "{} ({} times)\n".format(k[0], k[1])
    write_file("Killed most by : {}".format(s))

    stat = gamestats.get_stat_basic(StatColumn.dun_lev)

    s = "\n"
    for k in stat:
        s = s + "{} ({} times)\n".format(k[0], k[1])
    write_file("Killed most in : {}".format(s))

    write_file("Best game : {}".format(gamestats.get_best_game()))
    write_file("Average Score : {}".format(gamestats.get_averagescore()))
    write_file("-" * 50)

    list_character = gamestats.get_character_list()
    write_percharacter_stats(gamestats, list_character)
    list_dunlevel=gamestats.get_stat_list(StatColumn.dun_lev)
    write_perdungeonlevel_stats(gamestats,list_dunlevel)
    scorevol = gamestats.get_scoreevolution(type='day')

    with open('scorevol.csv', 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=' ',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["Date","Score"])
        writer.writerows(scorevol)



if __name__ == "__main__":
    main()
