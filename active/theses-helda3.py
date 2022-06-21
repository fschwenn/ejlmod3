# -*- coding: utf-8 -*-
#harvest theses from HELDA
#FS: 2019-10-25

import urllib.request, urllib.error, urllib.parse
import urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time


publisher = 'Helsinki U.'
jnlfilename = 'THESES-HELSINKI-%s' % (ejlmod3.stampoftoday())
rpp = 50
numofpages = 1

hdr = {'User-Agent' : 'Magic Browser'}
for i in range(numofpages):
    recs = []
    tocurl = 'https://helda.helsinki.fi/handle/10138/18070/browse?rpp=%i&sort_by=2&type=dateissued&offset=%i&etal=-1&order=DESC' % (rpp, i*rpp)
    ejlmod3.printprogress('=', [[i+1, numofpages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    time.sleep(2)
    for div in tocpage.body.find_all('div', attrs = {'class' : 'artifact-title'}):
        for a in div.find_all('a'):
            rec = {'tc' : 'T', 'jnl' : 'BOOK', 'autaff' : []}
            rec['link'] = 'https://helda.helsinki.fi' + a['href']
            rec['hdl'] = re.sub('\/handle\/', '', a['href'])
            rec['tit'] = a.text.strip()
            recs.append(rec)
            
j = 0
for rec in recs:
    j += 1
    ejlmod3.printprogress('-', [[j, len(recs)], [rec['link']]])
    req = urllib.request.Request(rec['link'])
    artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    time.sleep(5)
    ejlmod3.metatagcheck(rec, artpage, ['citation_date', 'citation_author', 'DC.rights',
                                        'citation_language', 'citation_pdf_url',
                                        'DC.identifier'])
    rec['autaff'][-1].append(publisher)                        
    #abstract
    for meta in artpage.find_all('meta', attrs = {'name' : 'DCTERMS.abstract'}):
        if meta.has_attr('xml:lang') and meta['xml:lang'] in ['eng', 'en_US']:
            rec['abs'] = meta['content']                                        
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)


