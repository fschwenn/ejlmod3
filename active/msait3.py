# -*- coding: utf-8 -*-
#program to harvest Memorie della Società Astronomica Italiana
# FS 2023-04-26

import sys
import os
import ejlmod3
import re
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup

publisher = 'Societa Astronomica Italiana'

tc = 'C'
tocurl = sys.argv[1]
jnl = 'Mem.Soc.Ast.It.'

tocpage = BeautifulSoup(urllib.request.urlopen(tocurl), features='lxml')
for p in tocpage.body.find_all('p', attrs = {'class' : 'has-text-align-center'}):
    pt = p.text.strip()
    vol = re.sub('.*olume *(\d+).*', r'\1', pt)
    isu = re.sub('.*olume .*?n\D*(\d[0-9\-]*).*', r'\1', pt)
    year = re.sub('.*([12]\d\d\d).*', r'\1', pt)
jnlfilename = 'msait%s.%s' % (vol, isu)
if len(sys.argv) > 2: 
    cnum = sys.argv[2]
    jnlfilename += '_%s' % (cnum)

recs = []
for table in tocpage.body.find_all('table'):
    trs = table.find_all('tr')
    rec = {'jnl' : jnl, 'vol' : vol, 'issue' : isu, 'tc' : tc, 'year' : year, 'auts' : []}
    if len(sys.argv) > 2: 
        rec['cnum'] = cnum
    if len(trs) == 3:
        authors = re.sub(',? et al\.', '', trs[0].text.strip())
        authors = re.sub(' (&amp;|and),?', ',', authors)
        authors = re.sub(' &,?', ',', authors)
        for author in re.split(', ', authors):
            rec['auts'].append(author)
        rec['tit'] = trs[1].text.strip()
        for a in trs[2].find_all('a'):
            rec['hidden'] = a['href']
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        print(table)
 
ejlmod3.writenewXML(recs, publisher, jnlfilename)
