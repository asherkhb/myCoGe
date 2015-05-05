__author__ = 'asherkhb'

#Operation instructions: "python initiate.py 2>&1 | tee ./temp/terminal_log.txt"

import myCoGe


# 0. Initialize
#       - Perform tasks to initialize run.

myCoGe.initialize()

run_date = myCoGe.datetime.now().strftime("%Y%m%d")
configs = myCoGe.pickle.load(open('config.p', 'rb'))
auth_k = configs['key']
auth_s = configs['secret']
irods_pass = configs['pass']


# 1. Execute SNPScraper (Partial)
#       - Return JSON of huIDs, download links, health info, sequencer

myCoGe.scrape_snps(run_date)


# 2. Decode JSON into dictionary (Partial)
#       - Return Dictionary of huIDs, download links, health info

#json_file = './temp/practice_1.json'  # For Practice
json_file = './temp/snps_%s.json' % run_date
simple_data, all_data = myCoGe.json_decode(json_file)


# 3. Compare dictionary with File Directory (_directory.txt)
#       - Return modified dictionary

missing_data = myCoGe.compare_to_directory(all_data)

# 4. Download Data
#       - Download missing data files.

repo = './data/tsvs'
download = myCoGe.get_data(missing_data, repo)


# 5. RESOLVE DOWNLOADED/MISSING, GENERATE NEW DICT UPDATE DICT, and PRINT ERROR REPORTS
#       - Compare the contents of the downloaded files folder with the files intended to be downloaded.

downloads, absent = myCoGe.list_dict_resolve(download, missing_data)

#### Conversions from Already-Obtained Files ####
# To Convert Already Obtained Files, Comment out above lines and begin here.

#downloaded_files = myCoGe.listdir('./data/tsvs/')
#download = []
#for item in downloaded_files:
#        download.append(item.strip('.txt'))
#
#downloads, absent = myCoGe.list_dict_resolve(download, missing_data)
####END####


# 6. Update File Directory
#       - Updates _directory.txt with newly downloaded files.

myCoGe.update_directory(downloads)


# 7. Generate Metadata file (Outdated with New LoadExperiment)
#       - Generate metadata file for LoadBatch

##myCoGe.generate_meta(downloads)


# 8. Convert to VCF
#       - Convert files with experiment class.

for item in downloads:
    file_huid = item
    filename = './data/tsvs/%s.txt' % item
    vcfname = './data/vcfs/%s.vcf' % item

    experiment = myCoGe.SnpExperiment(file_huid, filename, vcfname)
    experiment.convert_to_vcf()

print "File Conversions Complete"

# 9. Transfer files to iRODS
#        - Transfers files to iRODS directory

myCoGe.isync(irods_pass)


# 10. Batch load into CoGe (Needs API Fixing)
#       - Loads experiments into CoGe through API

## CoGe Loading Code - see myCoGe Practice


# 11. Generate Logs, Dump for finalize.py.
#       - Generates logs and pickles important file structures

preserved_datastructures = {'all_data': all_data,
                            'missing_data': missing_data,
                            'should_download': download,
                            'actual_download': downloads,
                            'absent_download': absent}

myCoGe.generate_log_pickles(preserved_datastructures)  # Produces ./temp/pickles.tar.gz

email_log_attachments = [json_file,
                         './data/_directory.txt',
                         './temp/pickles.tar.gz',
                         './temp/terminal_log.txt']

myCoGe.pickle.dump(downloads, open('./temp/finalize_downloads.p', 'wb'))
myCoGe.pickle.dump(email_log_attachments, open('./temp/finalize_email_log_attachments.p', 'wb'))


# 12. Cleanup
#       - Close open files.

myCoGe.cleanup()