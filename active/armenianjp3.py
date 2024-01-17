# -*- coding: UTF-8 -*-
#program to harvest ARMENIAN JOURNAL OF PHYSICS
# FS 2019-12-13
# FS 2023-05-30

import os
import ejlmod3
import re
import sys
#import unicodedata
#import string
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import time
import ssl

publisher = 'National Academy of Sciences of Armenia'
jnl = 'armjp'
vol = sys.argv[1]
issue = sys.argv[2]
year = str(int(vol)+2007)

jnlfilename = '%s%s.%s' % (jnl, vol, issue)
jnlname = 'Armenian J.Phys.'
issn = "1829-1171"


urltrunk = 'http://www.flib.sci.am/eng/journal/Phys'
urltrunk = 'https://www.flib.sci.am/journal/arm/Phys'
tocurl = '%s/PV%sIss%s.html' % (urltrunk, vol, issue)
tocurl = '%s/%i_%s.html' % (urltrunk, int(vol)+2007, issue)



#bad certificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

hdr = {'User-Agent' : 'Magic Browser'}
print("get table of content of %s %s,  No. %s via %s ..." % (jnlname, vol, issue, tocurl))
req = urllib.request.Request(tocurl, headers=hdr)
tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
time.sleep(1)
recs = []
for tr in tocpage.body.find_all('tr'):
    rec = {'year' : year, 'vol' : vol, 'keyw' : [],
           'issue' : issue, 'jnl' : jnlname, 'note' : [], 'tc' : "P"}
    for a in tr.find_all('a'):
        if a.has_attr('href'):
            rec['artlink'] = a['href']
            recs.append(rec)

if not recs:
    for a in tocpage.body.find_all('a'):
        if a.has_attr('href') and re.search('publication\/\d+', a['href']):
             rec = {'year' : year, 'vol' : vol, 'keyw' : [],
                    'issue' : issue, 'jnl' : jnlname, 'note' : [], 'tc' : "P"}
             rec['artlink'] = a['href']
             recs.append(rec)

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['artlink']]])
    req = urllib.request.Request(rec['artlink'])
    artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
    time.sleep(3)
    #license
    for a in artpage.find_all('a'):
        if a.has_attr('href') and re.search('creativecommons.org', a['href']):
            rec['license'] = {'url' : re.sub('\/legalcode$', '', a['href'])}
    ejlmod3.metatagcheck(rec, artpage, ['eprints.creators_name', 'DC.creator', 'DC.date', 'citation_online_date',
                                        'eprints.abstract', 'DC.description', 'DC.subject', 'citation_title',
                                        'eprints.document_url', 'citation_pdf_url', 'DC.identifier', 'DC.title'])
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #pages
            if meta['name'] in ['eprints.pagerange', 'DC.coverage']:
                rec['p1'] = re.sub('\-.*', '', meta['content'])
                rec['p2'] = re.sub('.*\-', '', meta['content'])
    #keywords
    for a in  artpage.body.find_all('a', attrs = {'class' : 'object__keyword'}):
        rec['keyw'].append(a.text.strip())
    if not 'doi' in list(rec.keys()):
        rec['link'] = rec['artlink']
        rec['doi'] = '20.2000/ArmenianJPhysics/' + re.sub('\D', '', rec['artlink'])
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
