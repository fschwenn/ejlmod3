# -*- coding: utf-8 -*-
#harvest theses from Canterbury U.
#FS: 2020-09-11
#FS: 2023-04-26

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Canterbury U.'
jnlfilename = 'THESES-CANTERBURY-%s' % (ejlmod3.stampoftoday())

rpp = 20
pages = 1
skipalreadyharvested = True

hdr = {'User-Agent' : 'Magic Browser'}

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []
    
prerecs = []
for page in range(pages):
    tocurl = 'https://ir.canterbury.ac.nz/handle/10092/841/discover?filtertype_1=discipline&filter_relational_operator_1=contains&filter_1=physics&submit_apply_filter=&rpp=' + str(rpp) + '&sort_by=dc.date.issued_dt&order=desc&page=' + str(page+1)
    ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    time.sleep(5)
    prerecs += ejlmod3.getdspacerecs(tocpage, 'https://ir.canterbury.ac.nz', alreadyharvested=alreadyharvested)
    print('  %4i records so far' % (len(prerecs)))

i = 0
recs = []
for rec in prerecs:
    i += 1
    keepit = True
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
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
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'DC.title', 'DCTERMS.issued',
                                        'DC.subject', 'DC.identifier', 'DC.rights',
                                        'citation_pdf_url', 'DCTERMS.abstract'])
    rec['autaff'][-1].append(publisher)
    for div in artpage.body.find_all('div', attrs = {'class' : 'simple-item-view-other'}):
        for h5 in div.find_all('h5'):
            #Degree
            if re.search('Degree', h5.text):
                for span in div.find_all('span'):
                    rec['degree'] = span.text.strip()
                    if re.search('Master', rec['degree']):
                        keepit = False
                        print('   skip "%s"' % (rec['degree']))
    if keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['hdl'])
        
ejlmod3.writenewXML(recs, publisher, jnlfilename)
