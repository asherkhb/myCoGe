__author__ = 'asherkhb'
# Metadata Generator Script, v.1.0.0
#
# by Asher Baltzell

#Function to generate metadata file.
#Future Updates: Unique Metadata Name
#Input: Dictionary dataset, format {huID:[link, health]}
# Current Metadata Inclusions: Filename*, Name*, Description, Source, Source Link, Sequencer, Health Info
# "*" Denotes CoGe Required Fields
def generateMeta(dataset):
    with open('meta.txt', 'w') as metadata:
        metadata.write("Filename\tName\tDescription\tSource\tSource_link\tSequencer\tHealth Records\n")
        for key in dataset.keys():
            meta = generateItemMeta(key, dataset[key][0], dataset[key][1])
            metadata.write(meta)

#Function to generate individual metadata entries for each experiment
#Requires huID, download link, and health info inputs
def generateItemMeta(huID, link, health):
    filename = "%s_snps.vcf" % huID
    name = "%s_snps" % huID
    description = "SNP Variant Data for %s, obtained from Personal Genome Project (www.personalgenomes.org)" % huID
    source = "PGP"
    source_link = link
    seq = "23andMe"
    health_info = health
    meta = "%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (filename, name, description, source, source_link, seq, health_info)
    return meta
