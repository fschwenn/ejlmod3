# -*- coding: utf-8 -*-
#!/usr/bin/python
#program to harvest CCSENET
# FS 2018-10-30
# FS 2022-11-25

import os
import ejlmod3
import re
import sys
import urllib.request, urllib.error, urllib.parse
import time
from bs4 import BeautifulSoup

def tfstrip(x): return x.strip()

publisher = 'Canadian Center of Science and Education'
jnl = sys.argv[1]
vol = sys.argv[2]
isu = sys.argv[3]

if   (jnl == 'apr'): 
    jnlname = 'Appl.Phys.Res.'
    issn = '1916-9639'
elif (jnl == 'jmr'):
    jnlname = 'J.Math.Res.'
    issn = '1916-9795'

jnlfilename = jnl+vol+'.'+isu
tc = 'P'

archiveslink = 'http://www.ccsenet.org/journal/index.php/%s/issue/archives' % (jnl)


print('[archive] %s' % (archiveslink))
arcpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(archiveslink), features="lxml")
toclink = False
otherlinks = []
for li in arcpage.body.find_all('li'):
    for a in li.find_all('a'):
        at = a.text.strip()
        if re.search('Vol. %s, No. %s$' % (vol, isu), at):
            toclink = a['href']
        elif re.search('Vol. \d', at):
            otherlinks.append(at)

if not toclink:
    print('TOC link for this issue not found')
    print('found only:', otherlinks)
    sys.exit(0)

print('[TOC] %s' % (toclink))
tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(toclink), features="lxml")
recs = []
for li in tocpage.body.find_all('li', attrs = {'class' : 'h5'}):
    for a in li.find_all('a'):
        artlink = a['href']
        print('[ART] %s' % (artlink))
        rec = {'vol' : vol, 'issue' : isu, 'jnl' : jnlname, 'tc' : tc,
               'auts' : []}
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(artlink), features="lxml")
        ejlmod3.metatagcheck(rec, artpage, ['DC.Date.issued', 'DC.Description', 'DC.Identifier.pageNumber', 'DC.Identifier.DOI',
                                            'DC.Rights', 'DC.Title', 'citation_author', 'citation_firstpage',
                                            'citation_lastpage', 'citation_pdf_url'])
        recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
