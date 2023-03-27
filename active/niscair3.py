# -*- coding: utf-8 -*-
#program to harvest Niscair online Periodicals Repository
# FS 2018-09-14

import sys
import os
import ejlmod3
import re
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import time
import ssl



tmpdir = '/tmp'
regexpref = re.compile('[\n\r\t]')

publisher = 'Niscair'
typecode = 'P'
vol = sys.argv[1]
issue = sys.argv[2]
tocurl = sys.argv[3]

jnl = 'ijpap'
jnlname = 'Indian J.Pure Appl.Phys.'
jnlfilename = jnl+vol+'.'+issue

#bad certificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
hdr = {'User-Agent' : 'Magic Browser'}

try:
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
    time.sleep(3)
except:
    print("retry %s in 180 seconds" % (tocurl))
    time.sleep(180)
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features='lxml')


recs = []
for tr in tocpage.body.find_all('tr'):
    for td in tr.find_all('td', attrs = {'headers' : 't1'}):
        for a in td.find_all('a'):
            rec = {'jnl' : jnlname, 'vol' : vol, 'issue' : issue,
                   'auts' : [],
                   'licence' : {'statement' : 'CC-BY-NC-ND-2.5'},
                   'tc' : typecode, 'tit' : a.text.strip()}
            rec['doi'] = '20.2000/Niscair/' + re.sub('.*handle\/', '', a['href'])
            rec['artlink'] = 'http://nopr.niscair.res.in' + a['href']
            for td in tr.find_all('td', attrs = {'headers' : 't4'}):
                pages = re.split(' *\- *', td.text.strip())
                rec['p1'] = pages[0]
                if len(pages) > 1:
                    rec['p2'] = pages[1]    
                recs.append(rec)

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['artlink']]])
    try:
        req = urllib.request.Request(rec['artlink'], headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        time.sleep(3)
    except:
        print("retry %s in 180 seconds" % (rec['artlink']))
        time.sleep(180)
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features='lxml')
    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'citation_date', 'citation_pdf_url'])
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'citation_keywords'}):
        cont = re.sub('[\n\t]', ' ', meta['content'])
        cont = re.sub('&lt;.*?&gt;', '', re.sub('<.*?>', '', cont))
        rec['keyw'] = re.split(' *; ', cont)
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'DCTERMS.abstract'}):
        cont = re.sub('[\n\t]', ' ', meta['content'])
        cont = re.sub('&lt;.*?&gt;', '', re.sub('<.*?>', '', cont))
        rec['abs'] = cont
    ejlmod3.printrecsummary(rec)

 
ejlmod3.writenewXML(recs, publisher, jnlfilename)
