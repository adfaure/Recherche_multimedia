#!/usr/bin/python
import os
import subprocess
import timeit
from datetime import datetime
import sys
import getopt
import logging
import ConfigParser
from utils import config_section_map


def main(argv):
    ###############################
    # Getting program options
    ###############################
    help_str = 'svm-train.py -c <concepts list>'
    try:
        opts, args = getopt.getopt(argv, "h", ["samples=", "results=",
                                               "config=", "nb-clusters=",
                                               "nb-iter="])
    except getopt.GetoptError as err:
        print help_str
        print str(err)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print help_str
            sys.exit()
        elif opt in "--config":
            config_file = arg
        elif opt in "--samples":
            data = arg
        elif opt in "--results":
            results = arg
        elif opt in "--nb-clusters":
            nb_clusters = arg
        elif opt in "--nb-iter":
            nb_iter = arg


    #########################
    # Chargement de la config
    #########################
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    config_general = config_section_map(config, 'General')
    config_scripts = config_section_map(config, 'Scripts')

    #########################
    # Configuration du logger
    #########################
    log_dir = config_general['log_dir']

    now = datetime.now()
    date_str = str(now.day) + '_' + str(now.hour) + '_' + str(now.minute) + "_" + str(now.second) + "_" + str(now.microsecond)
    logfile_name = os.path.basename(__file__).split('.')[0] + '-' + date_str + '.log'
    logging.basicConfig(filename=log_dir + '/' + logfile_name, level=logging.DEBUG)

    if 'data'not in locals() or not os.path.exists(data):
        logging.warning("no data")
        exit(1)

    if 'nb_clusters' not in locals():
        logging.warning("need to specify the number of clusters needed for kmeans")
        exit(1)
    logging.info("running with " + nb_clusters + " clusters to generate")

    if 'nb_iter' not in locals():
        logging.warning("need to specify the number of max iterations")
        exit(1)
    logging.info("running with " + nb_iter + " nb iterations")

    ########################################
    # Creation du fichier et dossier pour les resultats
    ########################################
    logging.info("results_dir = " + results)
    result_name = os.path.basename(results)
    results_dir = os.path.dirname(results)
    if not os.path.exists(results_dir):
        logging.info('no output dir creating at ' + results_dir)
        if not subprocess.call(['mkdir', '-p', results_dir]) == 0:
            logging.warning('cannot create output dir, aborting')
            sys.exit(1)
    logging.info('output dir is ' + results_dir)

    ####################
    # Creation de la commande
    ####################
    kmeans_script = config_scripts['kmeans']
    command = "R --slave --no-save --no-restore --no-environ --args "
    command += data + " " + nb_clusters + " " + results + " " + nb_iter + " < " + kmeans_script

    logging.info("command : " + command)
    begin_time = timeit.default_timer()
    #########################
    # Lancement du clustering
    #########################
    os.system(command)
    end_time = timeit.default_timer()
    logging.info('end after  ' + str(end_time - begin_time))

if __name__ == "__main__":
    main(sys.argv[1:])
