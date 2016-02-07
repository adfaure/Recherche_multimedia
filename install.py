#!/usr/bin/python
import sys
import os
import subprocess
import ConfigParser
import shutil
from scripts.utils import config_section_map


def main(argv):
    # Creating config instance
    config = ConfigParser.ConfigParser()
    # Creating config file
    if not os.path.exists('project.ini'):
        subprocess.call(['touch', 'project.ini'])

    # Read the base config
    config.read('project.ini')
    # Open file config for write
    config_file = open('install.ini', 'w')
    # Add project base directory
    current_directory = os.path.dirname(os.path.realpath(__file__))

    config.set('General', 'config_file', current_directory + '/install.ini')
    config.set('General', 'project_dir', current_directory)
    ######################################
    # Crating config section
    ######################################

    config.add_section('libC')
    config.add_section('libSvm')
    config.add_section('Scripts')
    config_general = config_section_map(config, 'General')
    #######################################
    # Create python related directory
    #######################################
    # Creating log directory
    log_directory = current_directory + '/log'
    if not os.path.exists(log_directory):
        res = subprocess.call(['mkdir', '-p', log_directory])
        if res != 0:
            print 'cannot create ' + log_directory
            sys.exit(1)
    config.set('General', 'log_dir', log_directory)

    # Creating download directory (to store photos)
    download_dir = current_directory + '/download'
    if not os.path.exists(download_dir):
        res = subprocess.call(['mkdir', '-p', download_dir])
        if res != 0:
            print 'cannot create ' + download_dir
            sys.exit(1)
    config.set('General', 'download_dir', download_dir)

    scripts_dir = current_directory + '/scripts'
    if not os.path.exists(scripts_dir):
        res = subprocess.call(['mkdir', '-p', scripts_dir])
        if res != 0:
            print 'cannot create ' + scripts_dir
            sys.exit(1)
    config.set('General', 'scripts_dir', scripts_dir)
    config.set('Scripts', 'histogram', scripts_dir + '/histogram.py')
    config.set('Scripts', 'concept', scripts_dir + '/concept.py')
    config.set('Scripts', 'svm-train', scripts_dir + '/svm-train.py')
    #######################################
    # Installing C module
    #######################################
    build_dir = current_directory + '/build'
    if os.path.exists(build_dir):
        print 'purging build dir'
        shutil.rmtree(build_dir)

    res = subprocess.call(['mkdir', '-p', build_dir])
    if res != 0:
        print 'cannot create ' + download_dir
        sys.exit(1)

    # Building C Library
    res = subprocess.call(['cmake', '..'], cwd=build_dir)
    if res != 0:
        print 'problem for Cmake '
        sys.exit(1)

    res = subprocess.call('make', cwd=build_dir)
    if res != 0:
        print 'Problem src not compiling'
        sys.exit(1)

    lib_histogram = build_dir + '/src/libHistogram.so'
    if os.path.exists(build_dir + '/src/libHistogram.so'):
        print 'libHistogram found at ' + lib_histogram
        config.set('libC', 'libHistogram', lib_histogram)

    #######################################
    # Installing SVM
    #######################################
    current_version = config_general['libsvm_version']
    svm_install_dir = current_directory + '/lib/libsvm-'+current_version
    if os.path.exists(svm_install_dir):
        subprocess.call(['rm', 'r', svm_install_dir], cwd='lib')

    tar_file = 'lib/libsvm-' + current_version + '.tar.gz'
    if not os.path.exists(tar_file):
        print "no svm provided "
        sys.exit(1)

    subprocess.call(['tar', '-zxvf' 'libsvm-' + current_version + '.tar.gz'], cwd='lib')
    config.set('libSvm', 'install_dir', svm_install_dir)
    if os.path.exists(svm_install_dir):
        subprocess.call(["make", "clean"], cwd=svm_install_dir)
        subprocess.call(["make"], cwd=svm_install_dir)
        svm_train = svm_install_dir + '/svm-train'
        svm_predict = svm_install_dir + '/svm-predict'
        if os.path.exists(svm_train) and os.path.exists(svm_predict):
            config.set('libSvm', 'svm_train', svm_train)
            config.set('libSvm', 'svm_predict', svm_predict)
        else:
            print 'problem svm exec not found'
            sys.exit(1)
    else:
        print 'Please check svm install, should be at ' + svm_install_dir
        sys.exit(1)

    #######################################
    # Result folder
    #######################################
    results_dir = current_directory + '/results'
    if not os.path.exists(results_dir):
        res = subprocess.call(['mkdir', '-p', results_dir])
        if res != 0:
            print 'cannot create ' + results_dir
            sys.exit(1)
    config.set('General', 'results_dir', results_dir)

    config.write(config_file)
    config_file.close()

if __name__ == "__main__":
    main(sys.argv[1:])
