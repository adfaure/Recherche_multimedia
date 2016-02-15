#!/usr/bin/python
from datetime import datetime
import sys
import timeit
import os
import ConfigParser
import argparse
import subprocess
import logging
from scripts.utils import config_section_map

#########################
# Chargement de la config
#########################
config = ConfigParser.ConfigParser()
config.read('install.ini')


def dispatch(config_scripts, config_general, section):
    if 'skip' in section:
        if 'True' == section['skip']:
            if 'name' in section:
                logging.info('skipping section ' + section['name'] + ' : ' + section['description'])
            else:
                logging.info('skipping section  : ' + section['description'])
            return
    print section['description']
    logging.info(section['description'])
    if section['script'] == 'histogram':
        histogram_plan(config_scripts, config_general, section)
    if section['script'] == 'concept':
        concept_plan(config_scripts, config_general, section)
    if section['script'] == 'svm-train':
        svm_train_plan(config_scripts, config_general, section)
    if section['script'] == 'svm-predict':
        svm_predict_plan(config_scripts, config_general, section)
    if section['script'] == 'transform-trec_eval':
        svm_to_trec_plan(config_scripts, config_general, section)
    if section['script'] == 'trec_eval':
        trec_eval_plan(config_scripts, config_general, section)


def histogram_plan(config_scripts, config_general, section):
    scripts_dir = config_general['scripts_dir']
    exec_file = config_scripts['histogram']
    download_specific_dir = os.path.join(config_general['download_dir'], section['dir_download'])
    working_dir = os.path.join(config_general['working_dir'], section['results'])
    subprocess.call([exec_file,
                     '--config', config_general['config_file'],
                     '-u', section['urls'],
                     '-o', working_dir,
                     '-d', download_specific_dir
                     ], cwd=scripts_dir)


def concept_plan(config_scripts, config_general, section):
    scripts_dir = config_general['scripts_dir']
    working_dir = os.path.join(config_general['working_dir'], section['output_dir'])
    histogram_base = os.path.join(config_general['working_dir'], section['histogram'])
    exec_file = config_scripts['concept']
    concept_file = section['concept_file']
    if not concept_file.startswith('/') and not concept_file.startswith('http://'):
        concept_file = os.path.join(config_general['project_dir'], section['concept_file'])
    subprocess.call([exec_file,
                     '--config', config_general['config_file'],
                     '-H', histogram_base,
                     '-c', concept_file,
                     '-o', working_dir,
                     '-u', section['url_base']
                     ], cwd=scripts_dir)


def svm_train_plan(config_scripts, config_general, section):
    scripts_dir = config_general['scripts_dir']
    working_dir = os.path.join(config_general['working_dir'], section['output_dir'])
    input_dir = os.path.join(config_general['working_dir'], section['input_dir'])
    exec_file = config_scripts['svm-train']
    cmd = [exec_file, '--config', config_general['config_file'],
                      '--input-svm', input_dir,
                      '--svm-args', section['svm-args'],
                      '--results-dir', working_dir ]
    if 'nb-threads' in section:
        cmd += ["--nb-thread", section["nb-threads"]]
    subprocess.call(cmd, cwd=scripts_dir)


def svm_predict_plan(config_scripts, config_general, section):
    scripts_dir = config_general['scripts_dir']
    working_dir = os.path.join(config_general['working_dir'], section['output_dir'])
    input_dir = os.path.join(config_general['working_dir'], section['input_dir'])
    exec_file = config_scripts['svm-predict']
    histogram_file = section['histograms']
    if not histogram_file.startswith("/"):
        histogram_file = os.path.join(config_general['project_dir'], histogram_file)

    predict_command = [exec_file, '--config', config_general['config_file'],
                       '--input-svm', input_dir,
                       '--histograms', histogram_file,
                       '--results-dir', working_dir]
    if 'svm-args' in section:
        predict_command += ['--svm-args', section['svm-args']]
    if 'nb-threads' in section:
        predict_command += ["--nb-thread", section["nb-threads"]]
    subprocess.call(predict_command, cwd=scripts_dir)


def trec_eval_plan(config_scripts, config_general, section):
    scripts_dir = config_general['scripts_dir']
    working_dir = os.path.join(config_general['results_dir'], section['output_dir'])
    input_dir = os.path.join(config_general['working_dir'], section['input_dir'])
    exec_file = config_scripts['trec_eval']
    base_url = section['base-url']
    eval_cmd = [exec_file, '--config', config_general['config_file'],
                           '--input-top', input_dir,
                           '--results-dir', working_dir,
                           '--base-url-rel', base_url]
    subprocess.call(eval_cmd, cwd=scripts_dir)


def svm_to_trec_plan(config_scripts, config_general, section):
    scripts_dir = config_general['scripts_dir']
    working_dir = os.path.join(config_general['working_dir'], section['output_dir'])
    input_dir = os.path.join(config_general['working_dir'], section['input_dir'])
    exec_file = config_scripts['transform-trec_eval']
    list_id = section['list_id']
    if not list_id.startswith("/") and not list_id.startswith("http://"):
        list_id = os.path.join(config_general['project_dir'], list_id)

    predict_command = [exec_file, '--config', config_general['config_file'],
                       '--input-predictions', input_dir,
                       '--list-id', list_id,
                       '--results-dir', working_dir]
    if 'all' in section:
        predict_command += ["--all"]
    subprocess.call(predict_command, cwd=scripts_dir)


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
    parser.add_argument('-j', action="store", dest='job')
    options = parser.parse_args()

    config_general = config_section_map(config, 'General')
    config_scripts = config_section_map(config, 'Scripts')
    #########################
    # Configuration du logger
    #########################
    log_dir = config_general['log_dir']

    now = datetime.now()
    date_str = str(now.day) + '_' + str(now.hour) + '_' + str(now.minute) + "_" + str(now.second) + "_" + str(now.microsecond)
    logfile_name = os.path.basename(__file__).split('.')[0] + '-' + date_str + '.log'
    logging.basicConfig(filename=log_dir + '/' + logfile_name, level=logging.DEBUG)

    ###############################
    # Load execution config
    ###############################
    execution = ConfigParser.ConfigParser()
    execution.read(options.execution_file)
    job = options.job
    if job is not None:
        logging.info("running single job " + job)
        section = config_section_map(execution, job)
        dispatch(config_scripts, config_general, section)
    else:
        ##########################################################
        # Execution of the whole described plan in the config file
        ##########################################################
        logging.info("running full execution ")
        begin_time = timeit.default_timer()
        for execution_plan_section in execution.sections():
            if execution_plan_section == "General":
                continue
            begin_time_section = timeit.default_timer()
            logging.info("running plan : " + execution_plan_section)
            section = config_section_map(execution, execution_plan_section)
            logging.info("running plan : " + section['description'])
            dispatch(config_scripts, config_general, section)
            end_time_section = timeit.default_timer()
            logging.info('section ' + execution_plan_section + ' took ' + str(end_time_section - begin_time_section) + 's')
        end_time = timeit.default_timer()
        logging.info("Total elapsed time " + str(end_time - begin_time) + "s ")

if __name__ == "__main__":
    main(sys.argv[1:])
