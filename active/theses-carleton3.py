# -*- coding: utf-8 -*-
#harvest theses from Carleton U. (main)
#FS: 2019-12-12
#FS: 2023-04-07

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Carleton U. (main)'
jnlfilename = 'THESES-CARLETON-%s' % (ejlmod3.stampoftoday())
skipalreadyharvested = True

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
for discipline in ['Physics', 'Mathematics', 'FLAG']:
    for year in [str(ejlmod3.year()), str(ejlmod3.year(backwards=1))]:
        tocurl = 'https://curve.carleton.ca/167299e9-53e6-48d7-a28d-8af2f87719ec?f%5B0%5D=thesis_degree_level%3ADoctoral&f%5B1%5D=dcterms_date%3A' + year + '&f%5B2%5D=thesis_degree_discipline%3A' + discipline
        ejlmod3.printprogress('=', [[discipline], [year], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features='lxml')
        divs = tocpage.body.find_all('div', attrs = {'class' : 'views-row'})
        for div in divs:
            rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK'}
            if discipline == 'Mathematics':
                rec['fc'] = 'm'
            for div2 in div.find_all('div', attrs = {'class' : 'views-field-title'}):
                for a in div2.find_all('a'):
                    rec['link'] = 'https://curve.carleton.ca' + a['href']
                    prerecs.append(rec)
        print('  %4i records so far' % (len(prerecs)))
        time.sleep(5)

i = 0
recs = []
for rec in prerecs:
        rec['doi'] = '20.2000/' + re.sub('\W', '', rec['link'][6:])
        i += 1
        ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
        try:
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features='lxml')
            time.sleep(3)
        except:
            try:
                print("retry %s in 180 seconds" % (rec['link']))
                time.sleep(180)
                artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features='lxml')
            except:
                print("no access to %s" % (rec['link']))
                continue    
        ejlmod3.metatagcheck(rec, artpage, ['dcterms.creator', 'citation_title', 'dcterms.date',
                                            'abstract', 'citation_pdf_url'])
        rec['autaff'][-1].append(publisher)
        #license
        ejlmod3.globallicensesearch(rec, artpage)
        #doi
        for a in artpage.find_all('a'):
            if a.has_attr('href') and re.search('doi.org\/10\.22215', a['href']):
                rec['doi'] = re.sub('.*doi.org\/', '', a['href'])
        if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
            ejlmod3.printrecsummary(rec)
            recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
