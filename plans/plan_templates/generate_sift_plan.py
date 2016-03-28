#!/usr/bin/python
import os
import sys
import getopt
import subprocess
import logging
from string import Template


def main(argv):
    ###############################
    # Getting programme options
    ###############################
    help_str = 'no help provided'
    try:
        opts, args = getopt.getopt(argv, "ho:t:", ["template=", "output-folder="])
    except getopt.GetoptError as err:
        print help_str
        print str(err)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print help_str
            sys.exit()
        elif opt in ("-t", "--template"):
            url_list = arg
        elif opt in ("-o", "--output-folder"):
            res_folder = arg

    ##########################
    # Create output dir
    ##########################
    logging.info("results_dir = " + res_folder)
    if not os.path.exists(res_folder):
        logging.info('no output dir creating at ' + res_folder)
        if not subprocess.call(['mkdir', '-p', res_folder]) == 0:
            logging.warning('cannot create output dir, aborting')
            sys.exit(1)
    logging.info('output dir is ' + res_folder)

    nb_clusters = ['512', '2048', '256']
    g_values    = [400, 25, 100, 150]
    w_values    = [100, 20, 5]

    all = [
        [1024, 150, 20],
        [512, 150, 5],
        [512, 25, 20],
        [2048, 150, 20],
        [512, 400, 20],
        [512, 150, 100],
        [256, 100, 20 ],
        [256, 150, 20]
    ]

    with open(url_list, "r") as outfile:
        template = Template(outfile.read())
        for nb_cluster in nb_clusters:
            for vals in all:
                    name = 'centers-' + str(vals[0]) + '_g-' + str(vals[1]) + '_w-' + str(vals[2])
                    with open(res_folder + "/" + name + ".ini", "w") as plan:
                        config = template.substitute(g=str(vals[1]), w=str(vals[2]), nb_clusters=str(vals[0]), name=name)
                        plan.write(config)

if __name__ == "__main__":
    main(sys.argv[1:])
