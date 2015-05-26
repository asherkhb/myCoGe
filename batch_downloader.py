__author__ = 'asherkhb'

from datetime import datetime
from json import load
from re import search
from subprocess import call, check_output, STDOUT
from os import mkdir, path


def cleanup():
    if not al_dwn.closed:
        al_dwn.close()
    if not fail_dwn.closed:
        fail_dwn.close()


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


def scrape_snps(date):
    """Scrape SNPs

    Scrapes 23andMe SNP Variant Data from PGP (http://my.pgp-hms.org)

    Dependencies: Python 2.7 w/ Scrapy installed.
    :param date: date of script execution, in format mm-dd-yy
    """

    initiation = "scrapy runspider snpscraper.py -a NAME=twentythree -o ./temp/snps_%s.json" % date
    call(initiation, shell=True)
    print "SNPScraper Complete"


def json_decode(snp_json):
    """Decode SNPScraper JSON Output

    A function to convert JSON objects outputted by SNPScraper into a python dictionary.
    Dictionary can then be used for obtaining data and generating metadata.

    Arguments:
      snp_json: JSON output from SNPScraper

    Returns:
      simpledata = Dictionary of huIDs, download links, and profile links.
        Structure: {'huid': {'download_link': link, 'profile_link': link}, ...}
    """

    #Define empty output dictionaries.
    simpledata = {}

    #Open the JSON object for processing.
    with open(snp_json, 'r') as scraped:
        #Load JSON data into variable jdata.
        jdata = load(scraped)
        #Iterate though each entry
        for i in range(0, len(jdata)):
            #Extract information
            hu_id = jdata[i]['huid']
            profile_link = jdata[i]['profile_link']
            dlink = jdata[i]['download_link']

            #Build dictionary
            simpledata[hu_id] = {'download_link': dlink,
                                 'profile_link': profile_link}

    print "JSON Decoded"
    #Return dictionaries.
    entrynumber = len(simpledata)
    return entrynumber, simpledata


def text_vs_zip(link):
    file_type = 'NA'
    #Send request for HTTP head document, then extract content-type into variable "content".
    try:
        spider_return = check_output(['wget', '--spider', '--tries=4', '--timeout=30', link], stderr=STDOUT)
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
            return True
        elif file_type == 'zip':
            file_path = './data/zips/%s.%s' % (hid, file_type)
            wget = "wget --tries=4 --timeout=30 -O %s %s" % (file_path, down_link)
            call(wget, shell=True)
            return True
        else:
            return False
    else:
        return False


# Initiate Script
initiate()
run_date = datetime.now().strftime("%Y%m%d")

# Scrape SNPs
scrape_snps(run_date)

# Decode JSON Object
json_file = './temp/snps_%s.json' % run_date
length, data = json_decode(json_file)

# Open Log Files and Establish Dictionaries
already_downloaded = []
al_dwn = open('downloaded.txt', 'r+')
for line in al_dwn:
    entry = line.strip()
    already_downloaded.append(entry)

failed_downloads = []
fail_dwn = open('failures.txt', 'r+')
for line in fail_dwn:
    entry = line.strip()
    failed_downloads.append(entry)

# Download Files
for huid in data:
    if huid not in already_downloaded:
        if huid not in failed_downloads:
            # Print out huid of attempted file
            print huid
            download_link = data[huid]['download_link']
            status = get_data(huid, download_link)
            if status:
                already_downloaded.append(huid)
                al_dwn.write('%s\n' % huid)
            else:
                failed_downloads.append(huid)
                fail_dwn.write('%s\n' % huid)
        else:
            pass
    else:
        pass

# Retry Failed Downloads
retrycount = 1

if len(failed_downloads) > 0:
    failures = True
else:
    failures = False

while failures:
    print "Retrying Failed Downloads, Iteration %s" % str(retrycount)

    # Close failed downloads file, so it can later be modified.
    if not fail_dwn.closed:
        fail_dwn.close()

    retrylist = failed_downloads
    for huid in retrylist:
        # Print out huid of attempted file
        print huid
        download_link = data[huid]['download_link']
        status = get_data(huid, download_link)
        if status:
            # Add to Successful Downloads
            already_downloaded.append(huid)
            al_dwn.write('%s\n' % huid)
            # Remove from Failures
            failed_downloads.remove(huid)
            with open('failures.txt', 'w') as failure_doc:
                for item in failed_downloads:
                    failure_doc.write(item + '\n')
        else:
            pass

    # Check if all failures have been resolved
    if len(failed_downloads) == 0:
        failures = False
        break
    else:
        retrycount += 1

    # Check for continuation every 5 iterations...
    if retrycount > 5:
        get_input = True
        while get_input:
            cont = raw_input("Retry failed downloads 5 more times? (Y/N) ").upper()
            if cont == "Y":
                retrycount = 1
                get_input = False
            elif cont == "N":
                failures = False
                get_input = False
            else:
                print "Invalid Input"
    else:
        pass


# Cleanup
cleanup()