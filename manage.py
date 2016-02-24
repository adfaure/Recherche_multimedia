#!/usr/bin/python
import glob
from datetime import datetime
import sys
import timeit
import os
import ConfigParser
import argparse
import atexit
import subprocess
import logging
from scripts.utils import config_section_map

#########################
# Chargement de la config
#########################
config = ConfigParser.ConfigParser()
config.read('install.ini')
subproc = {}


def safe_quit():
    logging.info("safe quit")
    for p_name in subproc:
        p = subproc[p_name]
        if p.poll() is None:
            logging.info("quit and terminate " + p_name)
            p.terminate()


def running_plan(file, config_scripts, config_general):
    ##########################################################
    # Execution of the whole described plan in the config file
    ##########################################################
    execution = ConfigParser.ConfigParser()
    execution.read(file)
    logging.info("##########################################")
    logging.info("running plan from " + file)
    logging.info("##########################################")
    begin_time = timeit.default_timer()
    for execution_plan_section in execution.sections():
        if execution_plan_section == "General":
            continue
        begin_time_section = timeit.default_timer()
        logging.info("-------------------------------------------")
        logging.info("running section : " + execution_plan_section)
        logging.info("-------------------------------------------")
        section = config_section_map(execution, execution_plan_section)
        logging.info("section : " + section['description'])
        dispatch(config_scripts, config_general, section)
        end_time_section = timeit.default_timer()
        logging.info('section ' + execution_plan_section + ' took ' + str(end_time_section - begin_time_section) + 's')
    end_time = timeit.default_timer()
    logging.info("Total elapsed time " + str(end_time - begin_time) + "s for plan : " + execution_plan_section)


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
    if section['script'] == 'formatSift':
        format_sift_plan(config_scripts, config_general, section)
    if section['script'] == 'kmeans':
        kmeans_plan(config_scripts, config_general, section)
    if section['script'] == 'cluster_mapping':
        center_mapping_plan(config_scripts, config_general, section)


def histogram_plan(config_scripts, config_general, section):
    scripts_dir = config_general['scripts_dir']
    exec_file = config_scripts['histogram']
    download_specific_dir = os.path.join(config_general['download_dir'], section['dir_download'])
    working_dir = os.path.join(config_general['working_dir'], section['results'])
    cmd = [exec_file, '--config', config_general['config_file'],
                      '-u', section['urls'],
                      '-o', working_dir,
                      '-d', download_specific_dir]
    p = subprocess.Popen(cmd, cwd=scripts_dir)
    atexit.register(p.terminate)
    subproc['histogram_plan'] = p
    while not p.poll() is not None:
        pass
    subproc.pop('histogram_plan')


def concept_plan(config_scripts, config_general, section):
    scripts_dir = config_general['scripts_dir']
    working_dir = os.path.join(config_general['working_dir'], section['output_dir'])
    histogram_base = os.path.join(config_general['working_dir'], section['histogram'])
    exec_file = config_scripts['concept']
    concept_file = section['concept_file']
    if not concept_file.startswith('/') and not concept_file.startswith('http://'):
        concept_file = os.path.join(config_general['project_dir'], section['concept_file'])
    cmd = [exec_file, '--config', config_general['config_file'],
                      '-H', histogram_base,
                      '-c', concept_file,
                      '-o', working_dir,
                      '-u', section['url_base']
                     ]
    p = subprocess.Popen(cmd, cwd=scripts_dir)
    subproc['concept_plan'] = p
    while not p.poll() is not None:
        pass
    subproc.pop('concept_plan')


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

    p = subprocess.Popen(cmd, cwd=scripts_dir)
    subproc['svm_train_plan'] = p
    while not p.poll() is not None:
        pass
    subproc.pop('svm_train_plan')


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
    p = subprocess.Popen(predict_command, cwd=scripts_dir)
    subproc['svm_predict_plan'] = p
    while not p.poll() is not None:
        pass
    subproc.pop('svm_predict_plan')


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
    p = subprocess.Popen(eval_cmd, cwd=scripts_dir)
    subproc['trec_eval_plan'] = p
    while not p.poll() is not None:
        pass
    subproc.pop('trec_eval_plan')


def svm_to_trec_plan(config_scripts, config_general, section):
    scripts_dir = config_general['scripts_dir']
    working_dir = os.path.join(config_general['working_dir'], section['output_dir'])
    input_dir = os.path.join(config_general['working_dir'], section['input_dir'])
    exec_file = config_scripts['transform-trec_eval']
    list_id = section['list_id']
    if not list_id.startswith("/") and not list_id.startswith("http://"):
        list_id = os.path.join(config_general['project_dir'], list_id)

    cmd = [exec_file, '--config', config_general['config_file'],
                      '--input-predictions', input_dir,
                      '--list-id', list_id,
                      '--results-dir', working_dir]
    if 'all' in section:
        cmd += ["--all"]
    p = subprocess.Popen(cmd, cwd=scripts_dir)
    subproc['svm_to_trec_plan'] = p
    while not p.poll() is not None:
        pass
    subproc.pop('svm_to_trec_plan')


def format_sift_plan(config_scripts, config_general, section):
    scripts_dir = config_general['scripts_dir']
    working_dir = os.path.join(config_general['working_dir'], section['results'])
    exec_file = config_scripts['format_sift']
    dl_dir = os.path.join(config_general['download_dir'], section['dir_download'])
    urls_file = section['urls']
    cmd = [exec_file, '--config', config_general['config_file'],
                      '--url-list', urls_file,
                      '--download-dir', dl_dir,
                      '--results-dir', working_dir,
                      '--freq-cut', section['freq']]
    p = subprocess.Popen(cmd, cwd=scripts_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subproc['format_sift_plan'] = p
    while not p.poll() is not None:
        pass
    subproc.pop('format_sift_plan')


def kmeans_plan(config_scripts, config_general, section):
    scripts_dir = config_general['scripts_dir']
    working_dir = os.path.join(config_general['working_dir'], section['results'])
    data = section['input']
    if not data.startswith("/"):
        data = os.path.join(config_general['working_dir'], section['input'])
    exec_file = config_scripts['sift_kmeans']
    cmd = [exec_file, '--config', config_general['config_file'],
                      '--results', working_dir,
                      '--samples', data,
                      '--nb-iter', section['nb_iter_max'],
                      '--nb-clusters', section['nb_clusters']]
    p = subprocess.Popen(cmd, cwd=scripts_dir)
    subproc['kmeans_plan'] = p
    while not p.poll() is not None:
        pass
    subproc.pop('kmeans_plan')


def center_mapping_plan(config_scripts, config_general, section):
    scripts_dir = config_general['scripts_dir']
    working_dir = section['results']
    if not working_dir.startswith("/"):
        working_dir = os.path.join(config_general['working_dir'], section['results'])
    sift_files_dir = section['input']
    if not sift_files_dir.startswith("/"):
        sift_files_dir = os.path.join(config_general['download_dir'], section['input'])
    clusters_file = section['clusters_file']
    if not clusters_file.startswith('/'):
        clusters_file = os.path.join(config_general['working_dir'], clusters_file)
    exec_file = config_scripts['mapping_kmeans']
    cmd = [exec_file, '--config', config_general['config_file'],
                      '--input-folder', sift_files_dir,
                      '--results-dir', working_dir,
                      '--cluster-map', clusters_file,
                      '--nb-thread', section['nb_threads'],
                      '--nb-clusters', section['nb_clusters']]
    p = subprocess.Popen(cmd, cwd=scripts_dir)
    subproc['center_mapping_plan'] = p
    while not p.poll() is not None:
        pass
    subproc.pop('center_mapping_plan')


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
    parser.add_argument('-d', action="store", dest='directory')
    parser.add_argument('-i', action="store", dest='init')
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

    atexit.register(safe_quit)

    ###############################
    # Load execution config
    ###############################
    directory = options.directory
    job = options.job
    init_plan = options.init
    if init_plan is not None:
        logging.info("running initialization plan ")
        running_plan(init_plan, config_scripts, config_general)
        logging.info("End initialisation")

    if job is not None:
        execution = ConfigParser.ConfigParser()
        execution.read(options.execution_file)
        logging.info("running single job " + job)
        section = config_section_map(execution, job)
        dispatch(config_scripts, config_general, section)
    elif directory is not None:
        if not directory.startswith("/"):
            directory = os.path.join(config_general['project_dir'], directory)
        if options.execution_file is not None:
            logging.warning("Execution file provided, will be ignored in folder mode")
        logging.info("Executing plan from folder " + directory)
        plans = glob.glob(directory + "/*")
        for plan_file in plans:
            execution = ConfigParser.ConfigParser()
            execution.read(plan_file)
            running_plan(plan_file, config_scripts, config_general)
    else:
        execution = ConfigParser.ConfigParser()
        execution.read(options.execution_file)
        running_plan(options.execution_file, config_scripts, config_general)

if __name__ == "__main__":
    main(sys.argv[1:])
