# -*- coding: utf-8 -*-
#harvest theses from Stavanger U.
#FS: 2023-05-06

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

rpp = 10
pages = 1
skipalreadyharvested = True

publisher = 'Stavanger U.'

jnlfilename = 'THESES-STAVANGER-%s' % (ejlmod3.stampoftoday())

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

hdr = {'User-Agent' : 'Magic Browser'}
recs = []
for dep in ['2655762', '182624', '181845']:
    for page in range(pages):        
        tocurl = 'https://uis.brage.unit.no/uis-xmlui/handle/11250/' + dep + '/discover?rpp=' + str(rpp) + '&etal=0&scope=&group_by=none&page=' + str(page+1) + '&sort_by=dc.date.issued_dt&order=desc'
        ejlmod3.printprogress("=", [[dep], [page+1, pages], [tocurl]])
        try:
            req = urllib.request.Request(tocurl, headers=hdr)
            tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
            time.sleep(4)
        except:
            print("retry %s in 180 seconds" % (tocurl))
            time.sleep(180)
            driver.get(tocurl)
            req = urllib.request.Request(tocurl, headers=hdr)
            tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        recs += ejlmod3.getdspacerecs(tocpage, 'https://uis.brage.unit.no', alreadyharvested=alreadyharvested)

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['link']]])
    try:
        req = urllib.request.Request(rec['link'], headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        time.sleep(4)
    except:
        print("retry %s in 180 seconds" % (rec['link']))
        time.sleep(180)
        req = urllib.request.Request(rec['link'], headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'citation_isbn', 'citation_language',
                                        'DCTERMS.issued', 'DCTERMS.abstract',  'DC.subject',
                                        'citation_pdf_url', 'citation_date', 'DC.rights', 'DC.contributor'])
    rec['autaff'][-1].append(publisher)
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
