# 23andMe Tab Separated Data to VCF 4.2 Conversion Script
# by Asher Baltzell
#
#Last Update: 2/15/15

from datetime import datetime
import os

version = "1.0.1"

#Get and Format Date
rundate = datetime.now().strftime("%Y%m%d")

#Pull data from 23andMe TSV, generate dictionary with rsid, chromosome, position, and genotype. Return dictionary as "data"
def pullData(line):
    #Remove '\r' newline character (was causing bug)
    line = line.strip("\r")
    data = {'rsid': '', 'chrom': '', 'pos': '', 'genotype': '', 'ref': '', 'alt': ''}
    data_list = line.split("\t")
    data['rsid'] = data_list[0]
    data['chrom'] = data_list[1]
    data['pos'] = data_list[2]
    data['genotype'] = data_list[3]
    data['ref'] = data_list[3][0]
    if len(data['genotype']) == 2:
        data['alt'] = data_list[3][1]
    elif len(data['genotype']) != 2:
        data['alt'] = '-'
    return data

def outputFileName(inputfile):
    filename, _ = os.path.splitext(inputfile)
    outputfile = "%s.vcf" % filename
    return outputfile

#Specify input file
inputfile = "23sample.txt"

#Generate output file name
outputfile = outputFileName(inputfile)

#Open input file
with open(inputfile, 'r') as inpt:
    #Open Output File
    with open(outputfile, 'w') as vcf:
        #Print Meta-Information
        vcf.write("##fileformat=VCFv4.2\n")
        vcf.write("##fileDate=%s\n" % rundate)
        vcf.write("##source=23me2VCF.pyV%s\n" % version)
        #vcf.write("##reference=%s\n" % inputfile)
        #***ADDITIONAL META-INFO HERE***
        vcf.write("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n")

        #Process Data, Line by Line, until end of document
        reading = True
        while reading:
            #Set line variable to current line
            line = inpt.readline()

            #End Data Processing at End of File
            if line == '':
                reading = False

            #Skip Blank Lines
            elif line == '\n':
                pass

            #Skip Comment Lines
            elif line[0] == '#':
                pass

            #Process Data Lines
            elif line[0] == 'r':
                line = line.strip("\n")
                #Extract data using pullData function
                data = pullData(line)

                #Set new data variables
                #NOTE: All missing fields delinated with a dot ('.')
                chrom = data['chrom']
                pos = data['pos']
                rsid = data['rsid']
                ref = data['ref']
                alt = data['alt']
                qual = '.'
                snpfilter = '.'
                info = '.'

                #Write new data string to output file
                vcf.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (chrom, pos, rsid, ref, alt, qual, snpfilter, info))

            #Skip wierd unpredicted situations
            else:
                pass
