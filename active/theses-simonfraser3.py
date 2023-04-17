# -*- coding: utf-8 -*-
#harvest Simon Fraser U., Burnaby (main)
#FS: 2020-02-05
#FS: 2022-04-26

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Simon Fraser U., Burnaby (main)'
hdr = {'User-Agent' : 'Magic Browser'}

recs = []
prerecs = []
jnlfilename = 'THESES-SIMONFRASER-%s' % (ejlmod3.stampoftoday())
pages = 1
skipalreadyharvested = True

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

for (dep, fc, aff) in [('30012', 'c', publisher), ('30034', 'm', publisher), ('30038', '', 'Simon Fraser U.')]:
    for page in range(pages):
        tocurl = 'https://summit.sfu.ca/collection/' + dep + '?sort_by=field_edtf_date_created_value&sort_order=DESC&page=' + str(page)
        ejlmod3.printprogress('=', [[dep], [page+1, pages], [tocurl]])
        tocpage = BeautifulSoup(urllib.request.urlopen(tocurl), features="lxml")
        for div in tocpage.body.find_all('div', attrs = {'class' : 'views-field-title'}):
            for a in div.find_all('a'):
                rec = {'tc' : 'T', 'jnl' : 'BOOK', 'affiliation' : aff, 'supervisor' : []}
                rec['tit'] = a.text.strip()
                rec['link'] = 'https://summit.sfu.ca' + a['href']
                rec['doi'] = '20.2000/SimonFraser' + a['href']
                if fc: rec['fc'] = fc
                if ejlmod3.checkinterestingDOI(rec['doi']):
                    if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
                        prerecs.append(rec)

i = 0
for rec in prerecs:
    i += 1
    keepit = True
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(3)
    except:
        try:
            print('retry %s in 180 seconds' % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        except:
            print('no access to %s' % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['dcterms.abstract', 'dcterms.creator', 'dcterms.title', 'citation_publication_date', 'citation_pdf_url', 'dc:subject', 'dc:rights'])
    rec['autaff'][-1].append(rec['affiliation'])
    #supervisor
    for div in artpage.body.find_all('div', attrs = {'class' : 'field--name-field-sfu-thesis-advisor'}):
        for a in div.find_all('a'):
            rec['supervisor'].append([a.text])
    #degree
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'degree|name'}):
        degree = meta['content']
        if re.search('M.Sc.', degree):
            keepit = False
        elif not re.search('Ph.D.', degree):
            rec['note'] = [ degree ]
    if keepit:
        recs.append(rec)        
        ejlmod3.printrecsummary(rec)
    else:  
        ejlmod3.adduninterestingDOI(rec['doi'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
