#!/usr/bin/python
import os
import timeit
from datetime import datetime
import sys
import getopt
import logging
import glob
import subprocess
import ConfigParser
from utils import config_section_map

########################################
# Configuration du repertoire de travail
########################################
working_dir = "work/"
if not os.path.isdir("work"):
    os.system("mkdir " + working_dir)


def main(argv):
    ###############################
    # Getting program options
    ###############################
    help_str = 'svm-train.py -c <concepts list>'
    try:
        opts, args = getopt.getopt(argv, "tc:ho:", ["concepts=", "results-dir=",
                                                    "input-svm=", "config=", "svm-args="])
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
        elif opt in "--input-svm":
            input_svm = arg
        elif opt in "--results-dir":
            results_dir = arg
        elif opt in "--svm-args":
            svm_options = arg

    #########################
    # Chargement de la config
    #########################
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    config_general = config_section_map(config, 'General')
    config_svm = config_section_map(config, 'libSvm')

    #########################
    # Configuration du logger
    #########################
    log_dir = config_general['log_dir']

    ############################
    # Initialisation de lib-svm
    ############################
    svm_train = config_svm['svm_train']

    now = datetime.now()
    script_name = os.path.basename(__file__)
    date_str = str(now.day) + '_' + str(now.hour) + '_' + str(now.minute) + "_" + str(now.second) + "_" + str(now.microsecond)
    logfile_name = os.path.basename(__file__).split('.')[0] + '-' + date_str + '.log'
    logging.basicConfig(filename=log_dir + '/' + logfile_name, level=logging.DEBUG)

    #########################
    # Init svm train_photos command
    #########################
    train_cmd = [svm_train]
    if 'svm_options' in locals():
        logging.info('svm options ' + svm_options)
        train_cmd = train_cmd + svm_options.split(' ')  # bug with space in subprocess so we have to split it here

    #########################
    # Get list of svm files
    #########################
    concepts = glob.glob(input_svm + '*.svm')
    for concept in concepts:
        logging.info("concept file " + concept)

    ##########################
    # Create output dir
    ##########################
    logging.info("results_dir = " + results_dir)
    if not os.path.exists(results_dir):
        logging.info('no output dir creating at ' + results_dir)
        if not subprocess.call(['mkdir', '-p', results_dir]) == 0:
            logging.warning('cannot create output dir, aborting')
            sys.exit(1)
    logging.info('output dir is ' + results_dir)

    logging.info('initialisation des concepts')
    begin_time = timeit.default_timer()
    for concept_file in concepts:
        print concept_file
        concept_name = os.path.basename(concept_file).split(".")[0]
        model_output = results_dir + concept_name + '.model'
        logging.info('model for ' + concept_name + ' registered at ' + model_output)
        command = [concept_file, model_output]
        command = train_cmd + command
        logging.info('svm call : ' + " ".join(command))
        ret = subprocess.call(command)
        if ret != 0:
            logging.info('exit code from train_photos for ' + concept_name + ' : ' + str(ret))
    end_time = timeit.default_timer()
    logging.info('end after  ' + str(end_time - begin_time) + 's generated ' + str(len(concepts)) + " concept models")

if __name__ == "__main__":
    main(sys.argv[1:])
