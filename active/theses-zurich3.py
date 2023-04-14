# -*- coding: utf-8 -*-
#harvest theses from Zurich U.
#FS: 2020-11-27
#FS: 2023-04-14

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Zurich U.'
jnlfilename = 'THESES-ZURICH-%s' % (ejlmod3.stampoftoday())

pages = 4
rpp = 20
skipalreadyharvested = True

hdr = {'User-Agent' : 'Magic Browser'}

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

prerecs = []
for page in range(pages):
    tocurl = 'https://www.zora.uzh.ch/cgi/search/archive/advanced?exp=0%7C1%7C-date%2Fcreators_name%2Feditors_name%2Ftitle%7Carchive%7C-%7Csubjects%3Asubjects%3AANY%3AEQ%3A10172+10123+10192%7Ctype%3Atype%3AANY%3AEQ%3Adissertation+habilitation%7C-%7Ceprint_status%3Aeprint_status%3AANY%3AEQ%3Aarchive%7Cmetadata_visibility%3Ametadata_visibility%3AANY%3AEQ%3Ashow&_action_search=1&order=-date%2Fcreators_name%2Feditors_name%2Ftitle&screen=Search&cache=7376471&search_offset=' + str(page*rpp)
    ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    time.sleep(5)
    for dt in tocpage.body.find_all('dt', attrs = {'class' : 'dreiklang_title'}):
        rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'ddc' : []}
        for a in dt.find_all('a'):
            rec['artlink'] = a['href']
            if ejlmod3.checkinterestingDOI(rec['artlink']):           
                prerecs.append(rec)
    print('  %4i records so far' % (len(prerecs)))

recs = []
i = 0
for rec in prerecs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        time.sleep(10)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'citation_title', 'DC.rights',
                                        'citation_publication_date', 'citation_pdf_url',
                                        'eprints.pages', 'eprints.abstract'])
    rec['autaff'][-1].append(publisher)
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #DOI
            if meta['name'] == 'DC.identifier':
                if re.search('10.5167', meta['content']):
                    rec['doi'] = re.sub('.*?(10.5167.*)', r'\1', meta['content'])
            #keywords
            elif meta['name'] == 'citation_keywords':
                for keyw in re.split(' *, +', meta['content']):
                    rec['keyw'].append(keyw)
            #language
            elif meta['name'] == 'citation_language':
                if meta['content'] == 'ger':
                    rec['language'] = 'german'
                elif meta['content'] != 'eng':
                    rec['language'] = meta['content']
            #DDC
            elif meta['name'] == 'eprints.dewey':
                rec['ddc'].append(re.sub('^ddc', '', meta['content']))
            #abstract
            elif meta['name'] == 'eprints.abstract':
                rec['abs'] = meta['content']
    if not 'doi' in list(rec.keys()):
        rec['doi'] = '20.2000/Zurich/' + re.sub('\D', '', rec['artlink'])
        rec['link'] = rec['artlink']
    keepit = True
    if 'ddc' in list(rec.keys()):
        keepit = False
        for ddc in rec['ddc']:
            if re.search('^5[0123]', ddc) or ddc == '004':
                keepit = True
    if keepit:
        if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
            recs.append(rec)
            ejlmod3.printrecsummary(rec)
    else:
        print('  skip', rec['ddc'])
        ejlmod3.adduninterestingDOI(rec['artlink'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
