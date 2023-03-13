# -*- coding: utf-8 -*-
#harvest theses from Rio Grande do Sul U.
#FS: 2020-10-08
#FS: 2023-03-12

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time


jnlfilename = 'THESES-RioGrandeDoSul-%s' % (ejlmod3.stampoftoday())
publisher = 'Rio Grande do Sul U.'

hdr = {'User-Agent' : 'Magic Browser'}

rpp = 50
pages = 3-1
years = 2
boringdegrees = ['mestrado']
skipalreadyharvested = True


if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

prerecs = []
for (depnr, department) in [('46', 'Physics'), ('48', 'Mathematics'), ('49', 'Applied Mathematics'), ('43', 'Computation')]:
    for page in range(pages):
        tocurl = 'https://lume.ufrgs.br/handle/10183/' + depnr +'/discover?rpp=' + str(rpp) + '&etal=0&group_by=none&page=' + str(page+1) + '&sort_by=dc.date.issued_dt&order=desc'
        ejlmod3.printprogress("=", [[department], [page+1, pages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        for rec in ejlmod3.getdspacerecs(tocpage, 'https://lume.ufrgs.br'):
            if 'year' in rec and int(rec['year']) <= ejlmod3.year(backwards=2):
                print('  %s too old' % (rec['year']))
            elif skipalreadyharvested and rec['hdl'] in alreadyharvested:
                print('  %s already in backup' % (rec['hdl']))
            else:
                if depnr in ['46', '48']:
                    rec['fc'] = 'm'
                elif depnr == '43':
                    rec['fc'] = 'c'
                prerecs.append(rec)
        print('  %4i records so far' % (len(prerecs)))
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
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'citation_title', 'DCTERMS.issued',
                                        'DCTERMS.abstract', 'citation_pdf_url'])
    rec['autaff'][-1].append(publisher)
    #keywords
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'citation_keywords'}):
        for keyw in re.split('[,;] ', meta['content']):
            if not re.search('^info.eu.repo', keyw):
                rec['keyw'].append(keyw)
    for tr in artpage.body.find_all('tr', attrs = {'class' : 'ds-table-row'}):
        for td in tr.find_all('td', attrs = {'class' : 'label-cell'}):
            tdt = td.text.strip()
            td.decompose()
        for td in tr.find_all('td'):
            if td.text.strip() == 'pt_BR':
                continue
            #supervisor
            if tdt == 'dc.contributor.advisor':
                rec['supervisor'] = [[ re.sub(' \(.*', '', td.text.strip()) ]]
            #degree
            elif tdt == 'dc.degree.level':
                degree = td.text.strip()
                if degree in boringdegrees:
                    print('  skip "%s"' % (degree))
                    keepit = False
                else:
                    rec['note'].append(degree)
            #language
            elif tdt == 'dc.language.iso':
                if td.text.strip() == 'por':
                    rec['language'] = 'portuguese'
    ejlmod3.globallicensesearch(rec, artpage)
    if keepit:
        recs.append(rec)
        ejlmod3.printrecsummary(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['hdl'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
