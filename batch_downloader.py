__author__ = 'asherkhb'

from datetime import datetime
from json import load


def json_decode(snp_json):
    """Decode SNPScraper JSON Output

    A function to convert JSON objects outputted by SNPScraper into a python dictionary.
    Dictionary can then be used for obtaining data and generating metadata.

    Arguments:
      snp_json: JSON output from SNPScraper

    Returns:
      simpledata = Dictionary of huIDs, download links, and profile links.
        Structure: {'huid': {'download_link': link, 'profile_link': link}, ...}
      alldata = Dictionary of huIDs, download links, profile links, sequencer, and health info
        Structure: {'huID': {'download_link': link, 'profile_link': link, 'health': health, 'sequencer': sequencer},...}
    """

    #Define empty output dictionaries.
    simpledata = {}
    alldata = {}

    #Open the JSON object for processing.
    with open(snp_json, 'r') as data:
        #Load JSON data into variable jdata.
        jdata = load(data)
        #Iterate though each entry
        for i in range(0, len(jdata)):
            #Extract information
            huid = jdata[i]['huid']
            profile_link = jdata[i]['profile_link']
            download_link = jdata[i]['download_link']
            health = jdata[i]['health']
            sequencer = jdata[i]['sequencer']

            #Build dictionaries
            simpledata[huid] = {'download_link': download_link,
                                'profile_link': profile_link}
            alldata[huid] = {'download_link': download_link,
                             'profile_link': profile_link,
                             'health': health,
                             'sequencer': sequencer}

    print "JSON Decoded"
    #Return dictionaries.
    entrynumber = len(simpledata)
    return entrynumber, simpledata, alldata

run_date = datetime.now().strftime("%Y%m%d")
json_file = './temp/snps_%s.json' % run_date
length, simple_data, all_data = json_decode(json_file)



dictionaries = {}
for i in range(1, length/10 + 1):
    dictionaries[i] = {}
print dictionaries

"""
dictionary_count = 1
entry_counter = 0
for huid in simple_data:
    dictionaries[i]
"""
