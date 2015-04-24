__author__ = 'asherkhb'

#Operation instructions: python initiate.py

import myCoGe


run_date = myCoGe.datetime.now().strftime("%Y%m%d")

# 1. Execute SNPScraper (Partial)
#       - Return JSON of huIDs, download links, health info, sequencer

##myCoGe.scrape_snps(run_date)

# 2. Decode JSON into dictionary (Partial)
#       - Return Dictionary of huIDs, download links, health info

##json_file = './temp/snps_%s.json' % run_date
json_file = './temp/practice_1.json' # For Practice
simple_data, all_data = myCoGe.json_decode(json_file)

# 3. Compare dictionary with File Directory (_directory.txt)
#       - Return modified dictionary

missing_data = myCoGe.compare_to_directory(all_data)


# 4. Download Data
#       - Download missing data fileset.

repo = './temp/tsvs'
downloaded = myCoGe.get_data(missing_data, repo)

# 5. RESOLVE DOWNLOADED/MISSING, GENERATE NEW DICT UPDATE DICT, and PRINT ERROR REPORTS

downloads, absent = myCoGe.list_dict_resolve(downloaded, missing_data)

# 6. Update File Directory

myCoGe.update_directory(downloads)

# 7. Generate Metadata file (Needs Updating)
#

##myCoGe.generate_meta(downloads)

# 8. Convert to VCF
#

for item in downloads:
    file_huid = item
    filename = './temp/tsvs/%s.txt' % item
    vcfname = './data/vcfs/%s.vcf' % item

    experiment = myCoGe.SnpExperiment(file_huid, filename, vcfname)
    experiment.convert_to_vcf()

# 9. Transfer files to iRODS (Partial)
#



# 10. Batch load into CoGe (Incomplete)
#

# 11. Delete temp folder, make new temp folder

##myCoGe.reset_temp()

# 12. Cleanup - Close files and delete any temps.

myCoGe.cleanup()
