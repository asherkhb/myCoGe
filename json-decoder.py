__author__ = 'asherkhb'
# SNPScraper JSON Object Decoding Script
# Converts JSON objects produced by SNPscraper into a dictionary {huID, [download link, health info] ... }
#
# by Asher Baltzell
# Last Update: 3/16/15
# Version 1.2.0

import json

practice = './snpscraper/snps_3-1-15.json'


def json_decode(snp_json):
    """Decode SNPScraper JSON Output

    A function to convert JSON objects outputted by SNPScraper into a python dictionary.
    Dictionary can then be used for obtaining data and generating metadata.

    Arguments:
      snp_json: JSON output from SNPScraper

    Returns:
      Dictionary of huIDs, download links, and health info
        Dictionary Structure: {key:values} of {'huID': ['download-link', 'health-info'], ... }
    """
    #Define empty output dictionary.
    data_dict = {}

    #Open the JSON object for processing.
    with open(snp_json, 'r') as data:
        #Load JSON data into variable jdata.
        jdata = json.load(data)
        #Iterate through jdata.
        for i in range(0, len(jdata)):
            #Set entry to current object.
            entry = jdata[i]
            #Assign huID, strip unwanted characters.
            huid = str(entry[u'huid']).strip('[').strip(']').strip('u').strip("'")
            #Assign raw link, strip unwanted characters.
            raw_link = str(entry[u'link']).strip('[').strip(']').strip('u').strip("'")
            #Define link based on raw-link.
            link = "https://my.pgp-hms.org%s" % raw_link
            #If huID and raw-link are present, add entry to dictionary.
            if huid != '' and raw_link != '':
                data_dict[huid] = [link, "Health Filler"]
    #Return dictionary.
    return data_dict


def write_acquired_data(dataset):
    """Write Out Contents from Decoded JSON Dictionary

    A function to write a summary text file of data sets (huIDs and associated links) from a converted JSON
    Prints summary file "acquired_data.txt" to working directory

    Arguments:
      dataset: Dictionary containing data-sets, typically obtained from json_decode.

    Returns:
      None - Generates and writes "acquired_data.txt" summary file.
    """
    with open('acquired_data.txt', 'w') as otpt:
        #Iterate through dataset
        for key in dataset.keys():
            #Write out lines with tab-separated huID and download link.
            writeout = "%s\t%s\n" % (key, dataset[key][0])
            otpt.write(writeout)

write_acquired_data(json_decode(practice))