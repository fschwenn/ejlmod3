# -*- coding: utf-8 -*-
#harvest Uni Bonn Theses
#FS: 2020-05-11
#FS: 2023-01-18

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'U. Bonn (main)'
hdr = {'User-Agent' : 'Magic Browser'}

rpp = 50
skipalreadyharvested = True
jnlfilename = 'THESES-BONN-%s' % (ejlmod3.stampoftoday())
pages = 3

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

hdls = []
recs = []
for (ddc, fc) in [('500', ''), ('510', 'm'), ('520', 'a'), ('530', ''), ('004', 'c')]:
    for page in range(pages):
        tocurl = 'https://bonndoc.ulb.uni-bonn.de/xmlui/handle/20.500.11811/1627/discover?filtertype_0=ddc&filter_relational_operator_0=equals&filter_0=ddc%3A' + ddc + '&sort_by=dc.date.issued_dt&order=desc&rpp=' + str(rpp) + '&page=' + str(page+1)  #&filtertype=dateIssued&filter_relational_operator=equals&filter=[' + str(year) + '+TO+' + str(year) + ']
        ejlmod3.printprogress("=", [[ddc, fc], [page+1, pages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req),features="lxml" )
        for div in tocpage.body.find_all('div', attrs = {'class' : 'artifact-description'}):
            rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK'}
            for a in div.find_all('a'):
                for h4 in a.find_all('h4'):
                    rec['artlink'] = 'https://bonndoc.ulb.uni-bonn.de' + a['href']# + '?show=full'
                    rec['hdl'] = re.sub('.*handle\/', '', a['href'])
                    if not rec['hdl'] in hdls and not rec['hdl'] in alreadyharvested:
                        if fc: rec['fc'] = fc
                        recs.append(rec)
                        hdls.append(rec['hdl'])
        time.sleep(3)

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['artlink']]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        time.sleep(10)
    except:
        try:
            print('retry %s in 180 seconds' % (rec['artlink']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        except:
            print('no access to %s' % (rec['artlink']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'DC.contributor', 'DC.title',
                                        'DC.Subject', 'DCTERMS.abstract', 'DC.Language',
                                        'DC.Identifier', 'DCTERMS.issued', 'DC.Rights',
                                        'citation_pdf_url'])
    rec['autaff'][-1].append(publisher)
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
