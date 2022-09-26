# -*- coding: utf-8 -*-
# program to harvest Journal of Fundamental and Applied Research (JFAR)
#FS: 2022-09-23

import sys
import os
import ejlmod3
import re
import urllib.request, urllib.error, urllib.parse
import codecs
from bs4 import BeautifulSoup
import time
import ssl


publisher = 'National Research University "Tashkent Institute of Irrigation and Agricultural Mechanization Engineers"'
year = sys.argv[1]
issue = sys.argv[2]
jnlfilename = 'jfar%s.%s' % (year, issue)

tocurl = 'https://www.jfar.uz/volumes/%s/%s/' % (year, issue)
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
hdr = {'User-Agent' : 'Magic Browser'}
try:
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
except:
    print("retry %s in 180 seconds" % (tocurl))
    time.sleep(180)
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")

for div in tocpage.body.find_all('div', attrs = {'class' : 'card-footer'}):
    note = div.text.strip()
recs = []
for div in tocpage.body.find_all('div', attrs = {'class' : 'card'}):
    rec = {'jnl' : 'J.Fund.Appl.Res.', 'tc' : 'P', 
           'year' : year, 'issue' : issue, 'note' : [note]}
    rec['note'].append('correct article IDs need to be taken from the PDF !')
    #volume
    rec['vol'] = str(int(year)-2020)
    #title
    for h5 in div.find_all('h5'):
        rec['tit'] = re.sub('[\n\t\r]', ' ', h5.text.strip())
    #authors  
    for h6 in div.find_all('h6'):
        rec['auts'] = re.split(', ', re.sub('[\n\t\r]', ' ', h6.text.strip()))
    #abstract
    for p in div.find_all('p', attrs = {'class' : 'card-text'}):
        rec['abs'] = p.text.strip()
    #fulltext, article ID
    for a in div.find_all('a'):
        if a.has_attr('href') and re.search('\.pdf$', a['href']):
            rec['FFT'] = tocurl + a['href']
            rec['link'] = tocurl + a['href']
            rec['p1'] = re.sub('\D', '', a['href'])
    if not re.search('^Issue \d+$', rec['tit']):
        recs.append(rec)
        ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
