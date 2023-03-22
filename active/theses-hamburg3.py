# -*- coding: utf-8 -*-
#harvest theses from Hamburg
#FS: 2020-01-27
#FS: 2023-03-19

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'U. Hamburg (main)'
jnlfilename = 'THESES-HAMBURG-%s' % (ejlmod3.stampoftoday())

pages = 3
skipalreadyharvested = True
rpp = 50

hdr = {'User-Agent' : 'Magic Browser'}

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

prerecs = []
recs = []
for fac in ['510+Mathematik', '530+Physik', '004+Informatik']:
    ejlmod3.printprogress("=", [[fac]])
    for page in range(pages):
        time.sleep(1)
        tocurl = 'https://ediss.sub.uni-hamburg.de/simple-search?query=&location=&filter_field_1=subject&filter_type_1=equals&filter_value_1=' + fac + '&crisID=&relationName=&sort_by=bi_sort_2_sort&order=desc&rpp=' + str(rpp) + '&etal=0&start=' + str(page*rpp)
        ejlmod3.printprogress("=", [[fac], [page+1, pages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features='lxml')
        for tr in tocpage.body.find_all('tr'):
            for td in tr.find_all('td', attrs = {'headers' : 't1'}):
                rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'supervisor' : []}
                if fac == '510+Mathematik':
                    rec['fc'] = 'm'
                elif fac == '004+Informatik':
                    rec['fc'] = 'c'
                for a in td.find_all('a'):
                    rec['artlink'] = 'https://ediss.sub.uni-hamburg.de' + a['href']
                    prerecs.append(rec)

for (i, rec) in enumerate(prerecs):
    ejlmod3.printprogress("-", [[i+1, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features='lxml')
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['artlink']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features='lxml')
        except:
            print("no access to %s" % (rec['artlink']))
            continue    
    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'DCTERMS.abstract', 'citation_title',
                                        'DCTERMS.issued', 'DC.subject', 'language',
                                        'DC.Identifier', 'DC.identifier', 'citation_pdf_url',
                                        'DC.contributor'])
    rec['autaff'][-1].append(publisher)
#        for meta in artpage.head.find_all('meta'):
#            if meta.has_attr('name'):#
                #supervisor
#                elif meta['name'] == 'DC.contributor':
#                    rec['supervisor'].append([re.sub(' *\(.*', '', meta['content'])])
    if skipalreadyharvested and 'urn' in rec and rec['urn'] in alreadyharvested:
        print('    already in backup')
    else:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
