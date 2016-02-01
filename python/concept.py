#!/usr/bin/python

import timeit
import os, re
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
script_name = os.path.basename(__file__)
date_str = str(now.day)  + '_' +  str(now.hour) + '_' + str(now.minute) + "_" + str(now.second)
logfile_name = os.path.basename(__file__)  + date_str + '.log'
logging.basicConfig(filename= "log/" + logfile_name,level=logging.DEBUG)

def main(argv):
    """
        Programme qui depuis une liste de concept et de photo attribut
        a une liste d'histogramme au format svm un concept
        Les arguments sont
            -c une url vers une liste de concepts
            -H la liste des histogrammes dans lordre d'aparition dans le fichiers de concepts.
            -o base path et name pour la sortie des fichiers "/file/starting_name_"
            -u url de base pour recuperer les concepts "default : http://mrim.imag.fr/GINF53C4/PROJET/val/ann/
    """
    ###############################
    #Getting programm options
    ###############################
    help_str = 'concept.py -c <concept> -H <histogram> -o <filesbase> -u <urlbase>'
    try:
        opts, args = getopt.getopt(argv,"hu:o:H:c:",["url=","output="])
    except getopt.GetoptError as err:
          print  help_str
          print str(err)
          sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print help_str
            sys.exit()
        elif opt in ("-u", "--url"):
            url_base = arg
        elif opt in ("-c"):
            concept_file = arg
        elif opt in ("-H"):
            histogram_file = arg
        elif opt in ("-o", "--output"):
            res_file = arg

    if not ('histogram_file' in locals()) :
            logging.info('main not correctly called : Histogram file is needed')
            print help_str
            sys.exit()

    #Base concept file
    if not ('url_base' in locals()):
        url_base = "http://mrim.imag.fr/GINF53C4/PROJET/val/ann/"
    logging.info("getting recorded concepts from " + url_base)

    #default results location
    if not ('res_file' in locals()):
        res_file = "../results/res_"
    logging.info("Results will be at  " + res_file + "<conceptname>")

    #Reciperation de la liste de concept
    logging.info('get concept list from ' + concept_file)
    if concept_file.startswith('http://') :
        response = urllib2.urlopen(concept_file).read()
    else :
        response = open(concept_file).read()

    ##################################
    # Chargement de l'Histogramme en memoire
    ##################################
    logging.info('openning histogram model file and read it')
    histogram = open(histogram_file).read()

    ##################################
    #Init variables
    ##################################
    open_files = {}
    concept_streams = {}
    join_seq = ""

    ##################################
    # Initisalizing concepts
    ##################################
    begintime =  timeit.default_timer()
    for concept in response.splitlines():
        logging.info(str(concept))
        concept_record_url = url_base + concept + ".ann"
        logging.info("getting record from " + concept_record_url)
        concept_stream = urllib2.urlopen(concept_record_url).read()
        concept_streams[concept] = concept_stream.splitlines()
        concept_file = res_file + concept
        logging.info("opening results file -> " + concept_file)
        fo = open(concept_file, "wb")
        open_files[concept] = fo

    ###################################
    # Main loop*
    ###################################
    current_line = 0
    for current_line_histogram in histogram.splitlines(): # loop through the histogram model once
        histogram_line = join_seq.join((current_line_histogram.split(' ')[1:])) # get the histogramme (skip the concept)
        for concept in response.splitlines():
            indice = re.split('[ ]*',concept_streams[concept][current_line])[1]
            open_files[concept].write(str(indice) + ' ')
            open_files[concept].write(histogram_line)
            open_files[concept].write('\n')
        current_line = current_line + 1

    for out_file in open_files: #Closing files
        open_files[out_file].close()

    endtime =  timeit.default_timer()
    logging.info('end after  ' + str(endtime -begintime))

if __name__ == "__main__":
   main(sys.argv[1:])
