#!/usr/bin/python
import os
from datetime import datetime
import sys
import getopt
import logging
import glob
import subprocess
import ConfigParser
from utils import config_section_map


def create_histogram(filename, nb_cluster):
    with open(filename, 'r') as f:
        try:
            content = f.read()
            mapping = content.splitlines()
            nb_sift = len(mapping)
            buckets = [0.0] * int(nb_cluster)
            for cluster in mapping:
                buckets[int(cluster) - 1] += 1.0
            for i, val in enumerate(buckets):
                buckets[i] = val / nb_sift
            return buckets
        except Exception as e:
            logging.warning("cannot open file " + filename)
            logging.warning(e)
    return None


def main(argv):
    ###############################
    # Getting program options
    ###############################
    generate_all_file = False
    help_str = ''
    try:
        opts, args = getopt.getopt(argv, "", ["output=", "input-dir=",
                                              "config=", "nb-cluster="])
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
        elif opt in "--input-dir":
            input_dir = arg
        elif opt in "--output":
            output = arg
        elif opt in "--nb-cluster":
            nb_cluster = float(arg)

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
    # Get mapping files
    #########################
    logging.info("looking for mapping in folder : " + input_dir)
    mappings = glob.glob(input_dir + '/*.map')
    logging.info("found " + str(len(mappings)) + " mapping files")

    logging.info("nb clusters : " + str(nb_cluster))
    ########################################
    # Creation du fichier et dossier pour les resultats
    ########################################
    logging.info("results file  = " + output)
    result_name = os.path.basename(output)
    results_dir = os.path.dirname(output)
    if not os.path.exists(results_dir):
        logging.info('no output dir creating at ' + results_dir)
        if not subprocess.call(['mkdir', '-p', results_dir]) == 0:
            logging.warning('cannot create output dir, aborting')
            sys.exit(1)
    logging.info('output dir is ' + results_dir)
    output_temp = output + ".temp"
    with open(output_temp, 'w') as res_file:
        for m in mappings:
            hist = create_histogram(m, nb_cluster)
            res_file.write(os.path.basename(os.path.splitext(m)[0]))
            res_file.write(" ")
            for i, val in enumerate(hist):
                if val != 0.0:
                    res_file.write(str(i+1) + ":")
                    res_file.write(str(val) + " ")
            res_file.write("\n")

    #####################
    # Ordering the file
    ####################
    os.system("sort " + output_temp + " > " + output)
    sed_command = "sed -i.back -e 's/^[0-9]*_[0-9]* /0 /g' " + output
    os.system(sed_command)
    logging.info(sed_command)
    os.remove(output_temp)

if __name__ == "__main__":
    main(sys.argv[1:])
