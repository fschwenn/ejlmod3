# -*- coding: utf-8 -*-
#program to harvest J.Kufa Phys.
# FS 2023-08-25

import sys
import os
import ejlmod3
import re
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import time

regexpref = re.compile('[\n\r\t]')

publisher = 'University of Kufa, Iraq'

issueid = sys.argv[1]
urltrunc = 'https://journal.uokufa.edu.iq/index.php/jkp/issue/view/%s' % (issueid)
    
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
for div in tocpage.body.find_all('h3', attrs = {'class' : 'title'}):
    for a in div.find_all('a'):
        rec = {'tc' : 'P', 'jnl' : 'J.Kufa Phys.', 'note' : []}
        rec['artlink'] = a['href']
        recs.append(rec)

i = 0
for rec in recs:
    i += 1
    autaff = False
    time.sleep(3)
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['artlink']]])
    artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['citation_date', 'citation_title', 'citation_firstpage',
                                        'citation_keywords', 'citation_doi', 'citation_author',
                                        'citation_author_institution', 'citation_issue',
                                        'citation_volume', 'DC.Description', 'citation_pdf_url',
                                        'citation_reference', 'citation_language', 'DC.Rights',
                                        'citation_lastpage'])
    ejlmod3.printrecsummary(rec)

jnlfilename = 'kufa%s.%s_%s' % (rec['vol'], rec['issue'], issueid)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
