# -*- coding: utf-8 -*-
#harvest theses from University of Bayreuth
#FS: 2023-04-07

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Bayreuth U.'
jnlfilename = 'THESES-BAYREUTH-%s' % (ejlmod3.stampoftoday())

skipalreadyharvested = True
pages = 1
rpp = 20

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
for page in range(pages):
    tocurl = 'https://epub.uni-bayreuth.de/cgi/search/archive/advanced?screen=Search&cache=821856&_action_search=1&order=-date%2Fcreators_name%2Ftitle&exp=0%7C1%7C-date%2Fcreators_name%2Ftitle%7Carchive%7C-%7Cdivisions%3Adivisions%3AANY%3AEQ%3A110000%7Ctype%3Atype%3AANY%3AEQ%3Athesis+habilitation%7C-%7Ceprint_status%3Aeprint_status%3AANY%3AEQ%3Aarchive%7Cmetadata_visibility%3Ametadata_visibility%3AANY%3AEQ%3Ashow&search_offset=' + str(rpp*page)
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features='lxml')
    for div in tocpage.body.find_all('div', attrs = {'class' : 'ep_search_results'}):
        for a in div.find_all('a'):
            if re.search('^http.*\/id\/', a['href']):
                rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'note' : []}
                rec['artlink'] = a['href']
                if ejlmod3.checkinterestingDOI(rec['artlink']):
                    prerecs.append(rec)
    print('  %4i records so far' % (len(prerecs)))
    
recs = []
for (i, rec) in enumerate(prerecs):
    ejlmod3.printprogress("-", [[i+1, len(prerecs)], [rec['artlink']], [len(recs)]])
    keepit = True
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features='lxml')
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['artlink']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features='lxml')
        except:
            print("no access to %s" % (rec['artlink']))
            continue    
    ejlmod3.metatagcheck(rec, artpage, ['eprints.creators_name', 'DC.title', #'DC.date',
                                        'eprints.pages', 'eprints.related_doi', 'eprints.document_url',
                                        "eprints.language", "eprints.urn", "eprints.thesis_datum",
                                        "eprints.keywords", "eprints.creators_id"])
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'DC.subject'}):
        ddc = meta['content']
        if ddc in ['520 Astronomy', '520 Astronomie']:
            rec['fc'] = 'a'
        elif ddc in ['510 Mathematics', '510 Mathematik']:
            rec['fc'] = 'm'
        elif ddc in ['004 Informatik']:
            rec['fc'] = 'c'
        elif ddc in ['540 Chemie', '550 Geowissenschaften, Geologie', '570 Biowissenschaften; Biologie']:
            keepit = False
        #elif not ddc in ['530 Physics', '530 Physik']:
        #    rec['note'].append(ddc)
    #abstract
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'eprints.abstract_original_lang'}):
        if meta['content'] == 'eng':
            for meta2  in artpage.head.find_all('meta', attrs = {'name' : 'eprints.abstract_original_text'}):
                rec['abs'] = meta2['content']
        else:
            for meta3 in artpage.head.find_all('meta', attrs = {'name' : 'eprints.abstract_translated_lang'}):
                if meta3['content'] == 'eng':
                    for meta2  in artpage.head.find_all('meta', attrs = {'name' : 'eprints.abstract_translated_text'}):
                        rec['abs'] = meta2['content']
    #division
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'eprints.divisions'}):
        division = meta['content']
        if division in ['111000']:
            rec['fc'] = 'm'
        elif division in ['112001', '112002', '112003', '112004', '112015', '112107']:
            rec['fc'] = 'q'
        elif division in ['114000']:
            rec['fc'] = 'c'
        elif division in ['112008']:
            rec['fc'] = 'f'            
    rec['autaff'][-1].append('Bayreuth U.')
    if skipalreadyharvested and 'doi' in rec and rec['doi'] in alreadyharvested:
        print('   already in backup')
    else:
        if keepit:
            recs.append(rec)
            ejlmod3.printrecsummary(rec)
        else:
            ejlmod3.adduninterestingDOI(rec['artlink'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
