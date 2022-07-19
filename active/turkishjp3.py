#!/usr/bin/python
# -*- coding: UTF-8 -*-
#program to harvest Turkish Journal of Physics 
# FS 2015-08-26

import os
import ejlmod3
import re
import sys
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import time


def tfstrip(x): return x.strip()

publisher = 'TÜBİTAK'
#publisher = 'TUBITAK'
jnl = sys.argv[1]
vol = sys.argv[2]
year = str(int(vol)+1976)
issue = sys.argv[3]

if   (jnl == 'tjp'):
    jnlname = 'Turk.J.Phys.'
    issn = "0019-5596"
    urlkey = 'physics'
    oldurlkey = 'fiz'
elif (jnl == 'tjm'):
    urlkey = 'math'
    oldurlkey = 'mat'
    jnlname = 'Turk.J.Math.'
    issn = "1300-0098"
jnlfilename = jnl+vol+'.'+issue

tocurl = 'https://journals.tubitak.gov.tr/%s/vol%s/iss%s/' % (urlkey, vol, issue)
print(tocurl)
page = BeautifulSoup(urllib.request.urlopen(tocurl), features="lxml")

recs = []
section = ''
for div in page.body.find_all('div', attrs = {'class' : 'article-list'}):
    for child in div.children:
        try:
            cn = child.name
        except:
            continue
        if cn == 'h2':
            section = child.text
        elif cn == 'div':
            print(child['class'])
            if child.has_attr('class') and 'doc' in child['class']:
                rec = {'jnl' : jnlname, 'tc' : 'P', 'vol' : vol, 'issue' : issue, 'note' : []}
                rec['license'] = {'statement' : 'CC-BY-4.0'}
                if section:
                    rec['note'].append(section)
                for a in child.find_all('a'):
                    if a.has_attr('href'):
                        if a.has_attr('class') and a['class'] == 'pdf':
                            rec['FFT'] = a['href']
                        else:
                            rec['artlink'] = a['href']
                if not section in ['Cover and Contents']:
                    recs.append(rec)

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress('-', [[i, len(recs)], [rec['artlink']]])
    time.sleep(5)
    artpage = BeautifulSoup(urllib.request.urlopen(rec['artlink']), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['bepress_citation_firstpage', 'og:title', 'bepress_citation_author',
                                        'description', 'bepress_citation_lastpage', 'bepress_citation_date',
                                        'bepress_citation_doi', 'keywords'])
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)


