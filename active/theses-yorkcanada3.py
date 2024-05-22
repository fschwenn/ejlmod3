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

rpp = 20
pages = 1+1+2
skipalreadyharvested = True

publisher = 'York U., Canada'

jnlfilename = 'THESES-YorkCanada-%s' % (ejlmod3.stampoftoday())

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []
options = uc.ChromeOptions()
#options.headless=True
options.binary_location='/usr/bin/google-chrome'
options.add_argument('--headless')
#options.binary_location='/usr/bin/chromium'
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
#        for rec in ejlmod3.getdspacerecs(tocpage, 'https://yorkspace.library.yorku.ca', alreadyharvested=alreadyharvested):
        for rec in ejlmod3.ngrx(tocpage, 'https://yorkspace.library.yorku.ca', ['dc.contributor.advisor', 'dc.contributor.author',
                                                                                'dc.degree.discipline', 'dc.degree.level',
                                                                                'dc.degree.name', 'dc.description.abstract',
                                                                                'dc.identifier.uri', 'dc.rights', 'dc.subject',
                                                                                'dc.title', 'dc.date.issued'], alreadyharvested=alreadyharvested):
            #print(rec['thesis.metadata.keys'])
            if dep == '27569':
                rec['fc'] = 'm'
            elif dep == '38508':
                rec['fc'] = 'c'
            rec['autaff'][-1].append(publisher)
            ejlmod3.printrecsummary(rec)
            recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
