# -*- coding: utf-8 -*-
#harvest theses from Rostock U.
#FS: 2021-03-21

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Rostock U.'
jnlfilename = 'THESES-ROSTOCK-%s' % (ejlmod3.stampoftoday())

rpp = 20
pages = 1
skipalreadyharvested = True

boring = []
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
artlinks = []
for ddc in ['530', '510', '500', '520', '004']:
    for j in range(pages):
        tocurl = 'http://rosdok.uni-rostock.de/do/browse/epub?_search=811f238e-c54c-48f3-8b0a-3f35a06f6650&_add-filter=%2Bir.sdnb_class.facet%3ASDNB%3A' + ddc + '&_start=' + str(rpp*j) + '&_add-filter=%2Bir.doctype_class.facet%3Adoctype%3Aepub.dissertation'
        ejlmod3.printprogress('=', [[ddc], [j+1, pages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        for span in tocpage.body.find_all('span', attrs = {'class' : 'ir-pagination-btn-numfound'}):
            print(span.text)
        divs = tocpage.body.find_all('div', attrs = {'class' : 'col-md-9'})
        for div in divs:
            for h4 in div.find_all('h4'):
                for a in h4.find_all('a'):
                    rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'supervisor' : [], 'note' : ['DDC:'+ddc]}
                    rec['artlink'] = 'https://rosdok.uni-rostock.de/' + a['href']
                    if not rec['artlink'] in artlinks:
                        prerecs.append(rec)
                        artlinks.append(rec['artlink'])
        time.sleep(15)
        print('  %i links so far' % (len(artlinks)))

i = 0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
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
    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'DC.title', 'citation_publication_date', 'citation_doi',
                                        'DC.description', 'citation_pdf_url', 'DC.rights'])
    rec['autaff'][-1].append(publisher)
    label = ''
    for tr in artpage.find_all('tr'):
        for th in tr.find_all('th'):
            label = th.text.strip()
        for td in tr.find_all('td'):
            try:
                word = td.text.strip()
            except:
                word = ''
            if word and label:
                #language
                if re.search('(language|Sprach)', label):
                    if word in ['Deutsch', 'German']:
                        rec['language'] = 'German'
    if not 'doi' in rec or not skipalreadyharvested or not rec['doi'] in alreadyharvested:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
