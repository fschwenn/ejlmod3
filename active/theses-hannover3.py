# -*- coding: utf-8 -*-
#harvest theses from Leibniz U., Hannover
#FS: 2020-03-24
#FS: 2023-02-20

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import mechanize
import unicodedata

publisher = 'Leibniz U., Hannover'

numberofpages = 4
recordsperpage = 50
skipalreadyharvested = True

prerecs = []
recs = []
jnlfilename = 'THESES-HANNOVER-%s' % (ejlmod3.stampoftoday())
for pn in range(numberofpages):
    tocurl = 'https://www.repo.uni-hannover.de/handle/123456789/2962/browse?rpp=' + str(recordsperpage) + '&sort_by=2&type=dateissued&offset=' + str(pn * recordsperpage) + '&etal=-1&order=DESC'
    ejlmod3.printprogress("=", [[pn+1, numberofpages], [tocurl]])
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
    for rec in ejlmod3.getdspacerecs(tocpage, 'https://www.repo.uni-hannover.de', fakehdl=True):
        if ejlmod3.checkinterestingDOI(rec['link']):
            prerecs.append(rec)
    print('  %4i records so far' % (len(prerecs)))
    time.sleep(10)

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

i = 0
for rec in prerecs:
    wrongddc = False
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(5)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'DC.identifier', 'DC.title',
                                        'citation_date', 'DC.language', 'citation_pdf_url',
                                        'DCTERMS.abstract', 'DC.rights'])
    rec['autaff'][-1].append(publisher)
    for meta in artpage.find_all('meta', attrs = {'name' : 'DC.subject'}):
        #DDC
        if meta.has_attr('scheme') and meta['scheme'] == 'DCTERMS.DDC':
            rec['ddc'] = meta['content']
            rec['note'].append(meta['content'])
            if rec['ddc'][:2] == '51':
                rec['fc'] = 'm'
            elif rec['ddc'][:2] == '52':
                rec['fc'] = 'a'
            elif not rec['ddc'][:2] in ['50', '53']:
                if rec['ddc'][:3] == '004':
                    rec['fc'] = 'c'
                else:
                    print('  skip DDC=%s' % (rec['ddc']))
                    wrongddc = True
        #keywords
        elif meta['xml:lang'] == 'eng':
            for keyw in re.split(' *; *', meta['content']):
                rec['keyw'].append(keyw)
    if wrongddc:
        ejlmod3.adduninterestingDOI(rec['link'])
    else:
        if skipalreadyharvested and rec['doi'] in alreadyharvested:
            print('   already in backup')
        else:
            ejlmod3.printrecsummary(rec)
            recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
