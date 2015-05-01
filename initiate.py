__author__ = 'asherkhb'

#Operation instructions: "python initiate.py 2>&1 | tee ./temp/terminal_log.txt"

import myCoGe

# 0. Book keeping

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

json_file = './temp/snps_%s.json' % run_date
##json_file = './temp/practice_1.json'  # For Practice
simple_data, all_data = myCoGe.json_decode(json_file)

# 3. Compare dictionary with File Directory (_directory.txt)
#       - Return modified dictionary

missing_data = myCoGe.compare_to_directory(all_data)

# 4. Download Data
#       - Download missing data fileset.

repo = './data/tsvs'
download = myCoGe.get_data(missing_data, repo)


# 5. RESOLVE DOWNLOADED/MISSING, GENERATE NEW DICT UPDATE DICT, and PRINT ERROR REPORTS

downloads, absent = myCoGe.list_dict_resolve(download, missing_data)


# 6. Update File Directory

myCoGe.update_directory(downloads)

# 7. Generate Metadata file (Needs Updating)
#

##myCoGe.generate_meta(downloads)

# 8. Convert to VCF
#

for item in downloads:
    file_huid = item
    filename = './data/tsvs/%s.txt' % item
    vcfname = './data/vcfs/%s.vcf' % item

    experiment = myCoGe.SnpExperiment(file_huid, filename, vcfname)
    experiment.convert_to_vcf()

print "File Conversions Complete"

# 9. Transfer files to iRODS
#

myCoGe.isync(irods_pass)

# 10. Batch load into CoGe (Incomplete)
#

# 11. Generate Logs, Dump for finalize.py.

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

##myCoGe.send_email_log(downloads, email_log_attachments)

# 12. Cleanup - Close files.

myCoGe.cleanup()