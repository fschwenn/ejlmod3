# -*- coding: utf-8 -*-
#harvest theses from Colorado State U., Fort Collins
#FS: 2021-12-06
#FS: 2023-03-29
#FS: 2023-11-28

import sys
import os
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import undetected_chromedriver as uc

publisher = 'Colorado State U., Fort Collins'
jnlfilename = 'THESES-ColoradoStateU-%s' % (ejlmod3.stampoftoday())

rpp = 40
skipalreadyharvested = True
pages = 1
boring = []

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
for (fc, dep) in [('s', '5988f96d-c5c7-4fbb-84bd-15efa8ac4138'),
                  ('m', 'a6f26758-6e22-40d7-bf0f-2bf93fcee300'),
                  ('c', '261a684c-5a74-4b9c-aec7-3363574844a2'),
                  ('', '17a53586-f4a5-44cc-b854-a94274964986')]:
    for page in range(pages):
        tocurl = 'https://mountainscholar.org/collections/' + dep + '?cp.page=' + str(page+1) + '&cp.rpp=' + str(rpp)
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
        baseurl = 'https://mountainscholar.org'
        
        for rec in ejlmod3.ngrx(tocpage, baseurl, ['dc.contributor.author', 'dc.date.issued', 'dc.description.abstract', 'dc.identifier', 'dc.identifier.uri', 'dc.language', 'dc.rights', 'dc.title', 'thesis.degree.discipline', 'thesis.degree.level', 'thesis.degree.name'], boring=boring, alreadyharvested=alreadyharvested):
            for author in rec['autaff'][1:]:
                if re.search('advisor', author[0]):
                    rec['supervisor'].append([re.sub(', advisor', '', author[0])])                
            rec['autaff'] = [[ rec['autaff'][0][0], publisher ]]
            if fc:
                rec['fc'] = fc
            ejlmod3.printrecsummary(rec)
            #print(rec['thesis.metadata.keys'])
            recs.append(rec)
        print('  %i records so far' % (len(recs)))
        time.sleep(20)
ejlmod3.writenewXML(recs, publisher, jnlfilename)
