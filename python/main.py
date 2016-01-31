#!/usr/bin/python

from datetime import datetime
from ctypes import *
from structures import *
import sys, getopt
import logging
import urllib2

#########################
# Configuration du logger
#########################
now = datetime.now()
date_str = str(now.day)  + '_' +  str(now.hour) + '_' +  str(now.second)
logging.basicConfig(filename='log/log_' + date_str + '.log',level=logging.DEBUG)

######################
# Chargement des lib C
######################
lib = cdll.LoadLibrary("../build/src/libHistogram.so")
libc = CDLL('libc.so.6')

def main(argv):
    ###############################
    #Getting programm options
    ###############################
    help_str = 'main.py -u <url> -o <outputfile>'
    try:
        opts, args = getopt.getopt(argv,"hu:o:",["url=","output="])
    except getopt.GetoptError:
          print 'test.py -i <inputfile> -o <outputfile>'
          sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print help_str
            sys.exit()
        elif opt in ("-u", "--url"):
            url_list = arg
        elif opt in ("-o", "--output"):
            res_file = arg

    if not (('url_list' in locals()) and (('res_file' in locals()))):
            logging.warning('main not correctly called')
            print help_str
            sys.exit()

    logging.info('Getting url from "' + url_list)
    logging.info('Output file is "' + res_file)

#    url_list = 'http://mrim.imag.fr/GINF53C4/PROJET/train/urls.txt'
#    res_file = "../results/train.results"

    logging.info('get url list from ' + url_list)
    response = urllib2.urlopen(url_list).read()

    logging.info('Opening file for results ' + res_file)
    fp = libc.fopen(res_file , "a+")

    ##################################
    #Begin main boucle
    ##################################
    hist = pointer(HISTROGRAM())
    begintime = datetime.now().microsecond
    logging.info('Begin at ' + str(begintime))
    nb_elem = 0
    for line in response.splitlines() :
        lib.read_img(hist,  line)
        lib.print_histogram_libsvm(fp, hist, 0)
        lib.free_histogram(hist)
        nb_elem++

    endtime = datetime.now().microsecond
    logging.info('end after  ' + str(endtime -begintime))
    logging.info(str(nb_elem) + ' have been traited')

if __name__ == "__main__":
   main(sys.argv[1:])
