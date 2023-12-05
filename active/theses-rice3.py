# -*- coding: utf-8 -*-
#harvest theses from Rice University
#JH+FS: 2021-11-04
#FS: 2023-01-10
#FS: 2023-12-02

import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import ejlmod3
import os
import sys
import re

pages = 3
rpp = 100
skipalreadyharvested = True

publisher = 'Rice U.'
jnlfilename = 'THESES-RICE-%s' % (ejlmod3.stampoftoday())

boring = ['Humanities', 'History', 'Chemistry', 'Biochemistry and Cell Biology',
          'Bioengineering', 'Chemical and Biomolecular Engineering',
          'Civil and Environmental Engineering', 'Music', 'Political Science',
          'Psychology', 'Social Sciences', 'Ecology and Evolutionary Biology',
          'Systems, Synthetic and Physical Biology', 'Business', 'Chemical Engineering',
          'Earth Science', 'Social Sciences', 'Anthropology', 'Biochemistry and Cell Biology',
          'Chemical and Biomolecular Engineering', 'Civil and Environmental Engineering',
          'Ecology and Evolutionary Biology', 'Economics',
          'Materials Science and NanoEngineering', 'Mechanical Engineering',
          'Political Science', 'Sociology']

# Initilize Webdriver
options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium'
options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

recs = []
for page in range(pages):
    tocurl = 'https://repository.rice.edu/collections/5aa4da72-3dd6-4196-9ca2-0eb55538e94e?cp.page=' + str(page+1) + '&cp.rpp=' + str(rpp)
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
    baseurl = 'https://repository.rice.edu'
        
    for rec in ejlmod3.ngrx(tocpage, baseurl, ['dc.contributor.advisor', 'dc.creator', 'dc.date.issued', 'dc.description.abstract', 'dc.embargo.lift', 'dc.embargo.terms', 'dc.identifier.uri', 'dc.subject', 'dc.title', 'thesis.degree.department', 'thesis.degree.discipline', 'thesis.degree.name'], boring=boring, alreadyharvested=alreadyharvested):
        rec['autaff'][-1].append(publisher)
        ejlmod3.printrecsummary(rec)
        #print(rec['thesis.metadata.keys'])
        recs.append(rec)
    print('  %i records so far' % (len(recs)))
    time.sleep(20)
ejlmod3.writenewXML(recs, publisher, jnlfilename)

    
