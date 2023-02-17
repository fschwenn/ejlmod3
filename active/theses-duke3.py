# -*- coding: utf-8 -*-
#harvest theses from Duke U.
#FS: 2019-12-13
#FS: 2023-02-17

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Duke U. (main)'
jnlfilename = 'THESES-DUKE_U-%s' % (ejlmod3.stampoftoday())

rpp = 20
skipalreadyharvested = True

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

recs = []
hdr = {'User-Agent' : 'Magic Browser'}
for department in ['Physics', 'Mathematics']:
    tocurl = 'https://dukespace.lib.duke.edu/dspace/handle/10161/4/browse?type=department&value=' + department + '&rpp=' + str(rpp) + '&sort_by=2&order=DESC'
    ejlmod3.printprogress('=', [[tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    for rec in ejlmod3.getdspacerecs(tocpage, 'https://dukespace.lib.duke.edu'):
        if skipalreadyharvested and rec['hdl'] in alreadyharvested:
            pass
        else:
            if department == 'Mathematics':
                rec['fc'] = 'm'
            recs.append(rec)
    time.sleep(30)

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
    ejlmod3.metatagcheck(rec, artpage, ['DC.title', 'DCTERMS.issued', 'DC.subject', 'DCTERMS.abstract', 'citation_pdf_url',
                                        'DC.creator', 'DC.contributor'])
    rec['autaff'][-1].append(publisher)
    #license
    ejlmod3.globallicensesearch(rec, artpage)
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
