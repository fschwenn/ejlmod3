# -*- coding: utf-8 -*-
#harvest theses from Pakistan Research Repository
#FS: 2020-01-07
#FS: 2023-03-25

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import json
import ssl

publisher = 'Pakistan Research Repository'
jnlfilename = 'THESES-PakistanResearchRepository-%s' % (ejlmod3.stampoftoday())
    
rpp = 40
numofpages = 1
skipalreadyharvested = True

hdr = {'User-Agent' : 'Magic Browser'}
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
recs = []
for subject in ['Physics', 'Mathematics', 'Computer+%26+IT']:
    for i in range(numofpages):
        tocurl = 'http://prr.hec.gov.pk/jspui/handle/123456789/1/simple-search?query=&filter_field_1=subject&filter_type_1=equals&filter_value_1=' + subject + '&sort_by=dc.date.issued_dt&order=desc&rpp=' + str(rpp) + '&etal=0&start=' + str(i*rpp)
        ejlmod3.printprogress('=', [[subject], [i+1, numofpages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features='lxml')
        for tr in tocpage.body.find_all('tr'):
            for td in tr.find_all('td', attrs = {'headers' : 't2'}):
                for a in td.find_all('a'):
                    rec = {'tc' : 'T', 'jnl' : 'BOOK'}
                    rec['link'] = 'http://prr.hec.gov.pk' + a['href']
                    rec['doi'] = '20.2000/PRR/' + re.sub('.*handle\/', '', a['href'])
                    if subject == 'Mathematics':
                        rec['fc'] = 'm'
                    elif subject == 'Computer+%26+IT':
                        rec['fc'] = 'c'
                    if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
                        recs.append(rec)
        print('  %4i records so far' % (len(recs)))
        time.sleep(30)

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['link']]])
    try:
        req = urllib.request.Request(rec['link'], headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features='lxml')
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            req = urllib.request.Request(rec['link'], headers=hdr)
            artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features='lxml')
        except:
            print("no access to %s" % (rec['link']))
            continue    
    ejlmod3.metatagcheck(rec, artpage, ['citation_authors', 'DC.title', 'DCTERMS.issued',
                                        'DCTERMS.abstract', 'citation_pdf_url'])
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'citation_dissertation_institution'}):
        aff = meta['content'] + ', Pakistan'
    if 'autaff' in list(rec.keys()):
        rec['autaff'][-1].append(aff)
    else:
        rec['autaff'] = [['unknown author', aff]]
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
