__author__ = 'asherkhb'

#Functions required for initiation of myCoGe

# 1. Execute SNPScraper


def scrape_snps(date):
    """Scrape SNPs

    Scrapes 23andMe SNP Variant Data from PGP (http://my.pgp-hms.org)

    Dependencies: Python 2.7 w/ Scrapy installed.
    :param date: date of script execution, in format mm-dd-yy
    """
    from subprocess import call

    initiation = "scrapy runspider snpscraper.py -a NAME=twentythree -o ./temp/snps_%s.json" % date
    call(initiation, shell=True)


# 2. Decode JSON into dictionary


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
    from json import load

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

    #Return dictionaries.
    return simpledata, alldata


# 3. Compare with Directory


def compare_to_directory(simple_data_dict):
    alldata = simple_data_dict
    missingdata = {}
    data_directory = './data/_directory.txt'

    with open(data_directory) as direct:
        current_data = []

        reading = True
        while reading:
            line = direct.readline()
            if line == '':
                reading = False
            elif line == '\n':
                pass
            elif line[0] == '#':
                pass
            else:
                splitline = line.split('\t')
                current_id = splitline[0]
                current_data.append(current_id)

    for huid in alldata:
        if huid in current_data:
            pass
        else:
            missingdata[huid] = alldata[huid]

    return missingdata


# 4. Download Data


def text_vs_zip(link):
    """Text vs Zip

    A function to determine if a file (located at an HTML link) is a text or a zip file.

    Dependencies:
      Requests (http://docs.python-requests.org/en/latest/)

    Arguments:
      link: an HTTP link to a file, either a .txt or some format of a .zip

    Returns:
      File Type
    """
    from re import search
    from requests import head

    file_type = ''
    #Send request for HTTP head document, then extract content-type into variable "content".
    heading = head(link)
    content = heading.headers['content-type']
    #RE search for file-type, assign file type to variable "file_type".
    if search('text', content):
        file_type = "txt"
    if search('zip', content):
        file_type = "zip"
    #Return file type.
    return file_type


def get_data(experiments, repository):
    """Get Data

    A function that downloads .txt or .zip files from HTML that are specified in an input dictionary.
    Compressed files are decompressed, and outputs renamed to ID as specified in input dictionary.
    Specifically, the function is optimized for obtaining 23andMe data from the Personal Genome Project.

    Dependencies:
      wget: must be installed in shell.

    Arguments:
      experiments: Python dictionary of experiments to be downloaded.
        Dictionary Structure: {key:values} of {'huID': ['download-link', <other content>, ...]
      repository: name of file for downloaded experiments to be stored. Typically generated with build_data_repo.

    Returns:
      obtained: list of huID files actually downloaded
    """
    from subprocess import call
    from zipfile import ZipFile
    from os import listdir, mkdir, rename, remove

    #make a folder for the obtained VCFs
    mkdir('./temp/vcfs')

    #Iterate through experiment dictionary.
    for key in experiments:
        #Define download link from dictionary, use textVsZip for file type, then define file path.
        file_link = experiments[key]['download_link']
        file_type = text_vs_zip(file_link)
        file_path = '%s/%s.%s' % (repository, key, file_type)
        #WGET File.
        #command: wget -O <output file location and name> <website>
        wget = "wget -O %s %s" % (file_path, file_link)
        call(wget, shell=True)
        #Unzip Zipped Files
        if file_type == "zip":
            #Create a ZipFile object.
            zip_file = ZipFile(file_path)
            #Create a list of ZipFile contents.
            zip_list = ZipFile.namelist(zip_file)
            #Create variables with old content name and new (huID) content name.
            old_name = "%s/%s" % (repository, zip_list[0])
            new_name = file_path.replace('.zip', '.txt')
            #Unzip ZipFile.
            unzip = "unzip %s -d ./%s " % (file_path, repository)
            call(unzip, shell=True)
            #Rename file contents with huID and then remove zip file.
            rename(old_name, new_name)
            remove(file_path)

    #Check what fiels were actually downloaded
    downloaded_files = listdir('./temp/vcfs')
    downloaded = []
    for item in downloaded_files:
        downloaded.append(item.strip('.txt'))

    return downloaded


# 5. Resolve differences between data that should be downloaded and data that was downloaded


def list_dict_resolve(item_list, dictionary_to_check):
    """List, Dictionary Comparison and Resolve
    from ashertools

    Takes a list, checks that list against the keys in a dictionary.
    Produces two new dictionaries, one with those items present in dictionary represented, one with differences.

    :param item_list: List of known present keys.
    :param dictionary_to_check: Dictionary, containing all potential key:value pairs.

    :return new_dict: Dictionary of key:value pairs of only those keys present in item_list.
    :return differences: Dictionary of the key:value pairs not represented in item_list.
    """
    new_dict = {}
    differences = {}

    for item in dictionary_to_check:
        if item in item_list:
            new_dict[item] = dictionary_to_check[item]
        else:
            differences[item] = dictionary_to_check[item]

    return new_dict, differences


# 6. Update File Directory


def update_directory(missing_data):
    with open('./data/_directory.txt', 'a') as directory:
        for entry in missing_data:
            huid = entry
            profile_link = missing_data[entry]['profile_link']
            download_link = missing_data[entry]['download_link']
            entry = '%s\t%s\t%s\n' % (huid, profile_link, download_link)
            directory.write(entry)


# 7. Generate Metadata


def generate_meta(dataset):
    """Generate Metadata TSV File

    A function to generate a TSV metadata file describing experiments contained in a dictionary.
    Optimized for dictionaries generated with json-decoder.py
    Current Metadata: Filename*, Name*, Description, Source, Source Link, Sequencer, Health Info
    "*" Denotes CoGe Required Fields

    Arguments:
      dataset: Python dictionary with datasets.
        Dictionary Structure: {huID:[link, health], ...}

    Returns:
      None - Generates and writes metadata file "meta.txt".
    """
    with open('meta.txt', 'w') as metadata:
        #Write head row
        metadata.write("Filename\tName\tDescription\tSource\tSource_link\tSequencer\tHealth Records\n")
        #Iterate through data-set, write each data point meta entry.
        for key in dataset.keys():
            meta = generate_item_meta(key, dataset[key][0], dataset[key][1])
            metadata.write(meta)


def generate_item_meta(huid, link, health):
    """Generate Metadata for Individual Experiment

    A function to generate a TSV metadata entry for an individual experiment.
    Optimized for generating entries for generate_meta function
    Current Metadata: Filename*, Name*, Description, Source, Source Link, Sequencer, Health Info
    "*" Denotes CoGe Required Fields

    Arguments:
      huid: huID identifying experiment.
      link: Download link for experiment (orignal source).
      health: Public health records.

    Returns:
      meta - TSV metadata entry for experiment.
    """
    #Assign Variables
    filename = "%s_snps.vcf" % huid
    name = "%s_snps" % huid
    description = "SNP Variant Data for %s, obtained from Personal Genome Project (www.personalgenomes.org)" % huid
    source = "PGP"
    source_link = link
    seq = "23andMe"
    health_info = health
    #Generate metadata entry
    meta = "%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (filename, name, description, source, source_link, seq, health_info)
    return meta


# 8. Convert files to VCF


def pull_data(line):
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


def output_file_name(inputfile):
    from os import path

    filename, _ = path.splitext(inputfile)
    outputfile = "./data/%s.vcf" % filename
    return outputfile, filename


def tsv_to_vcf(input_file, information_dict):
    from datetime import datetime

    #Get and Format Date
    rundate = datetime.now().strftime("%Y%m%d")

    #Specify input file
    inputfile = input_file

    #Generate output file name
    outputfile, filename = output_file_name(inputfile)

    #Open input file
    with open(inputfile, 'r') as inpt:
        #Open Output File
        with open(outputfile, 'w') as vcf:
            #Print Meta-Information
            vcf.write("##fileformat=VCFv4.2\n")
            vcf.write("##fileDate=%s\n" % rundate)
            vcf.write("##source=23me2VCF.pyV%s\n")
            vcf.write("##reference=%s\n" % information_dict[filename]['download_link'])
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
                    data = pull_data(line)

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


# 9. Transfer files to iRODS


def irod_import(dict):
    """

    :param dict: dictionary of newly obtained data.
    """
    from subprocess import call

    call("iinit", shell=True)
    #Feed Password

    call("icd pgp_variant_data", shell=True)

    for huID in dict:
        file = "./data/%s.vcf" % huID
        iput_command = "iput -P %s" % file
        call(iput_command, shell=True)


# 11. Reset temp folder


def reset_temp():
    """Reset temp Folder

    removes ./temp folder and all contents, makes a new ./temp folder.
    """
    from shutil import rmtree
    from os import mkdir

    rmtree('./temp')
    mkdir('./temp')