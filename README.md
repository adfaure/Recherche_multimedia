# Projet de Recherhce multimédia

** Le sujet peut être trouvé ici [
http://mrim.imag.fr/GINF53C4/PROJET/](http://mrim.imag.fr/GINF53C4/PROJET/) **

# Scripts
#### main.py
Ce script permet depuis une liste d'image de creer un fichier résultats contenant la liste des histogrammes de chacunes des images (jpg). Les histogrammes sont au format svm.

##### Usage

    ./main.py -u http://mrim.imag.fr/GINF53C4/PROJET/val/urls.txt -o ../results/val_test -d val

permet de lancer le calcul des histogrammes depuis la liste d'url `http://mrim.imag.fr/GINF53C4/PROJET/val/urls.txt` dans le fichier `../results/val_test`

** L'option -d permet de spécifier le fichier de téléchargement, il est important car il permet de ne pas retélécharger les images à chaques fois.**

#### concept.py
###### Usage

    ./concept.py -H ../results/val/val.svm  -u http://mrim.imag.fr/GINF53C4/PROJET/val/ann/ -c http://mrim.imag.fr/GINF53C4/PROJET/concepts.txt  -o ../results/val/svm/

* -H fichier avec les histogrammes
* -u url de base ou trouver les correspondance des concepts
* -c le fichier de concept (url ou path)
* -o repertoire de base ou enregistrer les résultats
