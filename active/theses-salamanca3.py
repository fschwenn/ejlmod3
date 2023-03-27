# -*- coding: utf-8 -*-
#harvest theses from Salamanca U.
#FS: 2022-04-20
#FS: 2023-03-25

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

rpp = 10
years = 2
skipalreadyharvested = True

publisher = 'Salamanca U.'
jnlfilename = 'THESES-SALAMANCA-%s' % (ejlmod3.stampoftoday())

hdr = {'User-Agent' : 'Magic Browser'}
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []
    
recs = []
for (fc, dep) in [('m', '4145'), ('m', '4154'), ('', '4091'), ('', '4109'), ('s', '4074'), ('c', '4394')]:
    tocurl = 'https://gredos.usal.es/handle/10366/' + dep + '/browse?order=DESC&rpp=' + str(rpp) + '&sort_by=3&etal=-1&offset=' + str(0 * rpp) + '&type=dateissued'
    print(tocurl)
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    time.sleep(3)
    for rec in ejlmod3.getdspacerecs(tocpage, 'https://gredos.usal.es', alreadyharvested=alreadyharvested):
        if 'year' in rec and int(rec['year']) <= ejlmod3.year(backwards=years):
            print('  %s too old' % (rec['year']))
        else:
            if fc:
                rec['fc'] = fc
            recs.append(rec)
    print('  %4i records so far' % (len(recs)))

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['link']]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(4)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['DC.title', 'DCTERMS.issued', 'citation_pdf_url', 'citation_doi',
                                        'DC.language', 'DC.rights', 'DC.creator', 'DC.contributor'])
    rec['autaff'][-1].append(publisher)
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name') and meta.has_attr('content'):
            #translated title
            if meta['name'] == 'DCTERMS.alternative':
                rec['transtit'] = meta['content']
            #keywords
            elif meta['name'] == 'DC.subject':
                if not meta['content'] in ['Tesis y disertaciones académicas', 'Universidad de Salamanca (España)',
                                           'Resumen de tesis', 'Thesis Abstracts']:
                    rec['keyw'].append(meta['content'])
            #abstract
            elif meta['name'] == 'DCTERMS.abstract':
                if 'abs' in list(rec.keys()) and (re.search('^\[EN', rec['abs']) or re.search(' the ', rec['abs'])):
                    pass
                else:
                    rec['abs'] = meta['content']
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
