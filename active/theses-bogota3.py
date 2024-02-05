# -*- coding: utf-8 -*-
#harvest theses from Andes U., Bogota
#FS: 2020-08-28
#FS: 2024-01-29


import undetected_chromedriver as uc
import urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import os
import time

publisher = 'Andes U., Bogota'
jnlfilename = 'THESES-BOGOTA-%s' % (ejlmod3.stampoftoday())
years = 3
rpp = 20
pages = 2
boring = []

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
baseurl = 'https://repositorio.uniandes.edu.co'

for (fc, dep) in [('', 'd06819b0-1c54-4c28-b6d3-a67cec690836'),
                  ('m', '1eb45f49-2a12-409b-89d7-946248148b31')]:
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
        
        for rec in ejlmod3.ngrx(tocpage, baseurl, ['dc.contributor.advisor',
                                                   'dc.contributor.author', 'dc.date.issued',
                                                   'dc.description.abstract', 'dc.identifier',
                                                   'dc.format.extent', 'dc.subject.keyword',
                                                   'dc.subject.themes'
                                                   'dc.identifier.uri', 'dc.language.iso', 'dc.rights.uri',
                                                   'dc.title', 'thesis.degree.discipline',
                                                   'thesis.degree.level', 'thesis.degree.name'],
                                boring=boring, alreadyharvested=alreadyharvested):
            rec['autaff'] = [[ rec['autaff'][0][0], publisher ]]
            if fc:
                rec['fc'] = fc
            ejlmod3.printrecsummary(rec)
            #print(rec['thesis.metadata.keys'])
            recs.append(rec)
        print('  %i records so far' % (len(recs)))
        time.sleep(20)
ejlmod3.writenewXML(recs, publisher, jnlfilename)


