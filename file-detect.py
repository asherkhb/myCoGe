__author__ = 'asherkhb'
#Genomic Data Filetype/Filesource Detection Script
#by Asher Baltzell
#
#Last Update: 2/17/15

#import os, linecache
import re

version = '1.0.0'
inputfile = './sample-variant-data/370449-x-chromosome-o37-results.csv'

with open(inputfile, 'r') as inpt:
    #filename = os.path.abspath(inpt)
    first_line = inpt.readline().strip('\n').strip('\r')

    #Perform RE Searches for File Indicators
    twentythree = re.search('23andMe', first_line)                          #23andMe File Key
    familytree = re.search('RSID,CHROMOSOME,POSITION,RESULT', first_line)   #Family Tree DNA File Key

    #Guide based on file-type
    if twentythree:
        print("23andMe File")
    elif familytree:
        print("Family Tree DNA File")
    else:
        print("Unknown File Type")