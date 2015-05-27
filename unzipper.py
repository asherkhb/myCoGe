__author__ = 'asherkhb'

from os import listdir, path, remove, rename
from shutil import move
from subprocess import call
from zipfile import ZipFile


def get_confirmation(prompt):
    get_input = True
    while get_input:
        message = prompt + ' (Y/N): '
        continuation = raw_input(message).upper()
        if continuation == "Y":
            get_input = False
            return True
        elif continuation == "N":
            get_input = False
            return False
        else:
            print "Invalid Input"


def get_zip_list():
    x = listdir('./')
    y = []
    for item in x:
        if path.isfile(item):
            if item[-4:] == '.zip':
                y.append(item)
    return y


filelist = get_zip_list()
start = get_confirmation('There are %s files to unzip. Continue?' % str(len(filelist)))
if start:
    for zippedfile in filelist:
        file_path = '%s.zip' % zippedfile
        print "Processing %s" % file_path
        #Create a ZipFile object.
        try:
            zip_file = ZipFile(file_path)
            #Create a list of ZipFile contents.
            zip_list = ZipFile.namelist(zip_file)
            print "The file contains: " + zip_list
            cont = get_confirmation("Continue with unzipping and renaming %s?" % zip_list[0])
            if cont:
                #Create variables with old content name and new (huID) content name.
                old_name = zip_list[0]
                new_name = file_path.replace('.zip', '.txt')
                #Unzip ZipFile.
                #unzip = "unzip %s -d %s " % (file_path, repository)  # Saved in-case
                unzip = "unzip %s" % file_path
                call(unzip, shell=True)
                #Rename file contents with huID and then remove zip file.
                rename(old_name, new_name)
                new_path = '../tsvs/%s' % new_name
                move(new_name, new_path)
                remove(file_path)
            else:
                continue
        except:
            cont = get_confirmation("Error Unzipping %s. Continue?" % zippedfile)
            if not cont:
                exit()
else:
    exit()