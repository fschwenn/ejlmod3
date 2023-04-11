# -*- coding: utf-8 -*-
#harvest theses from Salerno U.
#FS: 2020-08-25
#FS: 2023-04-04

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

jnlfilename = 'THESES-SALERNO-%s' % (ejlmod3.stampoftoday())

publisher = 'Salerno U.'

hdr = {'User-Agent' : 'Magic Browser'}

pages = 1
rpp = 50
years = 2
skipalreadyharvested = True

unintersting = [re.compile('Chimica'), re.compile('Biologia'), re.compile('Politiche'),
                re.compile('Farmacia')]
if skipalreadyharvested:    
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
recs = []
for page in range(pages):
    tocurl = 'http://elea.unisa.it:8080/xmlui/handle/10556/60/discover?rpp=' + str(rpp) + '&etal=0&group_by=none&page=' + str(page+1) + '&sort_by=dc.date.issued_dt&order=desc'
    ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features='lxml')
    for rec in ejlmod3.getdspacerecs(tocpage, 'http://elea.unisa.it:8080', alreadyharvested=alreadyharvested):
        keepit = True
        #check department
        if 'degrees' in rec:
            for degree in rec['degrees']:
                for unint in unintersting:
                    if unint.search(degree):
                        print('    skip',  degree)
                        keepit = False
                        break
        #check year
        if keepit:
            if 'year' in rec and int(rec['year']) <= ejlmod3.year(backwards=years):
                keepit = False
                print('    skip',  rec['year'])
        if keepit:
            recs.append(rec)
    print('  check %i of %i' % (len(recs), (page+1)*rpp))
    time.sleep(2)


i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['link']]])
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
    ejlmod3.metatagcheck(rec, artpage, ['DC.title', 'DCTERMS.issued', 'citation_isbn',
                                        'DC.identifier', 'citation_pdf_url', 'DC.language'])
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #author
            if meta['name'] == 'DC.creator':
                author = re.sub(' *\[.*', '', meta['content'])
                rec['autaff'] = [[ author ]]
                rec['autaff'][-1].append(publisher)
            #author
            #if meta['name'] == 'DC.contributor':
            #    rec['supervisor'].append([ meta['content'] ])
            #abstract
            elif meta['name'] == 'DCTERMS.abstract':
                if re.search(' the ',  meta['content']):
                    rec['abs'] = re.sub('ABSTRACT: ', '', meta['content'])
                else:
                    rec['absit'] = re.sub('RESUMEN: ', '', meta['content'])
            #keywords
            elif meta['name'] == 'citation_keywords':
                for keyw in re.split(' *; *', meta['content']):
                    if keyw != 'Doctoral Thesis':
                        rec['keyw'].append(keyw)
    if not 'abs' in list(rec.keys()):
        if 'absit' in list(rec.keys()):
            rec['abs'] = rec['absit']
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
