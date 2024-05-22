# -*- coding: utf-8 -*-
#harvest theses Regina U.
#FS: 2021-12-21
#FS: 2023-03-29
#FS: 2023-12-02

import sys
import os
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import undetected_chromedriver as uc

publisher = 'Regina U.'
jnlfilename = 'THESES-REGINA-%s' % (ejlmod3.stampoftoday())

rpp = 40
skipalreadyharvested = True
pages = 2

boring = ['Biochemistry', 'Biology', 'Clinical Psychology', 'Education',
          'Engineering - Electronic Systems', 'Engineering - Environmental Systems',
          'Engineering - Petroleum Systems', 'Experimental and Applied Psychology',
          'Geology', 'History', 'Interdisciplinary Studies', 'Public Policy',
          'Chemistry', 'Engineering - Industrial Systems', 'Engineering - Process Systems',
          'Geography', 'Kinesiology and Health Studies', 'Canadian Plains Studies',
          'Engineering - Software Systems', 'Psychology', 'Kinesiology', 'Media Studies',
          'Police Studies', 'olitical Science', 'Social Work', 'Media and Artistic Research']

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []


options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium'
options.binary_location='/usr/bin/google-chrome'
options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

recs = []
for page in range(pages):
    tocurl = 'https://ourspace.uregina.ca/collections/49f1d500-d514-427c-ba40-167d0c0807a8?cp.page=' + str(page+1) + '&cp.rpp=' + str(rpp)
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    try:
        driver.get(tocurl)
        time.sleep(5)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    except:
        time.sleep(60)
        driver.get(tocurl)
        time.sleep(5)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    baseurl = 'https://ourspace.uregina.ca'
        
    for rec in ejlmod3.ngrx(tocpage, baseurl, ['dc.contributor.advisor', 'dc.contributor.author', 'dc.date.issued', 'dc.description.abstract', 'dc.identifier.uri', 'dc.title', 'thesis.degree.discipline', 'thesis.degree.name'], boring=boring, alreadyharvested=alreadyharvested):
        rec['autaff'][-1].append(publisher)
        ejlmod3.printrecsummary(rec)
        #print(rec['thesis.metadata.keys'])
        recs.append(rec)
    print('  %i records so far' % (len(recs)))
    time.sleep(20)
ejlmod3.writenewXML(recs, publisher, jnlfilename)

    
