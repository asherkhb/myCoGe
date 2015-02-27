__author__ = 'asherkhb'
#Script to Obtain Multiple Datasets
#Current functionality pulls links/IDs from a tab-deliniated file with layout #Comments, experimentid \t datasource
#Returns a dictionary of key:values of experimentids:datasource
#
#by Asher Baltzell
#Last Update 2/21/15
version = '1.0.0'

import os, datetime, urllib2

#Define input file
#**SHOULD GRAB OFF COMMAND LINE**
inputfile = '../sample-experiment-list.txt'

experiments = {}

def buildExperimentDict(inputfile):
    with open(inputfile, 'r') as datalist:
        experiments = {}
        reading = True
        while reading:
            current_line = datalist.readline()
            if current_line == '':
                reading = False
            elif current_line == '\n':
                pass
            elif current_line[0] == '#':
                pass
            else:
                data = current_line.split('\t')
                experiments[data[0]] = data[1]
        return experiments

def buildDataRepo():
    #Create a unique instance variable, by calling datetime to milliseconds
    unique =  datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    #Create a repository folder for imported data based on the unique instance identifier
    repopath = './experiments-%s' % unique
    if not os.path.exists(repopath):
        os.mkdir(repopath)
    return repopath

def getData(experiments, repo):
    #CURRENTLY FUCKED UP. GOOD AT CREATING FILE WITHIN DIRECTORY, BUT FILE ISN'T RIGHT
    for key,value in experiments.iteritems():
        file_path = '%s/%s' % (repo, key)
        f = open(file_path, 'w+')
        file = urllib2.urlopen(value)
        reads = file.read()
        f.write(reads)
        f.close()

experiments = buildExperimentDict(inputfile)
repo = buildDataRepo()
#getData(experiments,repo)