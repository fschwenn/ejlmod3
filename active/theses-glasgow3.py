# -*- coding: utf-8 -*-
#harvest theses from University of Glasgow
#FS: 2020-02-14
#FS: 2023-03-14

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Glasgow U.'
jnlfilename = 'THESES-GLASGOW-%s' % (ejlmod3.stampoftoday())

pages = 4
skipalreadyharvested = True
boringdegrees = ["MSc(R)", "MD", "MPhil(R)", "MVM(R)", "MRes"]

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
for page in range(pages):
    tocurl = 'http://theses.gla.ac.uk/cgi/search/archive/advanced?exp=0%7C1%7C-date%2Fcreators_name%2Ftitle%7Carchive%7C-%7Csubjects%3Asubjects%3AANY%3AEQ%3AQ1+QA+QB+QC%7C-%7Ceprint_status%3Aeprint_status%3AANY%3AEQ%3Aarchive%7Cmetadata_visibility%3Ametadata_visibility%3AANY%3AEQ%3Ashow&_action_search=1&order=-date%2Fcreators_name%2Ftitle&screen=Search&cache=500363&search_offset=' + str(20*page)
    ejlmod3.printprogress("-", [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features='lxml')
#    for tr in tocpage.body.find_all('tr', attrs = {'class' : 'ep_search_result'}):
    for tr in tocpage.body.find_all('div', attrs = {'class' : 'ep_search_result'}):
        rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'supervisor' : [], 'note' : []}
        for div in tr.find_all('div', attrs = {'class' : 'ep_search_result_docs'}):
            for a in tr.find_all('a'):
                if a.has_attr('href') and re.search('theses.gla.ac.uk\/\d+.*pdf$', a['href']):
                    rec['pdf_url'] = a['href']
            div.decompose()
        for a in tr.find_all('a'):
            if a.has_attr('href') and re.search('theses.gla.ac.uk\/\d+.?', a['href']):
                rec['link'] = a['href']
                rec['doi'] = '20.2000/' + re.sub('\W', '', a['href'])
                rec['tit'] = a.text.strip()
                if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
                    if ejlmod3.checkinterestingDOI(rec['doi']):
                        prerecs.append(rec)
                    else:
                        print('   %s not interesting' % (rec['doi']))
                else:
                    print('   %s already in backup' % (rec['doi']))
    print('  %4i records so far' % (len(prerecs)))
    time.sleep(5)

                
i = 0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
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
    ejlmod3.metatagcheck(rec, artpage, ['eprints.creators_name', 'eprints.creators_id', 'eprints.title',
                                        'eprints.date', 'DC.subject', 'eprints.abstract', 'eprints.document_url',
                                        'eprints.supervisor_name', 'eprints.id_number'])  #not 'eprints.supervisor_id' as SVs not properly ordered
    rec['autaff'][-1].append(publisher)
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'eprints.thesis_type'}):
        rec['note'].append( meta['content'] )
    keepit = True
    for note in rec['note']:
        if note in boringdegrees:
            keepit = False
            print('   skip "%s"' % (note))
    if keepit:
        if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
            recs.append(rec)
            ejlmod3.printrecsummary(rec)
        else:
            print('   %s already in backup' % (rec['doi']))
    else:
        ejlmod3.adduninterestingDOI(rec['doi'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
