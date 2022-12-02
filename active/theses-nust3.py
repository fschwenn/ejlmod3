# -*- coding: utf-8 -*-
#harvest theses from Norwegian U. Sci. Tech.
#FS: 2020-04-03
#FS: 2022-11-25

import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time


publisher = 'Norwegian U. Sci. Tech.'
rpp = 20

hdr = {'User-Agent' : 'Magic Browser'}
recs = []
jnlfilename = 'THESES-NUST-%s' % (ejlmod3.stampoftoday())
for dep in ['2425196', '227485', '227491', '227496']:
    tocurl = 'https://ntnuopen.ntnu.no/ntnu-xmlui/handle/11250/' + dep + '/browse?resetOffset=true&sort_by=2&order=DESC&rpp=%i&type=type&value=Doctoral+thesis' % (rpp)
    ejlmod3.printprogress('=', [[dep], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    time.sleep(2)
    recs += ejlmod3.getdspacerecs(tocpage, 'https://ntnuopen.ntnu.no')

j = 0
for rec in recs:
    j += 1
    ejlmod3.printprogress('-', [[j, len(recs)], [rec['link']]])
    req = urllib.request.Request(rec['link'])
    artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    time.sleep(5)
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'DCTERMS.issued', 'DC.subject',
                                        'citation_title', 'citation_pdf_url', 'citation_isbn'])
    rec['autaff'][-1].append(publisher)
    #abstract
    for meta in artpage.find_all('meta', attrs = {'name' : 'DCTERMS.abstract'}):
        if not 'abs' in list(rec.keys()):
            rec['abs'] = meta['content']
    ejlmod3.printrecsummary(rec)
    time.sleep(3)
ejlmod3.writenewXML(recs, publisher, jnlfilename)

