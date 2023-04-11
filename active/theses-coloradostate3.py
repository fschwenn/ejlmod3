# -*- coding: utf-8 -*-
#harvest theses from Colorado State U., Fort Collins
#FS: 2021-12-06
#FS: 2023-03-29

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Colorado State U., Fort Collins'
jnlfilename = 'THESES-ColoradoStateU-%s' % (ejlmod3.stampoftoday())

rpp = 20
skipalreadyharvested = True
pages = 1

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []
hdr = {'User-Agent' : 'Magic Browser'}
recs = []
for dep in [('Physics', '', '100500', 'Colorado State U.'),
            ('Mathematics', 'm', '100469', 'Colorado State U., Fort Collins'),
            ('Computer Science', 'c', '100389', 'Colorado State U., Fort Collins')]:
    for page in range(pages):
        tocurl = 'https://mountainscholar.org/handle/10217/' + dep[2] + '/discover?rpp=' + str(rpp) + '&etal=0&group_by=none&page=' + str(page+1) + '&sort_by=dc.date.issued_dt&order=desc'
        ejlmod3.printprogress("=", [[dep[0]], [page+1, pages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        for rec in ejlmod3.getdspacerecs(tocpage, 'https://mountainscholar.org', alreadyharvested=alreadyharvested):
            if dep[1]:
                rec['fc'] = dep[1]
            rec['affiliation'] = dep[3]
            recs.append(rec)
        time.sleep(10)
        print('  %4i records so far' % (len(recs)))

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['link'] + '?show=full']])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link'] + '?show=full'), features="lxml")
        time.sleep(5)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link'] + '?show=full'))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link'] + '?show=full'), features="lxml")
        except:
            print("no access to %s" % (rec['link'] + '?show=full'))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'DC.title', 'DCTERMS.issued', 'DC.subject',
                                        'DCTERMS.abstract', 'citation_pdf_url'])
    rec['autaff'][-1].append(rec['affiliation'])
    ejlmod3.globallicensesearch(rec, artpage)
    #supervisor + degree
    for tr in artpage.find_all('tr'):
        for td in tr.find_all('td', attrs = {'class' : 'label-cell'}):
            tdt = td.text.strip()
        for td in tr.find_all('td', attrs = {'class' : 'word-break'}):
            if tdt == 'dc.contributor.advisor':
                rec['supervisor'].append([td.text.strip()])
            elif tdt == 'thesis.degree.level':
                degree = td.text.strip()
                if degree != 'Doctoral':
                    rec['note'].append(degree)
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
