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
    generate_all_file = False
    help_str = 'svm-train.py -c <concepts list>'
    try:
        opts, args = getopt.getopt(argv, "", ["base-url-rel=", "input-top=",
                                              "config=",
                                              "results-dir="])
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
        elif opt in "--input-top":
            input_top_files = arg
        elif opt in "--base-url-rel":
            rel_base = arg
        elif opt in "--results-dir":
            results_dir = arg

    if generate_all_file:
        logging.info("all option activated")

    #########################
    # Chargement de la config
    #########################
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    config_general = config_section_map(config, 'General')
    section_trec_eval = config_section_map(config, 'trecEval')

    #########################
    # Configuration du logger
    #########################
    log_dir = config_general['log_dir']

    now = datetime.now()
    date_str = str(now.day) + '_' + str(now.hour) + '_' + str(now.minute) + "_" + str(now.second) + "_" + str(now.microsecond)
    logfile_name = os.path.basename(__file__).split('.')[0] + '-' + date_str + '.log'
    logging.basicConfig(filename=log_dir + '/' + logfile_name, level=logging.DEBUG)

    #########################
    # Get list of top formatted files
    #########################
    concepts = glob.glob(os.path.join(input_top_files, '*.top'))
    print input_top_files
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

    begin_time = timeit.default_timer()

    for concept_file in concepts:
        concept_name = os.path.basename(concept_file).split(".")[0]
        res_output = results_dir + concept_name
        rel_path = '/tmp/' + concept_name + '.rel'
        url = rel_base + concept_name + ".rel"
        # curl instead of wget because wget do not override files
        os.system("curl " + rel_base + "/" + concept_name + ".rel " + ">/tmp/" + concept_name + ".rel ")
        if not os.path.exists(rel_path):
            logging.warning("Download error dor file " + url)
            sys.exit(1)
        cmd = [section_trec_eval['trec_eval'], rel_path, concept_file]
        with open(res_output, "w") as outfile:
            ret = subprocess.call(cmd, stdout=outfile)
            if ret != 0:
                logging.warning("error for " + concept_file)

    end_time = timeit.default_timer()
    logging.info('end after  ' + str(end_time - begin_time) + 's generated ' + str(len(concepts)) + " concept models")

if __name__ == "__main__":
    main(sys.argv[1:])
