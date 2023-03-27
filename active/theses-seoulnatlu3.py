# -*- coding: utf-8 -*-
#harvest theses from Seoul Natl. U.
#FS: 2020-11-19
#FS: 2023-03-27

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time


publisher = 'Seoul Natl. U.'
jnlfilename = 'THESES-SeoulNatlU-%s' % (ejlmod3.stampoftoday())

rpp = 20
pages = 1
departments = [('', '17020'), ('m', '17007'), ('a', '16967'), ('c', '118749')]
hdr = {'User-Agent' : 'Magic Browser'}
skipalreadyharvested = True

prerecs = []
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
for (fc, dep) in departments:
    for page in range(pages):
        tocurl = 'http://s-space.snu.ac.kr/handle/10371/' + dep + '?page=' + str(page+1) + '&offset=' + str(rpp*page)
        ejlmod3.printprogress("=", [[dep, fc], [page+1, pages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        time.sleep(3)
        for tr in tocpage.body.find_all('tr'):
            rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'supervisor' : [], 'note' : []}
            for a in tr.find_all('a'):
                if a.has_attr('href') and re.search('handle\/', a['href']):
                    rec['artlink'] = 'http://s-space.snu.ac.kr/' + a['href'] 
                    rec['hdl'] = re.sub('.*handle\/', '', a['href'])
                    if ejlmod3.checkinterestingDOI(rec['hdl']):
                        if not skipalreadyharvested or not rec['hdl'] in alreadyharvested:
                            if fc:
                                rec['fc'] = fc
                            prerecs.append(rec)
        print('  %4i records so far ' % (len(prerecs)))

i = 0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        time.sleep(5)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['artlink']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    (author, altauthor) = (False, False)
    keepit = True
    ejlmod3.metatagcheck(rec, artpage, ['DC.title', 'DC.subject', 'citation_pdf_url',
                                        'DCTERMS.extent', 'DC.date'])
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #author
            if meta['name'] == 'DC.creator':
                author = meta['content']
            #supervisor / english name
            elif meta['name'] == 'DC.contributor':
                if meta.has_attr('qualifier'):
                    if meta['qualifier'] == 'advisor':
                        rec['supervisor'].append([meta['content']])
                    elif meta['qualifier'] == 'AlternativeAuthor':
                        altauthor = meta['content']
            #keywords
            elif meta['name'] == 'DC.subject':
                if meta.has_attr('qualifier') and meta['qualifier'] == 'ddc':
                    rec['ddc'] = meta['content']
                    rec['note'].append('DDC=%s' % (meta['content']))
                    if rec['ddc'][:2] in ['54', '55', '56', '57', '58', '59']:
                        keepit = False
                        print('  skip DDC=', rec['ddc'])
                else:
                    for keyw in re.split(' *; *', meta['content']):
                        rec['keyw'].append(keyw)
            #abstract
            elif meta['name'] == 'DCTERMS.abstract':
                if re.search(' the ', meta['content']):
                    rec['abs'] = meta['content']
    #author
    if altauthor:
        if author:
            rec['MARC'] = [('100', [('a', author), ('q', altauthor), ('v', publisher)])]
        else:
            rec['autaff'] = [[ altauthor, publisher ]]
    else:
        rec['autaff'] = [[ author, publisher ]]
    if keepit:
        recs.append(rec)
        ejlmod3.printrecsummary(rec)
    else:
        ejlmod3.addninterestingDOI(rec['hdl'])
        
ejlmod3.writenewXML(recs, publisher, jnlfilename)
