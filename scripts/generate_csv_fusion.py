#!/usr/bin/python
import csv
import glob
import os
from datetime import datetime
import sys
import ConfigParser
import getopt
import re
import logging
from utils import config_section_map


def main(argv):
    ###############################
    # Getting programme options
    ###############################
    help_str = 'no help provided'
    try:
        opts, args = getopt.getopt(argv, "ho:c:i:", ["config=", "output-file=", "input-folder="])
    except getopt.GetoptError as err:
        print help_str
        print str(err)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print help_str
            sys.exit()
        elif opt in ("-o", "--output-file"):
            res_file = arg
        elif opt in ("-i", "--input-folder"):
            input_folder = arg
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

    fo = open(res_file, "wb")
    #############################
    # Get list of results folders
    #############################
    results = glob.glob(input_folder + '/fusion_*')
    #print results
    fieldnames = ["concept", "siftco", "colorco", "map"]
    writer = csv.DictWriter(fo, fieldnames=fieldnames)
    writer.writeheader()
    for result in results:
        fname = os.path.basename(result)
        values = re.split("_sift-|_color-|", fname)
        files = glob.glob(result +  "/*")
        print files
        for file_res in files:
            concept_name = os.path.basename(file_res)
            with open(file_res, "rb") as trec_res:
                for line in trec_res.read().splitlines():
                    if "map" in line and "gm_map" not in line and concept_name in line:
                        print line
                        token_line = re.split('[ \t]*', line)
                        row = dict()
                        row[fieldnames[0]] = concept_name
                        row[fieldnames[1]] = values[1]
                        row[fieldnames[2]] = values[2]
                        row[fieldnames[3]] = token_line[-1]
                        writer.writerow(row)
    fo.close()

if __name__ == "__main__":
    main(sys.argv[1:])
