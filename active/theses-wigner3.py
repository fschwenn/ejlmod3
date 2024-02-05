# -*- coding: utf-8 -*-
#harvest theses from Wigner RCP, Budapest
#FS: 2022-05-02
#FS: 2023-02-24
#FS: 2024-01-29

import sys
import os
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

jnlfilename = 'THESES-WignerRCP-%s' % (ejlmod3.stampoftoday())

Scheiss Javascript

publisher = 'Wigner RCP, Budapest'

hdr = {'User-Agent' : 'Magic Browser'}

rpp = 20
pages = 2
boring = []
years = 2
skipalreadyharvested = True

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

recs = []
baseurl = 'https://repozitorium.omikk.bme.hu'
for (fc, dep) in [('', 'ac1e1b89-9870-43c0-8882-0b6492b8498c'),
                  ('', '2d9da438-1b2a-4994-a39b-0d4fe5fb6096'),
                  ('', '4e37ba63-2d98-482a-98d2-3cda2ad0c86b'),
                  ('', 'd851348c-1950-402c-84e9-415d183a7901')]:
    for page in range(pages):
        tocurl = baseurl + '/collections/' + dep + '?cp.page=' + str(page+1) + '&cp.rpp=' + str(rpp)
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
        
        for rec in ejlmod3.ngrx(tocpage, baseurl, ['dc.contributor.author', 'dc.date.issued',
                                                   'dc.description.abstract', 'dc.identifier',
                                                   'dc.identifier.uri', 'dc.language', 'dc.rights',
                                                   'dc.title', 'thesis.degree.discipline',
                                                   'thesis.degree.level', 'thesis.degree.name'],
                                boring=boring, alreadyharvested=alreadyharvested):
            rec['autaff'] = [[ rec['autaff'][0][0], publisher ]]
            if fc:
                rec['fc'] = fc
            ejlmod3.printrecsummary(rec)
            print(rec['thesis.metadata.keys'])
            recs.append(rec)
        print('  %i records so far' % (len(recs)))
        time.sleep(20)
ejlmod3.writenewXML(recs, publisher, jnlfilename)
