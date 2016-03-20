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

    nb_clusters = ['256', '512']

    g_values = [25, 50, 100, 150]
    w_values = [20, 50]

    with open(url_list, "r") as outfile:
        template = Template(outfile.read())
        for nb_cluster in nb_clusters:
            for g in g_values:
                for w in w_values:
                    name = 'centers-' + nb_cluster + '_g-' + str(g) + '_w-' + str(w)
                    with open(res_folder + "/" + name + ".ini", "w") as plan:
                        config = template.substitute(g=g, w=w, nb_clusters=nb_cluster, name=name)
                        plan.write(config)

if __name__ == "__main__":
    main(sys.argv[1:])
