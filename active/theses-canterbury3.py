# -*- coding: utf-8 -*-
#harvest theses from Canterbury U.
#FS: 2020-09-11
#FS: 2023-04-26
#FS: 2023-11-28


import sys
import os
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import undetected_chromedriver as uc

publisher = 'Canterbury U.'
jnlfilename = 'THESES-CANTERBURY-%s' % (ejlmod3.stampoftoday())

rpp = 40
pages = 8
skipalreadyharvested = True
boring = ['Antarctic Studies', 'Geography', 'Geology', 'Speech and Language Therapy', 'Biochemistry',
          'Biological Sciences', 'Biology', 'Chemistry', 'Disaster Risk and Resilience', 'Ecology',
          'Environmental Chemistry', 'Environmental Sciences', 'Psychology',
          'Speech and Language Sciences', 'Water Resource Management']


if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

recs = []
for page in range(pages):
    tocurl = 'https://ir.canterbury.ac.nz/collections/ccf82095-90b1-41dd-a18e-06ae942f5513?cp.page=' + str(page+1) + '&cp.rpp=' + str(rpp)
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    try:
        driver.get(tocurl)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    except:
        time.sleep(60)
        driver.get(tocurl)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    baseurl = 'https://ir.canterbury.ac.nz'    
    for rec in ejlmod3.ngrx(tocpage, baseurl, ['dc.contributor.author', 'dc.date.issued', 'dc.description.abstract', 'dc.identifier.uri', 'dc.language', 'dc.title', 'dc.rights', 'dc.rights.uri', 'thesis.degree.discipline', 'thesis.degree.name'], boring=boring, alreadyharvested=alreadyharvested):
        rec['autaff'][-1].append(publisher)
        #ejlmod3.printrecsummary(rec)
        print(rec['thesis.metadata.keys'])
        recs.append(rec)
    print('  %i records so far' % (len(recs)))
    time.sleep(20)
ejlmod3.writenewXML(recs, publisher, jnlfilename)
