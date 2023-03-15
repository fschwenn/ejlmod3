# -*- coding: utf-8 -*-
#harvest theses from Iowa State U. (main)
#FS: 2020-04-08
#FS: 2023-03-15

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import json

publisher = 'Iowa State U. (main)'
jnlfilename = 'THESES-IOWASTATE-%s' % (ejlmod3.stampoftoday())

hdr = {'User-Agent' : 'Magic Browser'}

rpp = 20
pages = 1
skipalreadyharvested = True
recs = []

boringdegrees = ['Master of Science']

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

for (fc, dep) in [('', 'Physics%20and%20Astronomy'), ('m', 'Mathematics'), ('c', 'Computer%20Science')]:
    for page in range(pages):
        keepit = True
        tocurl = 'https://dr.lib.iastate.edu/collections/0830d32e-14e1-4a4f-bb8f-271a75ed35af?scope=0830d32e-14e1-4a4f-bb8f-271a75ed35af&view=listElement&f.department=' + dep + ',equals&spc.sf=dc.date.issued&spc.sd=DESC&spc.rpp=' + str(rpp) + '&spc.page=' + str(page+1)
        ejlmod3.printprogress('=', [[dep], [page+1, pages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        for rec in ejlmod3.ngrx(tocpage, 'https://dr.lib.iastate.edu',
                                ['thesis.degree.name', 'dc.date.issued', 'dc.title',
                                 'dc.contributor.advisor', 'dc.date.embargo', 'dc.identifier.doi',
                                 'dc.subject.keywords', 'dc.description.abstract', 'dc.contributor.author'], boring=boringdegrees):
            rec['autaff'][-1].append(publisher)
            if fc: rec['fc'] = fc
            if 'dc.type.genre' in rec:
                rec['note'].append(rec['dc.type.genre'])
            if 'dc.date.embargo' in rec:
                rec['embargo'] = (rec['dc.date.embargo'] > ejlmod3.stampoftoday())
            else:
                rec['embargo'] = False
         
            if keepit and 'autaff' in list(rec.keys()):
                if skipalreadyharvested and 'hdl' in rec and rec['hdl'] in alreadyharvested:
                    pass
                else:
                    recs.append(rec)
                #ejlmod3.printrecsummary(rec)
        print('  %4i records so far' % (len(recs)))
        time.sleep(5)

print('get fulltext links')

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['link']]])
    if not rec['embargo']:
        req = urllib.request.Request(rec['link'], headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        for meta in artpage.head.find_all('meta', attrs = {'property' : 'citation_pdf_url'}):
            rec['hidden'] = 'https://dr.lib.iastate.edu' + meta['content']
        time.sleep(5)
    ejlmod3.printrecsummary(rec)


ejlmod3.writenewXML(recs, publisher, jnlfilename)
