#!/usr/bin/python

import sys
import os
import ConfigParser
import argparse
import subprocess
from scripts.utils import config_section_map

#########################
# Chargement de la config
#########################
config = ConfigParser.ConfigParser()
config.read('install.ini')


def main(argv):
    """
        Entry point for Recherche multimedia.
        This scripts is used to make simple to run other scripts with pre-configured options
    """
    ###############################
    # Getting program options
    ###############################
    parser = argparse.ArgumentParser(description='Main for recherche multimedia.')
    parser.add_argument('-f', action="store", dest='execution_file')
    options = parser.parse_args()

    execution = ConfigParser.ConfigParser()
    execution.read(options.execution_file)

    config_general = config_section_map(config, 'General')
    config_scripts = config_section_map(config, 'Scripts')

    scripts_dir = config_general['scripts_dir']
    exec_file = config_scripts['histogram']
    for execution_plan_section in execution.sections():
        section = config_section_map(execution, execution_plan_section)
        print section['description']
        if section['script'] == 'histogram':
            download_specific_dir = os.path.join(config_general['download_dir'], section['dir_download'])
            result_dir = os.path.join(config_general['results_dir'], section['results'])
            subprocess.call([exec_file,
                             '--config', config_general['config_file'],
                             '-u', section['urls'],
                             '-o', result_dir,
                             '-d', download_specific_dir
                             ], cwd=scripts_dir)

if __name__ == "__main__":
    main(sys.argv[1:])
