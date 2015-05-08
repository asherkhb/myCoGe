__author__ = 'asherkhb'

import myCoGe

#list of huIDs to convert:
huids = ['hu016B28', 'hu019BBA', 'hu0369A1', 'hu0684DB', 'hu0E64A1', 'hu11DF5B', 'hu152E96', 'hu155D20', 'hu17DFDB', 'hu1A7894', 'hu1BDBA5', 'hu1BDE7A', 'hu1DD730', 'hu1F4A47', 'hu1F73AB', 'hu28F39C', 'hu2A4D22', 'hu2DF992', 'hu345185', 'hu394092', 'hu3AD9A6', 'hu3B89BD', 'hu3DDADF', 'hu3F37F2', 'hu3F8570', 'hu4AEB32', 'hu589685', 'hu59141C', 'hu5C3F07', 'hu5FCE15', 'hu5FD679', 'hu60AB7C', 'hu619F51', 'hu620523', 'hu635045', 'hu63DA55', 'hu65286B', 'hu654B61', 'hu6D1115', 'hu6D50BE', 'hu6ED94A', 'hu76CAA5', 'hu790518', 'hu79AB64', 'hu7AC640', 'hu7B594C', 'hu84787F', 'hu8578CD', 'hu88998A', 'hu911FDC', 'hu918363', 'hu939B7C', 'hu974CFF', 'huA09927', 'huA7A170', 'huB066C2', 'huB10361', 'huB2A9E7', 'huB2CFD0', 'huB36CAB', 'huB4D223', 'huB63C0C', 'huBA3075', 'huBBEB5D', 'huBE28C7', 'huC39675', 'huC5824D', 'huC93106', 'huCFD853', 'huD85057', 'huDF0DAF', 'huE24396', 'huE35226', 'huE9E777', 'huEEBCF4', 'huF4A676', 'huF5F075', 'huF7E042', 'huFE71F3']

for id in huids:
    file_huid = id
    filename = './data/tsvs/%s.txt' % id
    vcfname = './data/vcfs/%s.vcf' % id

    experiment = myCoGe.SnpExperiment(file_huid, filename, vcfname)
    experiment.convert_to_vcf()

print "File Conversions Complete"