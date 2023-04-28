# -*- coding: utf-8 -*-
#harvest theses from Hokkaido U.
#FS: 2021-12-17
#FS: 2023-04-28


import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time


publisher = 'Hokkaido U.'
jnlfilename = 'THESES-HOKKAIDO-%s' % (ejlmod3.stampoftoday())

rpp = 50
pages = 2
skipalreadyharvested = True

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
for page in range(pages):
    tocurl = 'https://eprints.lib.hokudai.ac.jp/dspace/handle/2115/20136/browse?type=dateissued&sort_by=2&order=DESC&rpp=' + str(rpp) + '&etal=-1&null=&offset=' + str(page*rpp)
    ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    time.sleep(5)
    for td in tocpage.body.find_all('td', attrs = {'headers' : 't3'}):
        for a in td.find_all('a'):
            rec = {'tc' : 'T', 'jnl' : 'BOOK', 'note' : []}
            rec['link'] = 'https://eprints.lib.hokudai.ac.jp' + a['href']
            rec['hdl'] = re.sub('.*handle\/', '', a['href'])
            if not skipalreadyharvested or not rec['hdl'] in alreadyharvested:
                prerecs.append(rec)


i = 0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link'] + '?mode=full'), features="lxml")
        time.sleep(5)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'citation_pdf_url', 'DCTERMS.abstract',
                                        'citation_title', 'DCTERMS.alternative',
                                        'citation_publication_date', 'citation_keywords'])
    rec['autaff'][-1].append(publisher)
    for tr in artpage.body.find_all('tr'):
        for td in tr.find_all('td', attrs = {'class' : 'metadataFieldLabel'}):
            mfl = td.text.strip()
        for td in tr.find_all('td', attrs = {'class' : 'metadataFieldValue'}):
            if td.text.strip() == 'en':
                continue
            #DOI
            if mfl == 'dc.identifier.selfdoi':
                rec['doi'] = td.text.strip()
            #pages
            elif mfl == 'dc.format.physicalSize':
                if re.search('\d\d', td.text):
                    rec['pages'] = re.sub('.*?(\d\d+).*', r'\1', td.text.strip())
    if skipalreadyharvested and 'doi' in rec and rec['doi'] in alreadyharvested:
        print('   %i already in backup' % (rec['doi']))
    else:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
