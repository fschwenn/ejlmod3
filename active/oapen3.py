# -*- coding: utf-8 -*-
#harvest books from oapen.org
#FS: 2021-10-19
#FS: 2023-02-06

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import json

rpp = 50
pages = 2
publishers = {}
hdr = {'User-Agent' : 'Magic Browser'}
skipalreadyharvested = True

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested('oapen_')
    
recs = []
for page in range(pages):
    tocurl = 'https://library.oapen.org/browse?rpp=' + str(rpp) + '&offset=' + str(rpp*page) + '&etal=-1&sort_by=3&type=collection&value=SCOAP3+for+Books&order=DSC'
    ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    for li in tocpage.body.find_all('li', attrs = {'class' : 'ds-artifact-item'}):
        rec = {'tc' : 'B', 'keyw' : [], 'jnl' : 'BOOK', 'note' : [], 'autaff' : []}
        for div in li.find_all('div', attrs = {'class' : 'artifact-title'}):
            for a in div.find_all('a'):
                rec['artlink'] = 'https://library.oapen.org' + a['href']
                rec['hdl'] = re.sub('.*handle\/', '', a['href'])
            if skipalreadyharvested and rec['hdl'] in alreadyharvested:
                print('   %s already in backup' % (rec['hdl']))
                pass
            else:
                recs.append(rec)
    time.sleep(3)

i = 0
reorcid = re.compile('^([A-Za-z].*) \[(\d\d\d\d\-.*)\]')
for rec in recs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['artlink']]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['artlink']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        except:
            print("no access to %s" % (rec['artlink']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'citation_title', 'citation_publication_date',
                                        'DC.subject', 'DCTERMS.abstract', 'citation_pdf_url',
                                        'citation_isbn', 'citation_pages', 'citation_doi',
                                        'citation_publisher'])    
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'citation_publisher'}):
        rec['publisher'] = meta['content']
    #editors
    if not rec['autaff']:
        for meta in artpage.head.find_all('meta', attrs = {'name' : 'citation_editor'}):
            rec['autaff'].append([meta['content'].title() + ' (Ed.)'])
    #ORCID?
    for j in range(len(rec['autaff'])):
        if reorcid.search(rec['autaff'][j][0]):
            newautaff = [ reorcid.sub(r'\1', rec['autaff'][j][0]), reorcid.sub(r'ORCID:\2', rec['autaff'][j][0]) ]
            print(rec['autaff'][j],'---->',newautaff)
            rec['autaff'][j] = newautaff        
    #license
    ejlmod3.globallicensesearch(rec, artpage)
    #sort
    if rec['publisher'] in publishers:
        publishers[rec['publisher']].append(rec)
    else:
        publishers[rec['publisher']] = [rec]
    ejlmod3.printrecsummary(rec)

for publisher in list(publishers.keys()):
    jnlfilename = 'oapen_%s.%s' % (ejlmod3.stampoftoday(), re.sub('\W', '', publisher))
    ejlmod3.writenewXML(publishers[publisher], publisher, jnlfilename)
