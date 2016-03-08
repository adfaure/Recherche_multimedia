#!/usr/bin/python
import os
from datetime import datetime
import sys
import ConfigParser
import getopt
import logging
from utils import config_section_map
from string import Template


def main(argv):
    ###############################
    # Getting programme options
    ###############################
    help_str = 'no help provided'
    try:
        opts, args = getopt.getopt(argv, "hr:c:i:", ["config=", "output-file=", "input-folder="])
    except getopt.GetoptError as err:
        print help_str
        print str(err)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print help_str
            sys.exit()
        elif opt in ("-c", "--config"):
            config_file = arg

    #########################
    # Chargement de la config
    #########################
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    config_general = config_section_map(config, 'General')
    config_predict = config_section_map(config, 'Predict')

    #########################
    # Configuration du logger
    #########################
    log_dir = config_general['log_dir']

    now = datetime.now()
    date_str = str(now.day) + '_' + str(now.hour) + '_' + str(now.minute) + "_" + str(now.second) + "_" + str(now.microsecond)
    logfile_name = os.path.basename(__file__).split('.')[0] + '-' + date_str + '.log'
    logging.basicConfig(filename=log_dir + '/' + logfile_name, level=logging.DEBUG)

    model_folders = dict()

    folder_tmpl = Template('centers-${centers}_g-${g}_w-${w}')
    res_file = config_predict['best_results_sift']
    input_folder = config_predict['sift_folders']

    with open(res_file, "r") as best_option:
        content = best_option.read().splitlines()
        for line in content:
            row = line.split(" ")
            concept_name = row[1]
            concept_map = dict()
            nb_centers = row[3]
            g_value = row[5]
            w_value = row[7]
            folder_name = folder_tmpl.substitute(g=g_value, centers=nb_centers, w=w_value)
            if not input_folder.startswith("/"):
                folder_path = os.path.join(config_general['project_dir'], input_folder, folder_name)
            else:
                folder_path = os.path.join(input_folder, folder_name)
            logging.info("folder for " + concept_name + " -> " + folder_path)
            if not os.path.exists(folder_path):
                logging.warning("folder " + folder_name + " required for " + concept_name + " not found")
            else:
                concept_map['sift_folder'] = folder_path
                concept_map['sift_g'] = g_value
                concept_map['sift_w'] = w_value
                concept_map['sift_centers'] = nb_centers
                model_folders[concept_name] = concept_map



if __name__ == "__main__":
    main(sys.argv[1:])
