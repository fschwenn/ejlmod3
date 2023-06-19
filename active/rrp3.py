# -*- coding: UTF-8 -*-
#program to harvest Romanian Reports in Physics
# FS 2017-06-27
# FS 2023-06-19

import os
import ejlmod3
import re
import sys
#import unicodedata
#import string
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import ssl

publisher = 'Romanian Academy Publishing House'
year = sys.argv[1]
vol = sys.argv[2]
issue = sys.argv[3]

jnl = 'rrp'
jnlname = 'Rom.Rep.Phys.'

jnlfilename = '%s%s.%s' % (jnl, vol, issue)

url = 'https://rrp.nipne.ro/%s_%s_%s.html' % (year, vol, issue)

#bad certificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
hdr = {'User-Agent' : 'Magic Browser'}

print("get table of content of %s%s.%s ... via %s" %(jnlname, vol, issue, url))
req = urllib.request.Request(url, headers=hdr)
tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")


tsection = ''
recs = []
done = []
for table in tocpage.body.find_all('table', attrs = {'dwcopytype' : 'CopyTableRow'}):
    for tr in table.find_all('tr'):
        for font in tr.find_all('font', attrs = {'color' : '#ff0000'}):
            fonttext = font.text.strip()
            if fonttext:
                tsection = fonttext
        for b in tr.find_all('b', attrs = {'class' : 'tocTitle'}):
            rec = {'jnl' : jnlname, 'vol' : vol, 'issue' : issue, 'year' : year,
                   'tc' : 'P', 'note' : [tsection], 'auts' : []}
            rec['tit'] = b.text.strip()
        for div in tr.find_all('div'):
            for i1 in div.find_all('i'):
                i1.replace_with('')
                rec['abs'] = re.sub('[\n\t\r ]+', ' ', div.text.strip())
        for i2 in tr.find_all('i', attrs = {'class' : 'tocAuth'}):
            authors = i2.text.strip()
            for author in re.split(' *, *', authors):
                rec['auts'].append(re.sub('(.*) (.*)', r'\2, \1', author))
        for td in tr.find_all('td', attrs = {'width' : '60%'}):
            for a in td.find_all('a'):
                rec['pdf'] = 'https://rrp.nipne.ro/' + re.sub('^\.\/', '', a['href'])
                rec['hidden'] = rec['pdf']
                rec['p1'] = re.sub('.*? (\d+).*', r'\1', re.sub('[\n\t\r]', '', td.text.strip()))
                if rec['p1'] not in done:
                    recs.append(rec)
                    done.append(rec['p1'])
                    ejlmod3.printrecsummary(rec)


ejlmod3.writenewXML(recs, publisher, jnlfilename)
