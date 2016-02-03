#!/usr/bin/python
import os
import timeit
from datetime import datetime
from structures import *
import sys
import ConfigParser
import getopt
import logging
import urllib2
from utils import config_section_map


def main(argv):
    ###############################
    # Getting programme options
    ###############################
    help_str = 'histogram.py -u <url> -o <outputfile>'
    download = False
    try:
        opts, args = getopt.getopt(argv, "hd:u:o:c:", ["config=", "url=", "output="])
    except getopt.GetoptError as err:
        print help_str
        print str(err)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print help_str
            sys.exit()
        elif opt in ("-u", "--url"):
            url_list = arg
        elif opt in ("-o", "--output"):
            res_file = arg
        elif opt in "-d":
            dl_dir = arg
        elif opt in ("-c", "--config"):
            config_file = arg

    if not (('url_list' in locals()) and ('res_file' in locals()) and ('dl_dir' in locals()) and ('config_file' in locals())):
            logging.warning('histogram.py not correctly called')
            print help_str
            sys.exit()

    #########################
    # Chargement de la config
    #########################
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    config_general = config_section_map(config, 'General')
    config_libc = config_section_map(config, 'libC')

    ######################
    # Chargement des libs C
    ######################
    lib = cdll.LoadLibrary(config_libc['libhistogram'])
    libc = CDLL('libc.so.6')

    #########################
    # Configuration du logger
    #########################
    log_dir = config_general['log_dir']

    now = datetime.now()
    script_name = os.path.basename(__file__)
    date_str = str(now.day) + '_' + str(now.hour) + '_' + str(now.minute) + "_" + str(now.second) + "_" + str(now.microsecond)
    logfile_name = os.path.basename(__file__).split('.')[0] + '-' + date_str + '.log'
    logging.basicConfig(filename=log_dir + '/' + logfile_name, level=logging.DEBUG)

    logging.info('Getting url from "' + url_list)
    logging.info('Output file is "' + res_file)

#    url_list = 'http://mrim.imag.fr/GINF53C4/PROJET/train/urls.txt'
#    res_file = "../results/train_photos.results"

    photo_path = dl_dir
    if not (os.path.isdir(photo_path)):
        logging.info("creating folder to dl photos")
        os.system("mkdir -p " + photo_path)
    else:
        logging.info("Photo will be dl to " + photo_path)

    logging.info('get url list from ' + url_list)
    response = urllib2.urlopen(url_list).read()

    logging.info("dl all photos")
    begin_dl = timeit.default_timer()
    nb_photo = 0
    nb_existing = 0
    for line in response.splitlines():
        if not os.path.exists(photo_path + "/" + line.split('/')[-1]):
            # os.system("wget -P " + photo_path + " " + line + " >/dev/null 2>&1")
            nb_photo += 1
        else:
            nb_existing += 1
    elapsed = timeit.default_timer() - begin_dl
    logging.info("dl " + str(nb_photo) + " photos took " + str(elapsed))
    logging.info(str(nb_existing) + " photos already in the folder")

    logging.info('Opening file for results ' + res_file)
    fp = libc.fopen(res_file, "w")

    ##################################
    # Begin main loop
    ##################################
    hist = pointer(HISTROGRAM())
    begin_time = timeit.default_timer()
    logging.info('Begin at ' + str(begin_time))
    nb_elem = 0
    for line in response.splitlines():
        path = photo_path + "/" + line.split('/')[-1]
        lib.read_img(hist,  path)
        lib.print_histogram_libsvm(fp, hist, 0)
        lib.free_histogram(hist)
        nb_elem += 1
        if nb_elem % 500 == 0:
            logging.info(str(nb_elem) + ' in ' + str(timeit.default_timer() - begin_time))

    end_time = timeit.default_timer()
    logging.info('end after  ' + str(end_time - begin_time))
    logging.info(str(nb_elem) + ' have been treated')

if __name__ == "__main__":
    main(sys.argv[1:])
