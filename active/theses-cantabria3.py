# -*- coding: utf-8 -*-
#harvest theses from Cantabria U., Santander
#FS: 2020-08-25
#FS: 2023-03-13

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

skipalreadyharvested = True

jnlfilename = 'THESES-CANTABRIA-%s' % (ejlmod3.stampoftoday())
publisher = 'Cantabria U., Santander'

hdr = {'User-Agent' : 'Magic Browser'}

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

recs = []
for fac in ['103', '133', '123', '1838']:
    tocurl = 'https://repositorio.unican.es/xmlui/handle/10902/' + fac + '/discover?rpp=10&etal=0&group_by=none&page=1&sort_by=dc.date.issued_dt&order=desc'
    ejlmod3.printprogress('=', [[fac], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    for rec in ejlmod3.getdspacerecs(tocpage, 'https://repositorio.unican.es', alreadyharvested=alreadyharvested):
        new = True
        if 'year' in rec and int(rec['year']) < ejlmod3.year(backwards=2):
            new = False
            print('  skip',  rec['year'])
        if new:
            recs.append(rec)
    time.sleep(2)

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['link']]])
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
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'DC.contributor', 'DC.title', 'DC.rights',
                                        'DCTERMS.issued', 'citation_isbn', 'DC.subject',
                                        'citation_pdf_url', 'DC.language'])
    rec['autaff'][-1].append(publisher)
    #abstract
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'DCTERMS.abstract'}):
        if re.search(' the ',  meta['content']):
            rec['abs'] = re.sub('ABSTRACT: ', '', meta['content'])
        else:
            rec['absspa'] = re.sub('RESUMEN: ', '', meta['content'])
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
