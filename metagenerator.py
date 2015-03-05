__author__ = 'asherkhb'

#Takes Dataset as a dictionary with {huID:[link, health]} layout

def generateMeta(dataset):
    with open('meta.txt', 'w') as metadata:
        metadata.write("Filename\tName\tDescription\tSource\tSource_link\tSequencer\tHealth Records\n")
        for key in dataset.keys():
            meta = generateItemMeta(key, dataset[key][0], dataset[key][1])
            metadata.write(meta)
    print "Complete. See meta.txt"


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
