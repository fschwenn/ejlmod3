# -*- coding: utf-8 -*-
#harvest theses from HUB
#FS: 2019-09-13
#FS: 2022-12-20


import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import undetected_chromedriver as uc

jnlfilename = 'THESES-HUB-%s' % (ejlmod3.stampoftoday())
rpp = 50
publisher = 'Humboldt U., Berlin'

hdr = {'User-Agent' : 'Magic Browser'}
options = uc.ChromeOptions()
options.headless=True
options.binary_location='/usr/bin/chromium-browser'
options.add_argument('--headless')
driver = uc.Chrome(version_main=103, options=options)
prerecs = []
hdls = []
for (ddc, fc) in [('530+Physik', ''),  ('510+Mathematik', 'm'), ('539+Moderne+Physik', ''),
                  ('004+Informatik', 'c')]:
    tocurl = 'https://edoc.hu-berlin.de/handle/18452/2/discover?sort_by=dc.date.issued_dt&order=desc&rpp=' +str(rpp) + '&filtertype_0=subjectDDC&filter_relational_operator_0=equals&filter_0=' + ddc 
    print(tocurl)
    driver.implicitly_wait(120)
    driver.get(tocurl)
    tocpage = BeautifulSoup(driver.page_source, features="lxml")
    #print(tocpage.text)
    time.sleep(3)
    for rec in ejlmod3.getdspacerecs(tocpage, 'https://edoc.hu-berlin.de', divclass='ds-artifact-item'):
        if fc: rec['fc'] = 'fc'
        rec['note'].append(ddc)
        if not rec['hdl'] in hdls:
            prerecs.append(rec)
            hdls.append(rec['hdl'])
    print('  %4i records so far' % (len(prerecs)))


recs = []
i = 0
for rec in prerecs:
    i += 1
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['link']]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['DC.identifier', 'citation_title', 'DCTERMS.issued', 'DC.subject',
                                        'DC.language', 'citation_pdf_url', 'DCTERMS.abstract', 'DC.rights'])
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #author
            if meta['name'] == 'DC.creator':
                author = re.sub(' *\[.*', '', meta['content'])
                rec['autaff'] = [[ author ]]
                rec['autaff'][-1].append(publisher)
    recs.append(rec)
    ejlmod3.printrecsummary(rec)
ejlmod3.writenewXML(recs, publisher, jnlfilename)
driver.close()
