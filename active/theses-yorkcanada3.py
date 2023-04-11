# -*- coding: utf-8 -*-
#harvest theses from York U., Canada
#FS: 2021-09-15
#FS: 2023-01-06

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import json

rpp = 10
pages = 1+1
skipalreadyharvested = True

publisher = 'York U., Canada'

jnlfilename = 'THESES-YorkCanada-%s' % (ejlmod3.stampoftoday())

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []
options = uc.ChromeOptions()
options.headless=True
options.binary_location='/usr/bin/google-chrome'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

recs = []
for dep in ['27569', '28582', '38508']:
    for page in range(pages):        
        tocurl = 'https://yorkspace.library.yorku.ca/xmlui/handle/10315/' + dep + '/discover?rpp=' + str(rpp) + '&page=' + str(page+1) + '&sort_by=dc.date.issued_dt&order=desc'
        ejlmod3.printprogress("=", [[dep], [page+1, pages], [tocurl]])
        try:
            driver.get(tocurl)
            tocpage = BeautifulSoup(driver.page_source, features="lxml")
            time.sleep(4)
        except:
            print("retry %s in 180 seconds" % (tocurl))
            time.sleep(180)
            driver.get(tocurl)
            tocpage = BeautifulSoup(driver.page_source, features="lxml")
        for rec in ejlmod3.getdspacerecs(tocpage, 'https://yorkspace.library.yorku.ca', alreadyharvested=alreadyharvested):
            if dep == '27569':
                rec['fc'] = 'm'
            elif dep == '38508':
                rec['fc'] = 'c'
            recs.append(rec)

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['link']]])
    try:
        driver.get(rec['link'])
        artpage = BeautifulSoup(driver.page_source, features="lxml")
        time.sleep(4)
    except:
        print("retry %s in 180 seconds" % (rec['link']))
        time.sleep(180)
        driver.get(rec['link'])
        artpage = BeautifulSoup(driver.page_source, features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'DCTERMS.issued', 'DCTERMS.abstract',  'DC.subject',
                                        'citation_pdf_url', 'citation_date', 'DC.rights', 'DC.contributor'])
    rec['autaff'][-1].append(publisher)
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
