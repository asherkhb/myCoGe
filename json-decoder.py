# SNPScraper JSON Object Decoding Script
# Converts JSON objects produced by snpscraper web-crawler into a dictionary of huIDs (keys) download links(values)
#
#by Asher Baltzell

import json
import metagenerator

data_dict = {}

with open('./snpscraper/snps_3-1-15.json', 'r') as data:
    jdata = json.load(data)

    for i in range(0,len(jdata)):
        entry = jdata[i]
        huid = str(entry[u'huid']).strip('[').strip(']').strip('u').strip("'")
        raw_link = str(entry[u'link']).strip('[').strip(']').strip('u').strip("'")
        link = "https://my.pgp-hms.org%s" % raw_link
        if huid != '':
            if raw_link != '':
                data_dict[huid] = [link, "Health Filler"]

    #ACCESS ALL HUIDS & LINKS
    #for key in data_dict.keys():
    #    print key, data_dict[key]

#Use Metagenerator to Generate Metadata File for datapoints in data_dict
metagenerator.generateMeta(data_dict)