#!/usr/bin/python
import csv
import sys
import getopt


def main(argv):
    ###############################
    # Getting programme options
    ###############################
    help_str = 'no help provided'
    try:
        opts, args = getopt.getopt(argv, "o:c:", ["csv-file="])
    except getopt.GetoptError as err:
        print help_str
        print str(err)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print help_str
            sys.exit()
        elif opt in ("-c", "--csv-file"):
            csv_path = arg

    results = dict()
    with open(csv_path) as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            concept_name = row['concept']
            if concept_name not in results:
                results[concept_name] = row

            if float(results[concept_name]['map']) < float(row['map']):
                results[concept_name] = row

    gvalues = []
    wvalues = []
    for concept_name in results:
        row = results[concept_name]
        wvalues.append(int(row['w']))
        gvalues.append(int(row['g']))
        #print 'concept ' + concept_name + ' g ' + row['g'] + ' w ' + row['w'] + ' ' + row['map']
        #print 'concept ' + concept_name + ' centers ' + row['centers'] + ' g ' + row['g'] + ' w ' + row['w'] + ' ' + row['map']
        #print 'concept ' + concept_name  + ' siftcoef ' + row['siftco'] + ' color ' + row['colorco'] + ' ' + row['map']
    print set(gvalues)
    print set(wvalues)
if __name__ == "__main__":
    main(sys.argv[1:])
