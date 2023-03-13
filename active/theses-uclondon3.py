# -*- coding: utf-8 -*-
#harvest University College London Theses
#FS: 2020-02-10
#FS: 2023-03-11

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'University Coll. London'
jnlfilename = 'THESES-UCLONDON-%s' % (ejlmod3.stampoftoday())

skipalreadyharvested = True
pages = 5

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

hdr = {'User-Agent' : 'Magic Browser'}
recs = []
for page in range(pages):
    tocurl = 'https://discovery.ucl.ac.uk/cgi/search/archive/advanced?screen=Search&dataset=archive&documents_merge=ALL&documents=&title_merge=ALL&title=&creators_name_merge=ALL&creators_name=&editors_name_merge=ALL&editors_name=&abstract_merge=ALL&abstract=&divisions=C06&divisions_merge=ANY&date=&type=thesis&satisfyall=ALL&order=-date%2Fcreators_name%2Ftitle&_action_search=Search&search_offset=' + str(20*page)
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    time.sleep(2)
    for tr in tocpage.find_all('tr', attrs = {'class' : 'ep_search_result'}):
        for a in tr.find_all('a'):
            if a.has_attr('href') and re.search('discovery.ucl.ac.uk\/id\/eprint', a['href']):
                rec = {'tc' : 'T', 'jnl' : 'BOOK', 'link' : a['href'], 'note' : []}
                rec['tit'] = a.text.strip()
                rec['doi'] = '20.2000/UCLodon/' + re.sub('\D', '', a['href'])
                if skipalreadyharvested and rec['doi'] in alreadyharvested:
                    pass
                else:
                    recs.append(rec)
    print('  %4i records so far' % (len(recs)))

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['link']]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(10)
    except:
        try:
            print('retry %s in 180 seconds' % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        except:
            print('no access to %s' % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['eprints.creators_name', 'eprints.creators_orcid',
                                        'eprints.keywords', 'eprints.abstract', 'eprints.date',
                                        'eprints.doi', 'eprints.pages'])
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #PDF
            if meta['name'] == 'eprints.document_url':
                rec['FFT'] = meta['content']
            #PDF
            elif meta['name'] == 'eprints.thesis_award':
                rec['note'].append(meta['content'])
    rec['autaff'][-1].append(publisher)
    ejlmod3.printrecsummary(rec)


ejlmod3.writenewXML(recs, publisher, jnlfilename)
