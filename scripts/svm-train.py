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


def main(argv):
    ###############################
    # Getting program options
    ###############################
    nb_thread = 2
    help_str = 'svm-train.py -c <concepts list>'
    try:
        opts, args = getopt.getopt(argv, "tc:ho:", ["concepts=", "results-dir=",
                                                    "input-svm=", "config=",
                                                    "svm-args=", "nb-thread="])
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
        elif opt in "--nb-thread":
            nb_thread = int(arg)

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

    logging.info("Running with " + str(nb_thread) + " threads ")
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
    cmds = []
    for concept_file in concepts:
        command = []
        concept_name = os.path.basename(concept_file).split(".")[0]
        model_output = results_dir + concept_name + '.model'
        logging.info('model for ' + concept_name + ' registered at ' + model_output)
        command = [concept_file, model_output]
        command = train_cmd + command
        logging.info('svm call : ' + " ".join(command))
        cmds.append(command)

    logging.info('---------------PROCESS--------------------')

    process = []
    while len(cmds) != 0 or len(process) != 0:
        if len(process) < nb_thread and len(cmds) != 0:
            cmd = cmds.pop()
            process.append([cmd, subprocess.Popen(cmd)])
            logging.info("running : " + " ".join(cmd))
        for idx, p in enumerate(process):
            if p[1].poll() is not None:
                logging.info(" end : " + " ".join(p[0]))
                process.pop(idx)

    end_time = timeit.default_timer()
    logging.info('end after  ' + str(end_time - begin_time) + 's generated ' + str(len(concepts)) + " concept models")

if __name__ == "__main__":
    main(sys.argv[1:])
