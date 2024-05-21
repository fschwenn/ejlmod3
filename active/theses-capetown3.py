# -*- coding: utf-8 -*-
#harvest theses from University of Cape Town
#FS: 2019-09-25
#FS: 2022-12-20
#FS: 2023-11-28

import sys
import os
from bs4 import BeautifulSoup
import re
import undetected_chromedriver as uc
import ejlmod3
import time

publisher = 'Cape Town U.'
rpp = 40
pages = 7
skipalreadyharvested = True

jnlfilename = 'THESES-CAPETOWN-%s' % (ejlmod3.stampoftoday())

boring = ['Faculty of Commerce', 'Faculty of Health Sciences',
          'Faculty of Humanities', 'Faculty of Law']

options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium'
options.binary_location='/usr/bin/google-chrome'
options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)


if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

recs = []
for page in range(pages):
    tocurl = 'https://open.uct.ac.za/collections/54eb0a16-4729-412a-8839-554727ee22f5?cp.page=' + str(page+1) + '&cp.rpp=' + str(rpp)
    #tocurl = 'https://open.uct.ac.za/browse/dateissued?scope=54eb0a16-4729-412a-8839-554727ee22f5&bbm.page=' + str(page+1) + '&startsWith=2023'
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
    baseurl = 'https://open.uct.ac.za'
    
    for rec in ejlmod3.ngrx(tocpage, baseurl, ['dc.contributor.advisor', 'dc.contributor.author', 'dc.date.issued', 'dc.description.abstract', 'dc.identifier.uri', 'dc.publisher.faculty', 'dc.subject', 'dc.title'], boring=boring, alreadyharvested=alreadyharvested):
        rec['autaff'][-1].append(publisher)
        ejlmod3.printrecsummary(rec)
        #print(rec['thesis.metadata.keys'])
        recs.append(rec)
    print('  %i records so far' % (len(recs)))
    time.sleep(20)
ejlmod3.writenewXML(recs, publisher, jnlfilename)
