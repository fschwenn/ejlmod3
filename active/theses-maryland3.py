# -*- coding: utf-8 -*-
#harvest Maryland University theses
#FS: 2018-01-31
#FS: 2022-11-18
#FS: 2023-12-02

import getopt
import os
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import undetected_chromedriver as uc

publisher = 'Maryland U., College Park'

jnlfilename = 'THESES-MARYLAND-%s' % (ejlmod3.stampoftoday())

rpp = 60
pages = 1
years = 2 
skipalreadyharvested = True
boring = ['Biophysics (BIPH)']


if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

options = uc.ChromeOptions()
#options.binary_location='/usr/bin/chromium'
options.binary_location='/usr/bin/google-chrome'
options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)


recs = []
for (fc, dep) in [('m', '95a82c34-4a9e-4c60-b7ca-97e72aae87f8'),
                  ('a', '99f30899-ac38-4c92-ba8e-93acf93ff8f5'),
                  ('c', 'b7b14361-c1de-4b2c-8250-62ad1064f457'),
                  ('', '5b1551c7-d9b5-4bed-aa6b-7bde543a32a1')]:
    for page in range(pages):
        tocurl = 'https://drum.lib.umd.edu/collections/' + dep + '?cp.page=' + str(page+1) + '&cp.rpp=' + str(rpp)
        ejlmod3.printprogress('=', [[fc,dep], [page+1, pages], [tocurl]])
        try:
            driver.get(tocurl)
            time.sleep(5)
            tocpage = BeautifulSoup(driver.page_source, features="lxml")
        except:
            time.sleep(60)
            driver.get(tocurl)
            time.sleep(5)
            tocpage = BeautifulSoup(driver.page_source, features="lxml")
        baseurl = 'https://drum.lib.umd.edu'
        
        for rec in ejlmod3.ngrx(tocpage, baseurl, ['dc.contributor.advisor', 'dc.contributor.author', 'dc.contributor.department', 'dc.date.issued', 'dc.description.abstract', 'dc.identifier.uri', 'dc.subject.pqcontrolled', 'dc.subject.pquncontrolled', 'dc.title'], boring=boring, alreadyharvested=alreadyharvested):
            rec['autaff'][-1].append(publisher)
            if fc:
                rec['fc'] = fc
            ejlmod3.printrecsummary(rec)
            #print(rec['thesis.metadata.keys'])
            recs.append(rec)
        print('  %i records so far' % (len(recs)))
        time.sleep(20)
ejlmod3.writenewXML(recs, publisher, jnlfilename)

    
