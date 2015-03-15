__author__ = 'asherkhb'
#Script to Obtain Multiple Datasets from PGP
#Optimized for 23andMe TSV SNP Variant Data
#
#by Asher Baltzell
#Last Update 3/14/15
#Dependencies: requests, wget
version = '1.1.0'

import os
import datetime
import subprocess
import requests
import re
import zipfile

# Practice data dictionary
practice = {'huD2F73D': ['https://my.pgp-hms.org/user_file/download/1092', 'Health Filler'],
            'hu589D0B': ['https://my.pgp-hms.org/user_file/download/83', 'Health Filler']}

# Build Unique Data Repository
# Return Repository name.
def buildDataRepo():
    #Create a unique instance variable based on second-millisecond
    unique =  datetime.datetime.now().strftime("%S%f")
    #Create a repository folder for imported data based on the unique instance identifier
    repopath = './experiments-%s' % unique
    #If unique repo path already exists, print error message and exit program
    if os.path.exists(repopath):
        print("Operation Error - Please Try Again")
        exit()
    #If unique repo does not exist, create it. Return the repository name.
    if not os.path.exists(repopath):
        os.mkdir(repopath)
    return repopath

# Determine if Files are .txt or .zip
# Return file type
def textVsZip(link):
        file_type = ''
        #Send request for HTTP head document, then extract content-type into variable "content"
        head = requests.head(link)
        content = head.headers['content-type']
        #RE search for file-type, assign file type to variable "file_type"
        if re.search('text', content):
            file_type = "txt"
        if re.search('zip', content):
            file_type = "zip"
        #Return file type
        return file_type

# Download Data Sets
# Experiments contained in dictionary with {key:values} of {'huID': ['download-link', <other content>, ...]
# Also requires repository folder to be specified
def getData(experiments, repo):
    #Iterate through experiment dictionary.
    for key in experiments:
        #Define download link from dictionary, use textVsZip for file type, then define file path.
        file_link = experiments[key][0]
        file_type = textVsZip(file_link)
        file_path = '%s/%s.%s' % (repo, key, file_type)
        #WGET File
        #command: wget -O <output file location and name> <website>
        wget = "wget -O %s %s" % (file_path, file_link)
        subprocess.call(wget, shell=True)
        #Unzip Zipped Files
        if file_type == "zip":
            #Create a ZipFile object
            zip = zipfile.ZipFile(file_path)
            #Create a list of ZipFile contents
            zip_list = zipfile.ZipFile.namelist(zip)
            #Create variables with old content name and new (huID) content name
            old_name = "%s/%s" % (repo, zip_list[0])
            new_name = file_path.replace('.zip', '.txt')
            #Unzip ZipFile
            unzip = "unzip %s -d ./%s " % (file_path, repo)
            subprocess.call(unzip, shell=True)
            #Rename file contents with huID and then remove zip file.
            os.rename(old_name, new_name)
            os.remove(file_path)

# Execute Script
repo = buildDataRepo()
getData(practice,repo)