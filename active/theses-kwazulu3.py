# -*- coding: utf-8 -*-
#harvest theses from KwaZulu Natal U.
#FS: 2022-04-20
#FS: 2023-03-27
#FS: 2024-01-22

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
import re
import ejlmod3
import time


pages = 1
rpp = 100
years = 2
skipalreadyharvested = True

publisher = 'KwaZulu Natal U.'
jnlfilename = 'THESES-KWAZULU-%s' % (ejlmod3.stampoftoday())

recs = []
hdr = {'User-Agent' : 'Magic Browser'}

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

baseurl = 'https://researchspace.ukzn.ac.za'


recs = []
for (dep, fc) in [('cb394e9b-111c-4ff4-9ac5-d4f86536c315', 'm'),
                  ('3e198bf6-5d1d-4a8f-bf84-6da5060be658', ''),
                  ('6ac6889b-c8f5-4576-bc66-e6ca7c37b08e', 'm'),
                  ('c1f53a9b-a630-4a86-b79b-d9ab0df2e86f', 'c')]:
    for page in range(pages):
        tocurl = baseurl + '/collections/' + dep +  '?cp.page=' + str(page+1) + '&cp.rpp=' + str(rpp)
        ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
        try:
            driver.get(tocurl)
            time.sleep(5)
            tocpage = BeautifulSoup(driver.page_source, features="lxml")
        except:
            time.sleep(60)
            driver.get(tocurl)
            tocpage = BeautifulSoup(driver.page_source, features="lxml")
        
        for rec in ejlmod3.ngrx(tocpage, baseurl, ['dc.contributor.advisor', 'dc.creator', 
                                                   'dc.date.issued', 'dc.subject.other',
                                                   'dc.rights', 'dc.language.iso', 
                                                   'dc.description.abstract', 'dc.identifier.uri',
                                                   'dc.title'],
                                alreadyharvested=alreadyharvested):
            if fc: rec['fc'] = fc
            rec['autaff'][-1].append(publisher)
            ejlmod3.printrecsummary(rec)
            #print(rec['thesis.metadata.keys'])
            if 'date' in rec and re.search('[12]\d\d\d', rec['date']) and int(re.sub('.*([12]\d\d\d).*', r'\1', rec['date'])) <= ejlmod3.year(backwards=years):
                print('    too old:', rec['date'])
            else:
                recs.append(rec)
        print('  %i records so far' % (len(recs)))
        time.sleep(20)
ejlmod3.writenewXML(recs, publisher, jnlfilename)
