# -*- coding: utf-8 -*-
#harvest theses from University of Nottingham
#FS: 2021-12-06
#FS: 2023-02-24

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Nottingham U.'

hdr = {'User-Agent' : 'Magic Browser'}
jnlfilename = 'THESES-NOTTINGHAM-%s' % (ejlmod3.stampoftoday())
recs = []

pages = 4
skipalreadyharvested = True

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

for page in range(pages):
    tocurl = 'http://eprints.nottingham.ac.uk/cgi/search/archive/advanced_t?exp=0%7C1%7C-date%2Fcreators_name%2Ftitle%7Carchive%7C-%7Ceth_subjects%3Aeth_subjects%3AANY%3AEQ%3AQA+QB+QC%7Cthesis_type%3Athesis_type%3AANY%3AEQ%3APhD%7C-%7Ceprint_status%3Aeprint_status%3AANY%3AEQ%3Aarchive%7Cmetadata_visibility%3Ametadata_visibility%3AANY%3AEQ%3Ashow%7Ctype%3Atype%3AANY%3AEQ%3Aethesis&_action_search=1&order=-date%2Fcreators_name%2Ftitle&screen=Search&cache=15020075&search_offset=' + str(page*20)
    ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    for tr in tocpage.body.find_all('tr', attrs = {'class' : 'ep_search_result'}):
        rec = {'tc' : 'T', 'jnl' : 'BOOK', 'autaff' : [], 'supervisor' : [], 'note' : [], 'fc' : []}
        for a in tr.find_all('a'):
            if not re.search('(zip|pdf)$', a['href']):
                rec['link'] = a['href']
                rec['doi'] = '20.2000/Nottingham/'+re.sub('\D', '', a['href'])
                if not rec['doi'] in ['20.2000/Nottingham/289862']:
                    if skipalreadyharvested and rec['doi'] in alreadyharvested:
                        print('   %s already in backup' % (rec['doi']))
                    else:
                        recs.append(rec)
    print('  %4i records so far' % (len(recs)))
    time.sleep(5)
            
i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['link']]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue    
    ejlmod3.metatagcheck(rec, artpage, ['eprints.date', 'eprints.creators_name', 'eprints.creators_id',
                                        'eprints.title', 'eprints.abstract', 'eprints.keywords',
                                        'eprints.document_url', 'eprints.supervisors_name'])
    #division
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'eprints.eth_divisions'}):
        if meta['content'] == 'e_Sci_Maths':
            rec['fc'].append('m')
        elif meta['content'] == 'e_Sci_Computer':
            rec['fc'].append('c')
        else:
            rec['note'].append([meta['content']])
    rec['autaff'][-1].append(publisher)
    ejlmod3.printrecsummary(rec)
    
ejlmod3.writenewXML(recs, publisher, jnlfilename)
