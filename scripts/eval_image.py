#!/usr/bin/python
import os
import subprocess
from datetime import datetime
import sys
import getopt
import logging
import time
import ConfigParser
from utils import config_section_map


def main(argv):
    ###############################
    # Getting program options
    ###############################
    help_str = 'eval photo'
    try:
        opts, args = getopt.getopt(argv, None, ["config=", "image-path=",
                                                "result="])
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
        elif opt in "--image-path":
            image_path = arg
        elif opt in "--result":
            result = arg

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

    if not os.path.exists(image_path):
        logging.warning("not image found at path " + image_path)

    sift_file = os.path.join('/tmp/', os.path.splitext(image_path)[0] + '.sift')
    color_descriptor_exec = os.path.join(config_general['project_dir'], 'dep', 'colorDescriptor')
    create_sift_cmd = [
        color_descriptor_exec,
        '--descriptor', 'sift',
        image_path, '--output', sift_file
    ]

    logging.info('sift commande : ' + str(create_sift_cmd))
    process = subprocess.Popen(create_sift_cmd)
    while process.poll() is None:
        time.sleep(0)
        pass
    if not os.path.exists(sift_file):
        logging.warning('error while creating sift file')
        exit(1)

if __name__ == "__main__":
    main(sys.argv[1:])
