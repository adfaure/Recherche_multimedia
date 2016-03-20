#!/usr/bin/python
import csv
import glob
import os
from datetime import datetime
import sys
import ConfigParser
import getopt
import re
from string import Template
import logging
from utils import config_section_map
from collections import namedtuple


def main(argv):
    """ programme which generate a  new trec formated files
        It take in entry a files which indeicates for each concepts the trec formated files to merge.
        the sum of int float must be 1.
        Line example

        aeroplane;/path/toFile1:float1;/path/toFile2:float2;/path/toFile3:float3
    """
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
        elif opt in ("-o", "--output-folder"):
            res_folder = arg
        elif opt in ("-i", "--input-file"):
            input_file = arg
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
    logging.info("running")

    FileAndPods = namedtuple("FileAndPods", "file name pods")

    if not os.path.exists(input_file):
        logging.warning("input file doesn't exist : " + input_file)
        sys.exit(1)

    if not os.path.exists(res_folder):
        logging.info("creating res folder at : " + res_folder)
        os.system('mkdir -p ' + res_folder)

    template = Template("$concept Q0 $name 0 $map R")
    with open(input_file, 'r') as input_stream :
        lines = input_stream.read().splitlines()
        for line in lines: # EACH CONCEPT
            content = line.split(';')
            concept_name = content[0]
            results_file = os.path.join(res_folder , concept_name + '.top')
            files = []
            size = -1
            nb_trec_file = 0
            for i in range(1, len(content)) : # each file
                pair = content[i].split(':')
                if not os.path.exists(pair[0]):
                    logging.warning("not able to merge files for concept " + str(concept_name) + " no file " + paire[0] )
                    continue
                nb_trec_file += 1
                stream = open(pair[0], 'r')
                tuple = FileAndPods(stream.read().splitlines(),concept_name, pair[1])
                stream.close()
                if (size == -1) :
                    size = len(tuple.file)
                else :
                    if len(tuple.file) != size:
                        logging.warning("files doesn't have same length cannot merge")
                files.append(tuple)

            with open(results_file, 'w') as res_writer:
                for i in range(0,size):
                    photo_name = None
                    new_val = 0
                    for elem in files:
                        line = elem.file[i].split(' ')
                        if photo_name is None:
                            photo_name = line[2]
                        else :
                            if photo_name != line[2] :
                                logging.warning("photoname doesn't match")
                                logging.warning(photo_name + " & " + line[2])
                                sys.exit(1)

                        current_val = float(line[4])
                        new_val += current_val * float(elem.pods)
                    new_line = template.substitute(concept=elem.name ,name=photo_name, map=new_val)

                    res_writer.write(new_line + "\n")
    logging.info('end of programme')

if __name__ == "__main__":
    main(sys.argv[1:])
