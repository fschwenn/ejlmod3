import os

### variables
#max number of record per xml/jsonl file
bunchsize = 10



### at DESY we have to main directories are kept:
#the home directory of the functional account 'library' (small but with backup)
afl = '/afs/desy.de/user/l/library'
#the group directory (large but without backup)
afg = '/afs/desy.de/group'

## subdirectories of those used for the harvesting
#directory where the abstract (+title, +keywors) of each record is stored as text file
absdir = afg + '/library/publisherdata/abs'
#directory where the PDF of each record is stored
pdfdir = afg + '/library/publisherdata/pdf'
#directory were knowledebases are stored
listdir = afl + '/lists'
#directory with all the python programs
procdir = afl + '/proc/python3'
#path were the files are stored which contain the list of xmls from harvesters waiting to be translated to jsonl
retfiles_path = afl + '/proc/retinspire'
#directory were the xml files are stored
xmldir= afl + '/inspire/ejl'
#directory were the doki files are kept
dokidir = afl + '/dok/ejl/backup'
#directory in AFS for temporary files
afstmpdir = afl + '/tmp'
#local directory for temporary files
localtmpdir = '/tmp'
#path were the ontologies for bibclassify are stored
ontdir = afl + '/akw'





host = os.uname()[1]
if host == 'l00schwenn':
    pass
