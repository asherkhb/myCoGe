__author__ = 'asherkhb'

import cPickle as pickle
import smtplib

from datetime import datetime
from email import Encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from json import load
from os import listdir, mkdir, path, remove, rename
from re import search
from shutil import rmtree, move
from subprocess import call, check_output, STDOUT
from zipfile import ZipFile


# Open reference files
indexfile = '00-All.vcf.p'
referencefile = '00-All.vcf'
mergeindexfile = 'RsMergeArch.bcp.p'
mergefile = 'RsMergeArch.bcp'

snp_index = pickle.load(open(indexfile, 'rb'))
merge_index = pickle.load(open(mergeindexfile, 'rb'))

reference = open(referencefile, 'r')
merged = open(mergefile, 'r')

print "Reference Documents Successfully Imported"


def cleanup():
    reference.close()
    merged.close()
    #rmtree('./temp')
    #mkdir('./temp')
    #mkdir('./temp/pickles')

    print "Cleanup Operations Complete"

#Functions required for initiation of myCoGe

# 1. Execute SNPScraper


def scrape_snps(date):
    """Scrape SNPs

    Scrapes 23andMe SNP Variant Data from PGP (http://my.pgp-hms.org)

    Dependencies: Python 2.7 w/ Scrapy installed.
    :param date: date of script execution, in format mm-dd-yy
    """

    initiation = "scrapy runspider snpscraper.py -a NAME=twentythree -o ./temp/snps_%s.json" % date
    call(initiation, shell=True)
    print "SNPScraper Complete"

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

    print "Missing Data Identified"
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
    file_type = ''
    #Send request for HTTP head document, then extract content-type into variable "content".
    spider_return = check_output(['wget', '--spider', link], stderr=STDOUT)

    #RE search for file-type, assign file type to variable "file_type".
    if search('.txt', spider_return):
        file_type = 'txt'

    if search('.zip', spider_return):
        file_type = 'zip'

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

    #make a folder for the obtained TSVs

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

    #Check what files were actually downloaded
    downloaded_files = listdir(repository)
    downloaded = []
    for item in downloaded_files:
        downloaded.append(item.strip('.txt'))

    print "Missing Data Downloaded"
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
    print "Directory Updated"

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
# Uses SnpExperiment Class

# 9. Transfer files to iRODS


def irod_import(newly_obtained_data):
    """

    :param newly_obtained_data: dictionary of newly obtained data.
    """

    call("iinit", shell=True)
    #Feed Password

    call("icd pgp_variant_data", shell=True)

    for huID in newly_obtained_data:
        file_id = "./data/%s.vcf" % huID
        iput_command = "iput -P %s" % file_id
        call(iput_command, shell=True)


# 11. Generate Logs, Email Log File


def generate_log_pickles(dictionary_of_datasets):
    #Dataset dictionaries should be dataset_name:dataset key:values
    pickles = []
    for key in dictionary_of_datasets:
        dataset_pickle_name = './temp/pickles/' + key + '.p'
        dataset_contents = dictionary_of_datasets[key]
        pickle.dump(dataset_contents, open(dataset_pickle_name, "wb"))
        pickles.append(dataset_pickle_name)

    call('tar -zcf ./temp/pickles.tar.gz ./temp/pickles', shell=True)
    return pickles


def send_email_log(new_files_added_list, attachments):
    account = "mycoge@gmail.com"
    password = "9P4cx3OoW3"

    date = datetime.now().strftime("%m-%d-%Y")
    number = str(len(new_files_added_list))

    FROM = account
    TO = ['ahaug@email.arizona.edu']
    SUBJECT = "myCoGe Log - %s" % date
    TEXT = "myCoGe was successfully executed, with %s new experiments added today.\n" \
           "The following files were added:\n%s" \
           "\n\n The following log files are attached:\n" \
           " - snps_DATE.json : JSON object generated by webscraping PGP for SNP datasets.\n" \
           " - _directory.txt : Current directory of all added experiments.\n" \
           " - pickles.tar.gz : Binary representations of critical script datasets. \n" \
           " - terminal_output.txt : Text file of all terminal output from script. \n" \
           % (number, '\n'.join(new_files_added_list))

    msg = MIMEMultipart()
    msg['Subject'] = SUBJECT
    msg['From'] = FROM
    msg['To'] = ', '.join(TO)

    msg.attach(MIMEText(TEXT))

    for item in attachments:
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(item, 'rb').read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % path.basename(item))
        msg.attach(part)

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(account, password)
        server.sendmail(FROM, TO, msg.as_string())
        server.close()
        print "Message Sent"
    except:
        print "Email Failure - Log written to file"


# Classes
# Currently Includes...
#    - SnpExperiment - Class for SNP experiments of all types. Checks file type and converts to VCF.


class SnpExperiment(object):
    def __init__(self, huid, file_path, vcf_path):
        self.id = huid
        self.file_path = file_path
        self.file_source = self.get_file_source
        self.vcf_reference_genome = 'GrCh38 (Annotation Release 106)'
        self.vcf_path = vcf_path

    @property
    def get_file_source(self):
        with open(self.file_path, 'r') as inpt:
            file_source = 'Unknown'
            identifyer = inpt.readline()
            identifyer_compressed = identifyer.strip('\n').strip('\r').strip(' ')
            identifyer_contents = identifyer_compressed.split('\t')

            if search('23andMe', identifyer):
                file_source = '23andMe'

            elif search('AncestryDNA', identifyer):
                file_source = 'AncestryDNA'

            elif identifyer_contents[0] == 'rsid':
                if len(identifyer_contents) == 4:
                    file_source = 'Genetic_4col'
                elif len(identifyer_contents) == 5:
                    file_source = 'Generic_5col'

            else:
                file_source = 'Unknown'

        return file_source

    def convert_to_vcf(self):
        filetype = self.file_source

        if filetype == '23andMe':
            self.fourcol_to_vcf()

        elif filetype == 'AncestryDNA':
            self.fivecol_to_vcf()

        elif filetype == 'Generic_4col':
            self.fourcol_to_vcf()

        elif filetype == 'Generic_5col':
            self.fivecol_to_vcf()

        else:
            move(self.file_path, './unknown_fileformats/%s' % path.basename(self.file_path))
            print "%s Filetype Unknown.\n -->TSV moved to ./unknown_fileformats/ for review" % self.file_path

    @staticmethod
    def fourcol_pull_data(line_to_pull):
        data = {'rsid': '', 'chrom': '', 'pos': '', 'genotype': '', 'ref': ''}

        pulling_line = line_to_pull.strip('\n').strip('\r')
        data_list = pulling_line.split('\t')
        rsid = data_list[0]
        legacy_id = rsid

        #Redo id's that don't start with rs
        if rsid[0] == 'i':
            rsid = rsid.replace('i', 'rs')

        data['rsid'] = rsid
        data['chrom'] = data_list[1]
        data['genotype'] = data_list[3]

        try:
            ref_loc = snp_index[rsid]
            reference.seek(ref_loc)
            referenceline = reference.readline()
            referenceline_split = referenceline.split('\t')
            data['pos'] = referenceline_split[1]    # This position updates to the new ref., GrCh38 (An. Release 106)
            data['ref'] = referenceline_split[3]
        except KeyError:
            #If key isn't found, search RsMerge table for new rsID, update rsID to account for this
            try:
                rsid_base = rsid.replace('rs', '')
                merge_loc = merge_index[rsid_base]
                merged.seek(merge_loc)
                mergeline = merged.readline()
                mergeline_split = mergeline.split('\t')
                new_id_base = str(mergeline_split[1])
                new_id = 'rs' + new_id_base
                data['rsid'] = new_id
                ref_loc = snp_index[new_id]
                reference.seek(ref_loc)
                referenceline = reference.readline()
                referenceline_split = referenceline.split('\t')
                data['pos'] = referenceline_split[1]    # Position updates to GrCh38 (An. Release 106)
                data['ref'] = referenceline_split[3]
            except KeyError:
                data['rsid'] = legacy_id
                data['pos'] = '0'
                data['ref'] = '?'

        return data

    @staticmethod
    def fivecol_pull_data(line_to_pull):
        data = {'rsid': '', 'chrom': '', 'pos': '', 'genotype': '', 'ref': ''}

        pulling_line = line_to_pull.strip('\n').strip('\r')
        data_list = pulling_line.split('\t')
        rsid = data_list[0]
        legacy_id = rsid

        #Redo id's that don't start with rs
        if rsid[0] == 'i':
            rsid = rsid.replace('i', 'rs')

        data['rsid'] = rsid
        data['chrom'] = data_list[1]
        data['genotype'] = data_list[3] + data_list[4]

        try:
            ref_loc = snp_index[rsid]
            reference.seek(ref_loc)
            referenceline = reference.readline()
            referenceline_split = referenceline.split('\t')
            data['pos'] = referenceline_split[1]    # This position updates to the new ref., GrCh38 (An. Release 106)
            data['ref'] = referenceline_split[3]
        except KeyError:
            #If key isn't found, search RsMerge table for new rsID, update rsID to account for this
            try:
                rsid_base = rsid.replace('rs', '')
                merge_loc = merge_index[rsid_base]
                merged.seek(merge_loc)
                mergeline = merged.readline()
                mergeline_split = mergeline.split('\t')
                new_id_base = str(mergeline_split[1])
                new_id = 'rs' + new_id_base
                data['rsid'] = new_id
                ref_loc = snp_index[new_id]
                reference.seek(ref_loc)
                referenceline = reference.readline()
                referenceline_split = referenceline.split('\t')
                data['pos'] = referenceline_split[1]    # Position updates to GrCh38 (An. Release 106)
                data['ref'] = referenceline_split[3]
            except KeyError:
                data['rsid'] = legacy_id
                data['pos'] = '0'
                data['ref'] = '?'

        return data

    def fourcol_to_vcf(self):
        with open(self.file_path, 'r') as inpt, open(self.vcf_path, 'w') as otpt:
            #Get and Format Date
            rundate = datetime.now().strftime("%Y%m%d")

            otpt.write('##fileformat=VCFv4.2\n')
            otpt.write('##fileDate=%s\n' % rundate)
            otpt.write('##source=myCoGe-twentythree_to_vcf.py\n')
            otpt.write('##reference = \n')

            otpt.write('#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n')

            for line in inpt:
                if line[0] == '#':
                    pass
                elif line[0] == '\n':
                    pass
                else:
                    line_thin = line.strip(' ')
                    line_split = line_thin.split('\t')
                    if line_split[0] != 'rsid':
                        datas = self.fourcol_pull_data(line)
                        chrom = datas['chrom']
                        pos = datas['pos']
                        rid = datas['rsid']
                        ref = datas['ref']
                        alt = datas['genotype']
                        qual = '.'
                        fill = '.'
                        info = '.\n'
                        entry = [chrom, pos, rid, ref, alt, qual, fill, info]
                        new_entry = '\t'.join(entry)
                        otpt.write(new_entry)

        print "%s Converted to VCF" % self.file_path

    def fivecol_to_vcf(self):
        with open(self.file_path, 'r') as inpt, open(self.vcf_path, 'w') as otpt:
            #Get and Format Date
            rundate = datetime.now().strftime("%Y%m%d")

            otpt.write('##fileformat=VCFv4.2\n')
            otpt.write('##fileDate=%s\n' % rundate)
            otpt.write('##source=myCoGe.py\n')
            otpt.write('##reference=\n')

            otpt.write('#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n')

            for line in inpt:
                if line[0] == '#':
                    pass
                elif line[0] == '\n':
                    pass
                else:
                    line_thin = line.strip(' ')
                    line_split = line_thin.split('\t')
                    if line_split[0] != 'rsid':
                        datas = self.fivecol_pull_data(line)
                        chrom = datas['chrom']
                        pos = datas['pos']
                        rid = datas['rsid']
                        ref = datas['ref']
                        alt = datas['genotype']
                        qual = '.'
                        fill = '.'
                        info = '.\n'
                        entry = [chrom, pos, rid, ref, alt, qual, fill, info]
                        new_entry = '\t'.join(entry)
                        otpt.write(new_entry)

        print "%s Converted to VCF" % self.file_path