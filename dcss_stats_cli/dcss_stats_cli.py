from os import  listdir,getcwd
from os.path import join,isdir
from argparse import ArgumentParser
from dcss_stats.core import logger,config
from dcss_stats import __version__
from report_generator import generate_report
import sys,inspect
import output

# this is the package we are inspecting -- for example 'email' from stdlib
import email

package = output


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
    if (not "morgue_path" in config.keys()   ):
        config.morgue_path = join(config.path, 'morgue')
    if (config.output is None):
        config.output = args.output
    if config.scoreevol is None:
        config.scoreevol=args.scoreevol



    output_module = __import__("output."+config.output, fromlist="dummy")
    for name, obj in inspect.getmembers(output_module):
        if inspect.isclass(obj):
            output_object = obj()
            break


    # looks like shit, but don't complain ! http://python.net/~goodger/projects/pycon/2007/idiomatic/handout.html#eafp-vs-lbyl
    try:
        output_object.filename = config.outputfilename
    except:
        pass


    try:
        generate_report(output_object,config)
    except RuntimeError as err:
        logger.critical(err)
        return 1
    logger.debug("successful completion")
    return 0


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
    parser.add_argument("-o", "--output", default="text",
                        help="output [text]")
    parser.add_argument("-s", "--scorevol", default="False",
                        help="generate CSV with score evolution values [False]")


    args = parser.parse_args(argv)
    if not args.config:
        # Don't specify this as an argument default or else it will always be
        # included in the list.
        args.config = join(getcwd(), "config.yml")
    return args



if __name__ == "__main__":
    main()