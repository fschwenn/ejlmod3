# -*- coding: utf-8 -*-
#program to harvest J.Phys.Theor.Appl.
# FS 2023-08-25

import sys
import os
import ejlmod3
import re
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import time

regexpref = re.compile('[\n\r\t]')

publisher = 'U. Sebelas Maret, Surakarta'

issueid = sys.argv[1]
urltrunc = 'https://jurnal.uns.ac.id/jphystheor-appl/issue/view/%s' % (issueid)
    
print(urltrunc)
try:
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(urltrunc), features="lxml")
    time.sleep(3)
except:
    print("retry %s in 180 seconds" % (urltrunc))
    time.sleep(180)
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(urltrunc), features="lxml")

#print(tocpage.text)
    
recs = []
for div in tocpage.body.find_all('div', attrs = {'class' : 'tocTitle'}):
    for a in div.find_all('a'):
        rec = {'tc' : 'P', 'jnl' : 'J.Phys.Theor.Appl.', 'note' : []}
        rec['artlink'] = a['href']
        recs.append(rec)

i = 0
for rec in recs:
    i += 1
    autaff = False
    time.sleep(3)
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['artlink']]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
    except:
        time.sleep(30)
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['citation_date', 'citation_title', 'citation_firstpage',
                                        'citation_keywords', 'citation_doi', 'citation_author',
                                        'citation_author_institution', 'citation_issue',
                                        'citation_volume', 'DC.Description', 'citation_pdf_url',
                                        'citation_reference', 'citation_language', 'DC.Rights',
                                        'citation_lastpage'])
    ejlmod3.printrecsummary(rec)

jnlfilename = 'jphysta%s.%s_%s' % (rec['vol'], rec['issue'], issueid)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
