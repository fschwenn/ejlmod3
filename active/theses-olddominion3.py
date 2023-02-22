# -*- coding: utf-8 -*-
#harvest Old Dominion U.
#FS: 2021-12-13
#FS: 2023-02-22

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Old Dominion U. (main)'
skipalreadyharvested = True


jnlfilename = 'THESES-OLDDOMINION-%s' % (ejlmod3.stampoftoday())
boringdegrees = []
basetocurl = 'https://digitalcommons.odu.edu/'

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

prerecs = []
for (url, aff, fc) in [('physics_etds/', 'Old Dominion U.', ''),
                       ('mathstat_etds/', 'Old Dominion U. (main)', 'm')]:
    tocurl = basetocurl + url
    print(tocurl)
    try:
        tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
        time.sleep(3)
    except:
        print("retry %s in 180 seconds" % (tocurl))
        time.sleep(180)
        tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
    for div in tocpage.body.find_all('div', attrs = {'id' : 'series-home'}):
        for child in div.children:
            try:
                name = child.name
            except:
                continue
            if name == 'h4':
                for span in child.find_all('span'):
                    date = span.text.strip()
            elif name == 'p':
                if child.has_attr('class') and 'article-listing' in child['class']:
                    #year = int(re.sub('.*(20\d\d).*', r'\1', rec['date']))
                    if int(date) >= ejlmod3.year() - 1:
                        rec = {'jnl' : 'BOOK', 'tc' : 'T', 'date' : date, 'note' : []}
                        if fc:
                            rec['fc'] = fc
                        for a in child.find_all('a'):
                            rec['tit'] = a.text.strip()
                            rec['artlink'] = a['href']
                            a.replace_with('')
                            if ejlmod3.checkinterestingDOI(rec['artlink']):
                                prerecs.append(rec)
    print('  ', len(prerecs))


recs = []
i = 0
for rec in prerecs:
    keepit = True
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        time.sleep(3)
    except:
        print("retry %s in 180 seconds" % (rec['artlink']))
        time.sleep(180)
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['description', 'keywords', 'bepress_citation_author', 'bepress_citation_pdf_url',
                                        'bepress_citation_doi', 'bepress_citation_date'])
    #ORCID
    for div in artpage.body.find_all('div', attrs = {'id' : 'orcid'}):
        for p in div.find_all('p'):
            rec['autaff'][-1].append('ORCID:'+re.sub('.*org\/', '', p.text.strip()))
    rec['autaff'][-1].append(publisher)
    #degree
    for div in artpage.body.find_all('div', attrs = {'id' : 'degree_name'}):
        for p in div.find_all('p'):
            degree = p.text.strip()
            rec['note'].append(degree)
            if degree in boringdegrees:
                print('    skip "%s"' % (degree))
                keepit = False
    #peusoDOI
    if 'doi' not in rec:
        rec['doi'] = '20.2000/OldDominion/' + re.sub('\W', '', re.sub('.*edu', '', rec['artlink']))
        rec['link'] = rec['artlink']        
    #license
    ejlmod3.globallicensesearch(rec, artpage)
    #ISBN
    for div in artpage.body.find_all('div', attrs = {'id' : 'identifier'}):
        for h4 in div.find_all('h4'):
            if h4.text.strip() == 'ISBN':
                for p in div.find_all('p'):
                    ISBN = p.text.strip()
                    rec['isbn'] = ISBN
    if keepit:
        if skipalreadyharvested and rec['doi'] in alreadyharvested:
            print('   already in backup')
        else:
            ejlmod3.printrecsummary(rec)
            recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['artlink'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
