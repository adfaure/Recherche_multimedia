#!/usr/bin/python
import os
import timeit
from datetime import datetime
import sys
import getopt
import logging
import glob
import subprocess
import ConfigParser
from utils import config_section_map


def main(argv):
    ###############################
    # Getting program options
    ###############################
    nb_thread = 2
    help_str = 'svm-train.py -c <concepts list>'
    try:
        opts, args = getopt.getopt(argv, "tc:ho:", ["input-folder=", "results-dir=",
                                                    "cluster-map=", "config=",
                                                    "nb-clusters=", "nb-thread="])
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
        elif opt in "--input-folder":
            input_sift = arg
        elif opt in "--results-dir":
            results_dir = arg
        elif opt in "--cluster-map":
            centroids_file = arg
        elif opt in "--nb-thread":
            nb_thread = int(arg)
        elif opt in "--nb-clusters":
            nb_clusters = int(arg)

    #########################
    # Chargement de la config
    #########################
    config = ConfigParser.ConfigParser()
    config.read(config_file)
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

    logging.info("Running with " + str(nb_thread) + " threads ")
    #########################
    # Init svm train_photos command
    #########################
    one_nn_script = config_scripts['1nn']

    #########################
    # Get list of sift files
    #########################
    sifts = glob.glob(input_sift + '*.sift')
    logging.info("getting " + str(len(sifts)) + " sift files")

    ##########################
    # Create output dir
    ##########################
    logging.info("results_dir = " + results_dir)
    if not os.path.exists(results_dir):
        logging.info('no output dir creating at ' + results_dir)
        if not subprocess.call(['mkdir', '-p', results_dir]) == 0:
            logging.warning('cannot create output dir, aborting')
            sys.exit(1)
    logging.info('output dir is ' + results_dir)

    logging.info('initialisation des fichiers Sift')
    begin_time = timeit.default_timer()
    cmds = []
    for sift_file in sifts:
        sift_file_name = os.path.basename(sift_file)
        file_name = os.path.splitext(sift_file_name)[0] + ".map"
        results_file = os.path.join(results_dir, file_name)
        command = []
        # R --slave --no-save --no-restore --no-environ --args centers256.txt 256 all_for_R_demo_30 res1nn.txt < 1nn.R
        command += ["R", "--slave", "--no-save", "--no-restore", "--no-environ", "--args"]
        command += [centroids_file, str(nb_clusters), sift_file, results_file]
        cmds.append(command)
    logging.info('---------------PROCESS--------------------')

    process = []
    while len(cmds) != 0 or len(process) != 0:
        if len(process) < nb_thread and len(cmds) != 0:
            file_string = open(one_nn_script, "r")
            cmd = cmds.pop()
            temp_sift_file = os.path.join("/tmp", os.path.splitext(os.path.basename(cmd[8]))[0] + ".temp")
            os.system("sed -n '4,$p' " + cmd[8] + " | tr -d \";\" |sed 's/<CIRCLE [1-9].*> //' > " + temp_sift_file)
            cmd[8] = temp_sift_file
            process.append([cmd, subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=file_string, preexec_fn=os.setsid), temp_sift_file, file_string])
            logging.info("running : " + " ".join(cmd))
        for idx, p in enumerate(process):
            if p[1].poll() is not None:
                stream_data = p[1].communicate()
                rc = p[1].returncode
                if rc != 0:
                    logging.warning(stream_data)
                    logging.warning("command " + " ".join(p[0]))
                logging.info(" end : " + " ".join(p[0]))
                logging.info(" remove temp file : " + p[2])
                os.remove(p[2])
                p[3].close()
                process.pop(idx)

    end_time = timeit.default_timer()
    logging.info('end after  ' + str(end_time - begin_time) + 's generated ' + str(len(sifts)) + " concept models")
    sys.exit(0)

if __name__ == "__main__":
    main(sys.argv[1:])
