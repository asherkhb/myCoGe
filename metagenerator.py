__author__ = 'asherkhb'
# Metadata Generator Script, v.1.0.0
# Generates metadata for SNP variant files for import into CoGe
#
# by Asher Baltzell
# Last Update: 3/16/15
# Version: 1.0.1


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

# Use Metagenerator to Generate Metadata File for datapoints in data_dict
# generate_meta(dataset_from_json_decoder)