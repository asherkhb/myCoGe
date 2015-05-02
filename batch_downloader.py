__author__ = 'asherkhb'

from datetime import datetime
from json import load
from re import search
from subprocess import call, check_output, STDOUT
from os import mkdir, path


def initiate():
    if not path.exists('./data'):
        mkdir('./data')
    if not path.exists('./data/tsvs'):
        mkdir('./data/tsvs')
    if not path.exists('./data/zips'):
        mkdir('./data/zips')
    if not path.exists('./downloaded.txt'):
        dnld = open('./downloaded.txt', 'w')
        dnld.close()
    if not path.exists('./failures.txt'):
        fl = open('./failures.txt', 'w')
        fl.close()


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


def text_vs_zip(link):
    file_type = 'NA'
    #Send request for HTTP head document, then extract content-type into variable "content".
    try:
        spider_return = check_output(['wget', '--spider', link], stderr=STDOUT)
    except:
        spider_return = 'NULL'

    #RE search for file-type, assign file type to variable "file_type".
    if search('.txt', spider_return):
        file_type = 'txt'

    if search('.zip', spider_return):
        file_type = 'zip'

    #Return file type.
    return file_type


def get_data(hid, down_link):
    #Iterate through experiment dictionary.
    #Define download link from dictionary, use textVsZip for file type, then define file path.
    try:
        file_type = text_vs_zip(down_link)
    except:
        file_type = 'NA'

    #WGET File.
    #command: wget -O <output file location and name> <website>
    if file_type != 'NA':
        if file_type == 'txt':
            file_path = './data/tsvs/%s.%s' % (hid, file_type)
            wget = "wget --tries=4 --timeout=30 -O %s %s" % (file_path, down_link)
            call(wget, shell=True)
            return 'success'
        elif file_type == 'zip':
            file_path = './data/zips/%s.%s' % (hid, file_type)
            wget = "wget --tries=4 --timeout=30 -O %s %s" % (file_path, down_link)
            call(wget, shell=True)
            return 'success'
        else:
            return 'fail'
    else:
        return 'fail'


initiate()
run_date = datetime.now().strftime("%Y%m%d")
json_file = './temp/snps_%s.json' % run_date
length, simple_data, all_data = json_decode(json_file)

already_downloaded = []
with open('downloaded.txt', 'r') as al_dwn:
    for line in al_dwn:
        entry = line.strip('\n')
        already_downloaded.append(entry)

failed_downloads = []
with open('failures.txt', 'r') as fail_dwn:
    for line in fail_dwn:
        entry = line.strip('\n')
        failed_downloads.append(entry)

with open('downloaded.txt', 'a+') as download_success, open('failures.txt', 'a+') as download_fail:
    for huid in simple_data:
        if huid not in already_downloaded:
            if huid not in failed_downloads:
                download_link = simple_data[huid]['download_link']
                status = get_data(huid, download_link)
                if status == 'success':
                    download_success.write('%s\n' % huid)
                elif status == 'fail':
                    download_fail.write('%s\n' % huid)
                else:
                    pass
            else:
                pass
        else:
            pass