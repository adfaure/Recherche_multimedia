#!/usr/bin/R
# Lancer ce scripts avec cette commande
#  R --slave --no-save --no-restore --no-environ --args /home/dadou/Documents/Projets/RM/works/sift_train/samples.txt 256 /home/dadou/Documents/Projets/RM/works/sift_train/centers256.txt 100 < /home/dadou/Documents/Projets/RM/scripts/kmeans_clustering.R

# ${1} feature vectors file
# ${2} codebook size
# ${3} directoy where we want to save the results
# ${4} number max of iteration for clustering

#R --slave --no-save --no-restore --no-environ --args /home/dadou/Documents/Projets/RM/works/sift_train/samples.txt 256 /home/dadou/Documents/Projets/RM/works/sift_train/centers256.txt 100 < /home/dadou/Documents/Projets/RM/scripts/kmeans_clustering.R

#[1] "cluster"      "centers"      "totss"        "withinss"     "tot.withinss"
#[6] "betweenss"    "size"         "iter"         "ifault"

cmd_args=commandArgs();
tmptable=read.table(cmd_args[7], sep=" ", colClasses="numeric", comment.char="");
k=kmeans(tmptable,as.integer(cmd_args[8]),as.integer(cmd_args[10]));

tmpname=as.name(cmd_args[9]);

mydata <- tmptable
wss <- (nrow(mydata)-1)

for (i in 1:1000) {
  t = i*5
  wss[i] <- sum(kmeans(tmptable,t,as.integer(cmd_args[10]))$withinss)
  write(i, "/home/dadou/Documents/Projets/RM/kmeans.txt")
}

plot(1:1000, wss, type="b", xlab="Number of Clusters",
     ylab="Within groups sum of squares")
