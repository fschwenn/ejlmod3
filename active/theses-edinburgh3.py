# -*- coding: utf-8 -*-
#harvest theses from University of Edinburgh
#FS: 2019-11-25
#FS: 2023-03-17

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Edinburgh U.'
jnlfilename = 'THESES-EDINBURGH-%s' % (ejlmod3.stampoftoday())

rpp = 50
skipalreadyharvested = True
pages = 1+4


if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
hdr = {'User-Agent' : 'Magic Browser'}
recs = []
hdls = []
#for (dep, fc) in [('3420', ''), ('3389', 'c'), ('2284', 'm')]:
for (dep, fc) in [('3389', 'c'), ('2284', 'm')]:
    for page in range(pages):
        tocurl = 'https://www.era.lib.ed.ac.uk/handle/1842/' + dep + '/discover?sort_by=dc.date.issued_dt&order=desc&rpp=' + str(rpp) + '&page=' + str(page+1)
        ejlmod3.printprogress("=", [[dep], [page+1, pages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        for rec in ejlmod3.getdspacerecs(tocpage, 'https://www.era.lib.ed.ac.uk'):
            if not skipalreadyharvested or not rec['hdl'] in alreadyharvested:
                if fc: rec['fc'] = fc
                recs.append(rec)
        print('  %4i records so far' % (len(recs)))
        time.sleep(5)

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['link']]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']+'?show=full'), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']+'?show=full'), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue    
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'DC.title', 'DCTERMS.issued', 'DC.subject',
                                        'DCTERMS.abstract', 'citation_pdf_url', 'DC.identifier'])
    rec['autaff'][-1].append('Edinburgh U.')
    #
    # "too many" advisors
    #
    #for tr in artpage.find_all('tr'):
    #    tdlabel = ''
    #    for td in tr.find_all('td', attrs = {'class' : 'label-cell'}):
    #        tdlabel = td.text.strip()
    #    for td in tr.find_all('td', attrs = {'class' : 'word-break'}):
    #        #supervisor
    #        if tdlabel == 'dc.contributor.advisor':
    #            rec['supervisor'].append([td.text.strip()])
    ejlmod3.printrecsummary(rec)
    time.sleep(1)
#    if i%20 == 0:
#        ejlmod3.writenewXML(recs[:i], publisher, jnlfilename)#, retfilename='retfiles_special')

ejlmod3.writenewXML(recs, publisher, jnlfilename)#, retfilename='retfiles_special')
