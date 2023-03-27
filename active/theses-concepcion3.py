# -*- coding: utf-8 -*-
#harvest theses from Concepcion U.
#FS: 2020-11-17
#FS: 2023-03-27

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Concepcion U.'
jnlfilename = 'THESES-CONCEPCION-%s' % (ejlmod3.stampoftoday())
hdr = {'User-Agent' : 'Magic Browser'}

recs = []
rpp = 10 
skipalreadyharvested = True

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

for dep in ['120', '117', '124']:
    tocurl = 'http://repositorio.udec.cl/jspui/handle/11594/' + dep + '/browse?type=dateissued&sort_by=2&order=DESC&rpp=' + str(rpp) 
    ejlmod3.printprogress('=', [[dep], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    for td in tocpage.body.find_all('td', attrs = {'headers' : 't1'}):
        rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'supervisor' : []}
        for a in td.find_all('a'):
            if re.search('handle\/11594', a['href']):
                rec['link'] = 'http://repositorio.udec.cl' + a['href'] #+ '?show=full'
                rec['doi'] = '20.2000/Concepcion/' + re.sub('.*handle\/', '', a['href'])
                if not skipalreadyharvested or not rec['doi'] in  alreadyharvested:
                    recs.append(rec)

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
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'DC.contributor', 'DC.title',
                                        'DCTERMS.issued', 'DCTERMS.abstract',
                                        'citation_pdf_url'])
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
