# -*- coding: utf-8 -*-
#harvest theses from KwaZulu Natal U.
#FS: 2022-04-20
#FS: 2023-03-27

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

rpp = 10
years = 2
skipalreadyharvested = True

publisher = 'KwaZulu Natal U.'
jnlfilename = 'THESES-KWAZULU-%s' % (ejlmod3.stampoftoday())

recs = []
hdr = {'User-Agent' : 'Magic Browser'}

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

recs = []
for (fc, dep) in [('m', '7094'), ('m', '7120'), ('', '6603'), ('c', '7113')]:
    tocurl = 'https://researchspace.ukzn.ac.za/handle/10413/' + dep + '/browse?order=DESC&rpp=' + str(rpp) + '&sort_by=3&etal=-1&offset=' + str(0 * rpp) + '&type=dateissued'
    print(tocurl)
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    time.sleep(3)
    for rec in ejlmod3.getdspacerecs(tocpage, 'https://researchspace.ukzn.ac.za', alreadyharvested=alreadyharvested):
        if 'year' in rec and int(rec['year']) <= ejlmod3.year(backwards=years):
            keepit = False            
        else:
            if fc:
                rec['fc'] = fc
            recs.append(rec)
    print('  %4i records so far' % (len(recs)))

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['link']]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(4)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['DC.title', 'DCTERMS.alternative', 'DC.subject', 'DCTERMS.abstract',
                                        'DCTERMS.issued', 'citation_pdf_url', 'citation_doi', 'DC.rights',
                                        'DC.creator', 'DC.contributor'])
    rec['autaff'][-1].append(publisher)
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
