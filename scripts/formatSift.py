#!/usr/bin/python
import os
import subprocess
import timeit
import urllib2
from datetime import datetime
import sys
import getopt
import logging
import ConfigParser
from utils import config_section_map


def main(argv):
    ###############################
    # Getting program options
    ###############################
    nb_thread = 2
    help_str = 'formatSift.py'
    try:
        opts, args = getopt.getopt(argv, None, ["config=", "url-list=",
                                                "results-dir=", "download-dir=",
                                                "freq-cut="])
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
        elif opt in "--url-list":
            url_list = arg
        elif opt in "--results-dir":
            results_dir = arg
        elif opt in "--download-dir":
            download_dir = arg
        elif opt in "--freq-cut":
            cut_every = int(arg)

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

    if 'cut_every' not in locals():
        logging.warning("no defined step")
        exit(1)

    ##################################################
    # Recuperation de la liste des fichiers SIFT
    ##################################################
    if 'url_list' not in locals():
        logging.warning("no sift files provided ")
        exit(1)

    if url_list.startswith("http://") or url_list.startswith("https://"):
        raw_file = urllib2.urlopen(url_list).read()
    else:
        raw_file = open(url_list).read()
    urls = raw_file.splitlines()
    logging.info("nombre d'url : " + str(len(urls)))

    ##################################################
    # Creation du dossier de sauvegarde
    ##################################################
    logging.info("download dir = " + download_dir)
    if not os.path.exists(results_dir):
        logging.info('no output dir creating at ' + results_dir)
        if not subprocess.call(['mkdir', '-p', download_dir]) == 0:
            logging.warning('cannot create download dir, aborting')
            sys.exit(1)
    logging.info('download dir is ' + results_dir)

    ########################################
    # Creation du dossier pour les resultats
    ########################################
    logging.info("results_dir = " + results_dir)
    result_name = os.path.basename(results_dir)
    results_dir = os.path.dirname(results_dir)
    if not os.path.exists(results_dir):
        logging.info('no output dir creating at ' + results_dir)
        if not subprocess.call(['mkdir', '-p', results_dir]) == 0:
            logging.warning('cannot create output dir, aborting')
            sys.exit(1)
    logging.info('output dir is ' + results_dir)

    logging.info("download sift files")
    begin_dl = timeit.default_timer()
    nb_existing = 0
    for url in urls:
        if url.endswith('.sift'):
            name = url.split('/')[-1]
            sift_path = os.path.join(download_dir, name)
            if not os.path.exists(sift_path):
                os.system("wget -P " + download_dir + " " + url + " >/dev/null 2>&1")
            else:
                nb_existing = 0
    elapsed = timeit.default_timer() - begin_dl
    logging.info("dl " + str(len(urls)) + " sift file took " + str(elapsed))
    logging.info(str(nb_existing) + " sift already in the folder")

    res_file = open(os.path.join(results_dir, result_name), "w")

    for url in urls:
        if url.endswith('.sift'):
            name = url.split('/')[-1]
            with open(os.path.join(download_dir, name)) as sift:
                content = sift.read().splitlines()
                step = 4  # on passe les trois premieres lignes
                while step < len(content):
                    line = content[step].split(";")[-2]
                    line = line.lstrip()
                    line = line.rstrip()
                    res_file.write(line)
                    res_file.write("\n")
                    step += cut_every

    res_file.close()

if __name__ == "__main__":
    main(sys.argv[1:])
