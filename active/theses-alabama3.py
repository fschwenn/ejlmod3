# -*- coding: utf-8 -*-
#harvest theses from Alabama U.
#FS: 2021-09-15
#FS: 2023-04-11
#FS: 2024-01-08

import sys
import os
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
import re
import ejlmod3
import time

skipalreadyharvested = True
rpp = 10
pages = 2

publisher = 'Alabama U.'
jnlfilename = 'THESES-ALABAMA-%s' % (ejlmod3.stampoftoday())

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []
    
options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

baseurl = 'https://ir.ua.edu'


recs = []
for (fc, dep) in [('', '2254008d-7c6d-44ed-a558-b4f4d528e4a9'),
                  ('m', 'c85afc3c-09ee-4721-8865-81f277a1cd17'),
                  ('c', '9b9eccd5-0566-4a81-b0c3-6868c0e77001'),
                  ('c', '6fcf7a33-64f8-48bf-98ef-826ffe8da3f0')]:
    for page in range(pages):
        tocurl = 'https://ir.ua.edu/collections/' + dep + '?cp.page=' + str(page+1) + '&cp.rpp=' + str(rpp)
        ejlmod3.printprogress('=', [[dep], [page+1, pages], [tocurl]])
        try:
            driver.get(tocurl)
            time.sleep(5)
            tocpage = BeautifulSoup(driver.page_source, features="lxml")
        except:
            time.sleep(60)
            driver.get(tocurl)
            tocpage = BeautifulSoup(driver.page_source, features="lxml")
    
        for rec in ejlmod3.ngrx(tocpage, baseurl, ['dc.contributor.advisor', 'dc.contributor.author', 
                                                   'dc.date.issued', 'dc.rights.uri', 'dc.format.extent',
                                                   'dc.contributor.department', 'dc.rights', 
                                                   'dc.description.abstract', 'dc.identifier.uri',
                                                   'dc.subject', 'dc.title',  'etdms.degree.discipline',
                                                   'etdms.degree.name', 'etdms.degree.department'],
                                alreadyharvested=alreadyharvested, fakehdl=True):
            rec['autaff'][-1].append(publisher)
            ejlmod3.printrecsummary(rec)
            #print(rec['thesis.metadata.keys'])
            recs.append(rec)
        print('  %i records so far' % (len(recs)))
        time.sleep(20)
ejlmod3.writenewXML(recs, publisher, jnlfilename)

