# -*- coding: utf-8 -*-
#harvest theses from Wigner RCP, Budapest
#FS: 2022-05-02
#FS: 2023-02-24

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

jnlfilename = 'THESES-WignerRCP-%s' % (ejlmod3.stampoftoday())

publisher = 'Wigner RCP, Budapest'

hdr = {'User-Agent' : 'Magic Browser'}

rpp = 20
pages = 2
boringdegrees = []
years = 2
skipalreadyharvested = True

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

prerecs = []
(old, inbackup) = (0, 0)
for (depnr, fc) in [('73', ''), ('77', 'm'), ('88', ''), ('75', 'c')]:
    for page in range(pages):
        tocurl = 'https://repozitorium.omikk.bme.hu/handle/10890/' + depnr +'/discover?rpp=' + str(rpp) + '&page=' + str(page+1) + '&sort_by=dc.date.issued_dt&order=desc'
        ejlmod3.printprogress("=", [[depnr+fc], [page+1, pages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        for rec in ejlmod3.getdspacerecs(tocpage, 'https://repozitorium.omikk.bme.hu'):
            if 'year' in rec and int(rec['year']) <= ejlmod3.year(backwards=years):
                #print('  skip',  rec['year'])
                old += 1
            elif skipalreadyharvested and rec['hdl'] in alreadyharvested:
                #print('   %s already in backup' % (rec['hdl']))
                inbackup += 1
            else:
                if fc:
                    rec['fc'] = fc
                prerecs.append(rec)        
        print('  %4i records so far (%i too old, %i already in backup)' % (len(prerecs), old, inbackup))
        time.sleep(2)

i = 0
recs = []
for rec in prerecs:
    keepit = True
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link'] + '?show=full'), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link'] + '?show=full'), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue    
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'citation_title', 'DCTERMS.issued', 'DCTERMS.abstract',
                                        'citation_pdf_url', ])
    #keywords
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'citation_keywords'}):
        for keyw in re.split('[,;] ', meta['content']):
            if not re.search('^info.eu.repo', keyw):
                rec['keyw'].append(keyw)
    for tr in artpage.body.find_all('tr', attrs = {'class' : 'ds-table-row'}):
        for label in tr.find_all('label'):
            tdt = label['title']
        tds = tr.find_all('td')
        if len(tds) == 3:
            #supervisor
            if tdt == 'dc.contributor.advisor':
                rec['supervisor'] = [[ re.sub(' \(.*', '', tds[1].text.strip()) ]]
            #degree
            elif tdt == 'dc.type':
                degree = tds[1].text.strip()
                if degree in boringdegrees:
                    print('  skip "%s"' % (degree))
                    keepit = False
                else:
                    rec['note'].append(degree)
            #language
            elif tdt == 'dc.language':
                if tds[1].text.strip() == 'hu':
                    rec['language'] = 'hungarian'
            #translated title
            elif tdt == 'dc.title.alternative':
                rec['transtit'] = tds[1].text.strip()
    ejlmod3.globallicensesearch(rec, artpage)
    if keepit:
        recs.append(rec)
        ejlmod3.printrecsummary(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['hdl'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
