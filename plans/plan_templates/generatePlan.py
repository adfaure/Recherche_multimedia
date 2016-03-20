#!/usr/bin/python
import os
from datetime import datetime
import sys
import ConfigParser
import getopt
import subprocess
import logging
from scripts.utils import config_section_map
from string import Template


def main(argv):
    ###############################
    # Getting programme options
    ###############################
    help_str = 'no help provided'
    try:
        opts, args = getopt.getopt(argv, "ho:t:c:", ["config=", "template=", "output-folder="])
    except getopt.GetoptError as err:
        print help_str
        print str(err)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print help_str
            sys.exit()
        elif opt in ("-t", "--template"):
            url_list = arg
        elif opt in ("-o", "--output-folder"):
            res_folder = arg
        elif opt in ("-c", "--config"):
            config_file = arg

    #########################
    # Chargement de la config
    #########################
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    config_general = config_section_map(config, 'General')

    #########################
    # Configuration du logger
    #########################
    log_dir = config_general['log_dir']

    now = datetime.now()
    date_str = str(now.day) + '_' + str(now.hour) + '_' + str(now.minute) + "_" + str(now.second) + "_" + str(now.microsecond)
    logfile_name = os.path.basename(__file__).split('.')[0] + '-' + date_str + '.log'
    logging.basicConfig(filename=log_dir + '/' + logfile_name, level=logging.DEBUG)

    ##########################
    # Create output dir
    ##########################
    logging.info("results_dir = " + res_folder)
    if not os.path.exists(res_folder):
        logging.info('no output dir creating at ' + res_folder)
        if not subprocess.call(['mkdir', '-p', res_folder]) == 0:
            logging.warning('cannot create output dir, aborting')
            sys.exit(1)
    logging.info('output dir is ' + res_folder)
    gvalues = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    wvalues = [1, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 21, 22, 23, 24]
    with open(url_list, "r") as outfile:
        template = Template(outfile.read())
        for g in gvalues:
            for w in wvalues:
                name = 'g-'+str(g)+'_w-'+str(w)
                with open(res_folder + "/" + name + ".ini", "w") as plan:
                    config = template.substitute(g=g, w=w, name=name)
                    plan.write(config)

if __name__ == "__main__":
    main(sys.argv[1:])
