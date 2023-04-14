# -*- coding: utf-8 -*-
#program to harvest Bulgarian Academy of Science
# FS 2022-04-14
# FS 2023-04-14

import sys
import os
import ejlmod3
import re
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import time




regexpref = re.compile('[\n\r\t]')

typecode = 'P'

issueid = sys.argv[1]

publisher = 'Bulgarian Academy of Sciences'
urltrunk = 'http://www.proceedings.bas.bg/index.php/cr/issue/view/%s' % (issueid)
    
print(urltrunk)
try:
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(urltrunk), features="lxml")
    time.sleep(3)
except:
    print("retry %s in 180 seconds" % (urltrunk))
    time.sleep(180)
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(urltrunk), features="lxml")

recs = []
for div in tocpage.body.find_all('div', attrs = {'class' : 'section'}):
    for h2 in div.find_all('h2'):
        note = regexpref.sub('', h2.text).strip()
        print(' - %s - ' % (note))
    for h3 in div.find_all('h3'):
        rec = {'jnl' : 'Compt.Rend.Acad.Bulg.Sci.', 'tc' : 'P', 'note' : [note], 'keyw' : [],
               'autaff' : []}
        if note in ['Mathematics']:
            rec['fc'] = 'm'
        elif note in ['Chemistry', 'Biology', 'Medicine', 'Geophysics', 'Agricultural Sciences'
                      'Engineering Sciences', 'Geology']:
            rec['fc'] = 'o'
        elif note in ['Space Sciences']:
            rec['fc'] = 'a'
        for a in h3.find_all('a'):
            rec['artlink'] = a['href']
            recs.append(rec)

i = 0
for rec in recs:
    i += 1
    autaff = False
    time.sleep(3)
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['artlink']]])
    artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']))
    ejlmod3.metatagcheck(rec, artpage, ['citation_date', 'citation_title', 'citation_firstpage',
                                        'citation_keywords', 'citation_doi', 'citation_author',
                                        'citation_author_institution', 'citation_issue',
                                        'citation_volume', 'DC.Description', 'citation_pdf_url',
                                        'citation_reference'])
    ejlmod3.printrecsummary(rec)

jnlfilename = 'crabs%s.%s_%s' % (rec['vol'], rec['issue'], issueid)
ejlmod3.writenewXML(recs, publisher, jnlfilename)
