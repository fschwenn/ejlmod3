# -*- coding: utf-8 -*-
#harvest theses from Warsaw U.
#FS: 2020-11-29
#FS: 2023-04-14

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import ssl

rpp = 20
skipalreadyharvested = True

publisher = 'Warsaw U. (main)'
jnlfilename = 'THESES-WARSAW-%s' % (ejlmod3.stampoftoday())

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

recs = []
hdr = {'User-Agent' : 'Magic Browser'}
#bad certificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

deps = [('29', 'Warsaw U., Inst. Math. Mech.', 'math'), ('5', 'Warsaw U.', 'phys')]

for (depnr, aff, subject) in deps:   
    tocurl = 'https://depotuw.ceon.pl/handle/item/' + depnr + '/discover?sort_by=dc.date.issued_dt&order=desc&rpp=' + str(rpp)
    print(tocurl)
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
    time.sleep(3)
    for div in tocpage.body.find_all('div', attrs = {'class' : 'artifact-title'}):
        for a in div.find_all('a'):
            rec = {'tc' : 'T', 'jnl' : 'BOOK', 'keyw' : [], 'note' : [], 'supervisor' : []}
            rec['link'] = 'https://depotuw.ceon.pl' + a['href'] + '?show=full'
            rec['doi'] = '20.2000/Warsaw/' + re.sub('\/handle\/', '', a['href'])
            rec['tit'] = a.text.strip()
            rec['affiliation'] = aff
            if depnr == '29':
                rec['fc'] = 'm'
            if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
                recs.append(rec)

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['link']]])
    try:
        req = urllib.request.Request(rec['link'], headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        time.sleep(4)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'DC.contributor', 'DC.title',
                                        'DCTERMS.alternative', 'DC.date',
                                        'citation_pdf_url', 'DCTERMS.extent',
                                        'DC.language', 'DC.rights'])
    rec['autaff'][-1].append(rec['affiliation'])
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name') and meta.has_attr('content'):
            #keywords
            if meta['name'] == 'DC.subject':
                if meta.has_attr('scheme'):
                    rec['ddc'] = meta['content']
                else:
                    rec['keyw'].append(meta['content'])
            #abstract
            elif meta['name'] == 'DCTERMS.abstract':
                if re.search(' the ', meta['content']):
                    rec['abs'] = meta['content']
                else:
                    rec['abspl'] = meta['content']
    if 'abspl' in list(rec.keys()) and not 'abs' in list(rec.keys()):
        rec['abs'] = rec['abspl']
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
