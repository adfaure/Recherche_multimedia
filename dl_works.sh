#!/bin/bash

echo "" > dl_log

mkdir -p predict_files/sift
mkdir -p predict_files/train

:'
SIFT_FILES=`cat rapport/best_results_sift.txt | awk '{print "dadou@raichu:/home/dadou/Documents/Recherche_multimedia/works/centers-"$4"_g-"$6"_w-"$8}'`

for FOLDER in $SIFT_FILES; do
    if [ ! -d $FOLDER ]; then
        name=`basename $FOLDER`
        mkdir -p predict_files/sift/$name/
        echo "dl de $FOLDER " | tee -a dl_log
        scp -r $FOLDER/sift_train/model predict_files/sift/$name/
    else
        echo "existing $FOLDER" |tee -a dl_log
    fi
done
'

COLOR_FILES=`cat rapport/best_results_color.txt   | awk '{print "dadou@raichu:/home/dadou/Documents/Recherche_multimedia/works/g-"$4"_w-"$6}'`

for FOLDER in $COLOR_FILES; do
    if [ ! -d $FOLDER ]; then
        name=`basename $FOLDER`
        mkdir -p predict_files/color/$name/
        echo "dl de $FOLDER " | tee -a dl_log
        scp -r $FOLDER/train/model predict_files/color/$name/
    else
        echo "existing $FOLDER" |tee -a dl_log
    fi
done
