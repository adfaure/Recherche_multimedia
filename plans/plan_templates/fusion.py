#!/usr/bin/python
import os
from datetime import datetime
import sys
import numpy as np
import ConfigParser
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
        opts, args = getopt.getopt(argv, "ho:t:e:", [])
    except getopt.GetoptError as err:
        print help_str
        print str(err)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print help_str
            sys.exit()
        elif opt in ("-t", "--template"):
            plan_tmpl = arg
        elif opt in ("-e", "--entry-file-templates"):
            entry_tmpl = arg
        elif opt in ("-o", "--output-folder"):
            res_folder = arg

    ##########################
    # Create output dir
    ##########################
    if not os.path.exists(res_folder):
        if not subprocess.call(['mkdir', '-p', res_folder]) == 0:
            sys.exit(1)
    if not subprocess.call(['mkdir', '-p', res_folder + "/entry_files/" ]) == 0:
        sys.exit(1)

    with open(entry_tmpl) as entry_file :
        entry_template = Template(entry_file.read())
    with open(plan_tmpl, "r") as outfile:
        template = Template(outfile.read())
    #${base_folder}/fusion_entry_sift-${sift}_color-${color}.txt
    for i in np.arange(0.1, 1, 0.01):
        entry_filename = "fusion_entry_sift-" + str(float(1 - i)) + "_color-" + str(i) + ".txt"
        entry_file = entry_template.substitute(color=i, sift=float(1 - i))
        os.system("echo \"" + entry_file  + "\" > " +  res_folder + "/entry_files/" + entry_filename)

        plan_name = "plan_fusion-" + str(float(1 - i)) + "_color-" + str(i) + ".ini"
        plan_string = template.substitute(base_folder=res_folder, color=i, sift=float(1 - i))
        os.system("echo \"" + plan_string  + "\" > " +  res_folder + "/" + plan_name)



if __name__ == "__main__":
    main(sys.argv[1:])
