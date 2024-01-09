# -*- coding: utf-8 -*-
#harvest theses from Duke U.
#FS: 2019-12-13
#FS: 2023-02-17
#FS: 2024-01-08

import sys
import os
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Duke U. (main)'
jnlfilename = 'THESES-DUKE_U-%s' % (ejlmod3.stampoftoday())

pages = 10
rpp = 40
skipalreadyharvested = True

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

boring = ['Mechanical Engineering and Materials Science', 'Art, Art History, and Visual Studies',
          'Biomedical Engineering', 'Business Administration', 'Chemistry',
          'Civil and Environmental Engineering', 'Classical Studies', 'Ecology', 'Economics',
          'Environmental Policy', 'Immunology', 'Materials Science and Engineering',
          'Mechanical Engineering and Materials Science', 'Molecular Genetics and Microbiology',
          'Pathology', 'Political Science', 'Psychology and Neuroscience', 'Romance Studies',
          'Biochemistry', 'Biology', 'Cell Biology', 'Environment', 'Evolutionary Anthropology',
          'German Studies', 'History', 'Literature', 'Marine Science and Conservation',
          'Molecular Cancer Biology', 'Music', 'Neurobiology', 'Pharmacology', 'Public Policy',
          'Religion', 'Biostatistics and Bioinformatics Doctor of Philosophy',
          'Computational Biology and Bioinformatics', 'Cultural Anthropology',
          'Earth and Ocean Sciences', 'English', 'Genetics and Genomics', 'Medical Physics',
          'Nursing', 'Sociology']




options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

baseurl = 'https://dukespace.lib.duke.edu'

recs = []
for page in range(pages):
    tocurl = 'https://dukespace.lib.duke.edu/collections/fadcf88f-ca4d-406b-8046-65e56de0b8eb?cp.page=' + str(page+1) + '&cp.rpp=' + str(rpp)
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    try:
        driver.get(tocurl)
        time.sleep(5)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    except:
        time.sleep(60)
        driver.get(tocurl)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    
    for rec in ejlmod3.ngrx(tocpage, baseurl, ['dc.contributor.advisor', 'dc.contributor.author', 
                                               'dc.date.issued', 'dc.rights.uri', 
                                               'dc.department', 'dc.rights', 
                                               'dc.description.abstract', 'dc.identifier.uri',
                                               'dc.subject', 'dc.title', 'duke.embargo.release'],
                            boring=boring, alreadyharvested=alreadyharvested):
        rec['autaff'][-1].append(publisher)
        ejlmod3.printrecsummary(rec)
        #print(rec['thesis.metadata.keys'])
        if 'duke.embargo.release' in rec['thesis.metadata.keys']:
            del rec['pdf_url']
        recs.append(rec)
    print('  %i records so far' % (len(recs)))
    time.sleep(20)
ejlmod3.writenewXML(recs, publisher, jnlfilename)



