#!/usr/bin/python
import os
import timeit
from datetime import datetime
import sys
import getopt
import logging
import urllib2
import subprocess
import ConfigParser

#########################
# Configuration du logger
#########################
log_dir = "log/"
if not os.path.isdir("log"):
    os.system("mkdir " + log_dir)

script_name = os.path.basename(__file__)
now = datetime.now()
date_str = str(now.day) + '_' + str(now.hour) + '_' + str(now.minute)
logfile_name = os.path.basename(__file__).split('.')[0] + '-' + date_str + '.log'
logging.basicConfig(filename=log_dir + logfile_name, level=logging.DEBUG)

########################################
# Configuration du repertoire de travail
########################################
working_dir = "work/"
if not os.path.isdir("work"):
    os.system("mkdir " + working_dir)

##########################################
# Configuration du repertoire de resultats
##########################################
results_dir = '../results'
if not os.path.isdir(results_dir):
    logging.warning('no results dir, exiting')
    sys.exit(1)

############################
# Initialisation de lib-svm
############################
svm_dir = '../lib/libsvm-3.21'
svm_train = svm_dir + '/svm-train_photos'
svm_predict = svm_dir + '/svm-predict'
if not os.path.isdir(svm_dir):
    logging.warning('no svm dir found')
    sys.exit(1)
else:
    if not os.path.exists(svm_predict) or not os.path.exists(svm_train):
        logging.warning('no executable found')
        sys.exit(1)


def main(argv):
    ###############################
    # Getting program options
    ###############################
    help_str = 'svm.py -c <concepts list>'
    try:
        opts, args = getopt.getopt(argv, "tc:ho:", ["train_photos", "concepts="])
    except getopt.GetoptError as err:
        print help_str
        print str(err)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print help_str
            sys.exit()
        elif opt in ("-c", "--concepts"):
            concept_file = arg
        elif opt in "-t":
            res_file = arg
        elif opt in "-o":
            svm_args = arg

    if 'concept_file' not in locals():
        logging.warning('no concept')
        print help_str
        sys.exit()

    ######################
    # Init concepts list
    ######################
    logging.info('get concept list from ' + concept_file)
    if concept_file.startswith('http://'):
        response = urllib2.urlopen(concept_file).read()
    else:
        response = open(concept_file).read()
    concepts = response.splitlines()

    #########################
    # Init svm train_photos command
    #########################
    train_cmd = ['./' + svm_train]
    if 'svm_options' in locals():
        logging.info('svm options ' + svm_args)
        train_cmd.append(svm_args.split(' '))  # bug with space in subprocess so we have to split it here

    ##########################
    # Create output dir
    ##########################
    output_dir = results_dir + '/train_photos/model/'
    if not os.path.exists(output_dir):
        logging.info('no output dir creating at ' + output_dir)
        if not subprocess.call('mkdir', '-P', output_dir) == 0:
            logging.warning('cannot create output dir, aborting')
            sys.exit(1)
    logging.info('output dir is ' + output_dir)

    hist_file = results_dir + '/train_photos/train_photos.svm'
    if not os.path.exists(hist_file):
        logging.warning('Warning no histograms provided ' + hist_file)
        sys.exit(1)
    logging.info('histograms are in  ' + hist_file)

    concept_svm_dir = os.path.join(results_dir, 'train_photos', 'svm')
    logging.info('concept svm are in ' + concept_svm_dir)

    logging.info('initialisation des concepts')
    begin_time = timeit.default_timer()
    for concept in concepts:
        concept_ann = os.path.join(concept_svm_dir, concept + '.svm')
        if not os.path.exists(concept_ann):
            logging.warning('cannot find ref for concept at ' + concept_ann)
            sys.exit(1)
        else:
            model_output = output_dir + concept + '.model'
            logging.info('model for ' + concept + ' registered at ' + model_output)
            command = [concept_ann, model_output]
            command = train_cmd + command
            ret = subprocess.call(command)
            logging.info('svm call : ' + " ".join(command))
            if ret != 0:
                logging.info('exit code from train_photos for ' + concept + ' : ' + str(ret))
    end_time = timeit.default_timer()
    logging.info('end after  ' + str(end_time - begin_time) + 's')

if __name__ == "__main__":
    main(sys.argv[1:])
