#!/usr/bin/python
import os
import timeit
import urllib2
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
        opts, args = getopt.getopt(argv, "", ["list-id=", "input-predictions=",
                                              "config=", "all",
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
        elif opt in "--input-predictions":
            input_predictions = arg
        elif opt in "--list-id":
            list_id = arg
        elif opt in "--results-dir":
            results_dir = arg
        elif opt in "--all":
            generate_all_file = True

    if generate_all_file:
        logging.info("all option activated")
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

    #########################
    # Get list of predictions files
    #########################
    concepts = glob.glob(input_predictions + '*.out')
    for concept in concepts:
        logging.info("concept file " + concept)

    #########################
    # Get list of id
    #########################
    logging.info('get concept list from ' + list_id)
    if list_id.startswith('http://'):
        res = urllib2.urlopen(list_id).read()
    else:
        res = open(list_id).read()
    photo_ids = res.splitlines()
    logging.info('found ids of ' + str(len(photo_ids)) + ' photos')

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

    if generate_all_file:
        fall = open(results_dir + 'all.top', "wb")

    logging.info('initialisation des concepts')
    begin_time = timeit.default_timer()
    for concept_file in concepts:
        concept_name = os.path.basename(concept_file).split(".")[0]
        top_output = results_dir + concept_name + '.top'
        fo = open(concept_file)
        file_result = open(top_output, 'wb')
        predictions = fo.read()
        lines = predictions.splitlines()
        indicator = lines[0].split(" ")
        score_row = 2
        if indicator[1] == "1":
            score_row = 1
        idx_begin = 1
        for photo_id in photo_ids:
            id_string = photo_id.split(".")[0]
            line = concept_name + " Q0 " + id_string + " 0 " + lines[idx_begin].split(" ")[score_row] + "\n"
            if generate_all_file :
                fall.write(line)
            file_result.write(line)
            idx_begin += 1
        file_result.close()
    if generate_all_file :
            fall.close()

    end_time = timeit.default_timer()
    logging.info('end after  ' + str(end_time - begin_time) + 's generated ' + str(len(concepts)) + " concept models")

if __name__ == "__main__":
    main(sys.argv[1:])
