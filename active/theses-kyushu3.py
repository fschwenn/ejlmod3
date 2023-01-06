# -*- coding: utf-8 -*-
#harvest theses from Kyushu U.
#FS: 2022-02-17
#FS: 2022-12-09

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import ssl

publisher = 'Kyushu U., Fukuoka (main)'
pages = 2
rpp = 200
boringdegrees = ['Master Thesis', 'DOCTOR OF PHILOSOPHY (Dental Science)', 'DOCTOR OF PHILOSOPHY (Medical Science)',
                 'DOCTOR OF PHILOSOPHY (Systems Life Sciences)', 'DOCTOR OF PHILOSOPHY IN HEALTH SCIENCES',
                 'DOCTOR OF DESIGN', 'DOCTOR OF LITERATURE', 'DOCTOR OF PHILOSOPHY IN KANSEI SCIENCE',
                 'DOCTOR OF PHILOSOPHY IN NURSING', 'DOCTOR OF PHILOSOPHY (Medicinal Sciences)',
                 'DOCTOR OF AUTOMOTIVE SCIENCE', 'DOCTOR OF LAWS', 'DOCTOR OF PHILOSOPHY (Clinical Pharmacy)',
                 'DOCTOR OF PHILOSOPHY (Education)', 'DOCTOR OF PHILOSOPHY (Pharmaceutical Sciences)',
                 'DOCTOR OF PHILOSOPHY (Psychology)',
                 'DOCTOR OF ECONOMICS', 'DOCTOR OF ENGINEERING', 'DOCTOR OF PHILOSOPHY (Agricultural Science)']
              
jnlfilename = 'THESES-KYUSHU-%s' % (ejlmod3.stampoftoday())

hdr = {'User-Agent' : 'Magic Browser'}
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

prerecs = []
for page in range(pages):
    tocurl = 'https://catalog.lib.kyushu-u.ac.jp/opac_search/?lang=1&amode=9&start=' + str(page*rpp+1) + '&opkey=B167057062892751&cmode=0&place=&list_disp=' + str(rpp) + '&list_sort=6'
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
    for ul in tocpage.body.find_all('ul', attrs = {'class' : 'result-list'}):
        for div in ul.find_all('div', attrs = {'class' : 'row'}):
            rec = {'tc' : 'T', 'jnl' : 'BOOK', 'supervisor' : [], 'note' : [], 'auts' : [], 'aff' : [publisher]}
            for div2 in div.find_all('div', attrs = {'class' : 'result-book-datatypenm'}):
                if not div2.text.strip() in boringdegrees:
                    for a in div.find_all('a'):
                        rec['artlink'] = 'https://catalog.lib.kyushu-u.ac.jp' + a['href']
                        rec['hdl'] = re.sub('.*bibid=(\d+).*', r'2324/\1', a['href'])
                    if ejlmod3.checkinterestingDOI(rec['hdl']):
                        prerecs.append(rec)
    time.sleep(2)
        

i = 0
recs = []
for rec in prerecs:
    keepit = True
    oa = False
    i += 1
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        req = urllib.request.Request(rec['artlink'], headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['artlink']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']))
        except:
            print("no access to %s" % (rec['artlink']))
            continue
    for table in artpage.find_all('table', attrs = {'class' : 'book-detail-table'}):
        for tr in table.find_all('tr'):
            for th in tr.find_all('th'):
                tht = th.text.strip()
            for td in tr.find_all('td'):
                #author
                if tht == 'Creator':
                    for a in td.find_all('a'):
                        if re.search('[A-Z]', a.text):
                            rec['auts'].append(a.text.strip())
                #supervisor
                elif tht == 'Thesis Advisor':
                    for div in td.find_all('div', attrs = {'class' : 'metadata_value'}):
                        rec['supervisor'].append([re.sub('[\n\t\r]', ' ', div.text).strip()])
                #degree
                elif tht == 'Degree':
                    degree = re.sub('[\n\t\r]', ' ', td.text).strip()
                    if degree in boringdegrees:
                        keepit = False
                    else:
                        rec['note'].append(degree)
                #DOI
                elif tht == 'JaLC DOI':
                    rec['doi'] = re.sub('..*doi.org\/', '', td.text.strip())
                #OA
                elif tht == 'Access Rights':
                    if re.search('open access', td.text):
                        oa = True
    ejlmod3.metatagcheck(rec, artpage, ['citation_title', 'citation_date', 'DCTERMS.abstract',
                                        'citation_pdf_url'])
    for meta in artpage.find_all('meta'):
        if meta.has_attr('property'):
            #author
            if meta['property'] == 'citation_author':
                rec['auts'][-1] += ', CHINESENAME: ' + meta['content']
            #handle
            elif meta['property'] == 'og:url':
                rec['link'] = meta['content']
                rec['hdl'] = re.sub('.*handle.net\/', '', meta['content'])
    #Master's Program?
    for div in artpage.find_all('div', attrs = {'class' : 'metadata_block'}):
        if re.search('[mM]aster.?s? [pP]rogram', div.text):
            keepit = False
            print(div.text)
    if keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['hdl'])
        
ejlmod3.writenewXML(recs, publisher, jnlfilename)
