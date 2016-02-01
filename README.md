# Projet de Recherhce multimédia

** Le sujet peut être trouvé ici [
http://mrim.imag.fr/GINF53C4/PROJET/](http://mrim.imag.fr/GINF53C4/PROJET/) **

# Scripts
#### main.py
Ce script permet depuis une liste d'image de creer un fichier résultats contenant la liste des histogrammes de chacunes des images (jpg). Les histogrammes sont au format svm.

##### Usage

    ./main.py -u http://mrim.imag.fr/GINF53C4/PROJET/val/urls.txt -o ../results/val_test

permet de lancer le calcul des histogrammes depuis la liste d'url `http://mrim.imag.fr/GINF53C4/PROJET/val/urls.txt` dans le fichier `../results/val_test`

#### concept.py
###### Usage

    ./concept.py -H ../results/val -c concepts.txt
