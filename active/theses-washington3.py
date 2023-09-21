# -*- coding: utf-8 -*-
#harvest theses Washington U.
#FS: 2020-09-01
#FS: 2022-09-29

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import ssl

publisher = 'U. Washington, Seattle (main)'
jnlfilename = 'THESES-WashingtonUSeattle-%s' % (ejlmod3.stampoftoday())

rpp = 20
pages = 1
skipalreadyharvested = True

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

#bad certificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
hdr = {'User-Agent' : 'Magic Browser'}
recs = []
for (dep, fc) in [('4891', 'm'), ('4909', 'c'), ('4939', 'm'), ('4892', 'a')]:#('4956', '')]:
    for page in range(pages):
        tocurl = 'https://digital.lib.washington.edu/researchworks/handle/1773/' + dep + '/browse?order=DESC&rpp=' + str(rpp) + '&sort_by=3&etal=-1&offset=' + str(page*rpp) + '&type=dateissued'
        ejlmod3.printprogress('=', [[dep], [page+1, pages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        recs += ejlmod3.getdspacerecs(tocpage, 'https://digital.lib.washington.edu', alreadyharvested=alreadyharvested)
        print('  %4i records do far' % (len(recs)))
        time.sleep(10)

for (i, rec) in enumerate(recs):
    ejlmod3.printprogress('-', [[i+1, len(recs)], [rec['link']]])
    try:
        req = urllib.request.Request(rec['link'], headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        time.sleep(3)
    except:
        try:
            print("   retry %s in 15 seconds" % (rec['link']))
            time.sleep(15)
            req = urllib.request.Request(rec['link'], headers=hdr)
            artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        except:
            print("   no access to %s" % (rec['link']))
            continue
    ejlmod3.globallicensesearch(rec, artpage)
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'DC.title', 'DCTERMS.issued',
                                        'DC.subject', 'DCTERMS.abstract', 'citation_pdf_url'])
    if not 'date' in rec:
        for meta in artpage.head.find_all('meta', attrs = {'name' : 'DCTERMS.dateAccepted'}):
            rec['date'] = meta['content']
            rec['note'].append('date from DCTERMS.dateAccepted')
    rec['autaff'][-1].append(publisher)
    ejlmod3.printrecsummary(rec)
    
ejlmod3.writenewXML(recs, publisher, jnlfilename)
