# -*- coding: utf-8 -*-
#harvest theses from Alabama U.
#FS: 2021-09-15
#FS: 2023-04-11

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

skipalreadyharvested = True
rpp = 10
pages = 1

publisher = 'Alabama U.'
jnlfilename = 'THESES-ALABAMA-%s' % (ejlmod3.stampoftoday())

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
    
recs = []
for page in range(pages):
    for dep in ['120', '126']:
        tocurl = 'https://ir.ua.edu/handle/123456789/' + dep + '/discover?rpp=' + str(rpp) + '&page=' + str(page+1) + '&sort_by=dc.date.issued_dt&order=desc'
        ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
        try:
            tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
            time.sleep(3)
        except:
            print("retry %s in 180 seconds" % (tocurl))
            time.sleep(180)
            tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
        for rec in ejlmod3.getdspacerecs(tocpage, 'https://ir.ua.edu', fakehdl=True):
            if dep == '120':
                rec['fc'] = 'm'
            if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
                if not rec['link'] in ['https://ir.ua.edu/handle/123456789/8322']:
                    recs.append(rec)

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['link']]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(3)
    except:
        print("retry %s in 180 seconds" % (rec['link']))
        time.sleep(180)
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'DCTERMS.issued', 'DCTERMS.abstract',
                                        'DC.subject', 'citation_pdf_url', 'citation_date',
                                        'DCTERMS.extent', 'DC.rights'])
    rec['autaff'][-1].append(publisher)
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
