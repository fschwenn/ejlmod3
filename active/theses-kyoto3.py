# -*- coding: utf-8 -*-
#harvest theses from University of Kyoto
#FS: 2019-09-27
#FS: 2023-04-29

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import json
import ssl

publisher = 'Kyoto U.'
jnlfilename = 'THESES-KYOTO-%s' % (ejlmod3.stampoftoday())
skipalreadyharvested = True

#bad certificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
hdr = {'User-Agent' : 'Magic Browser'}

tocurl = 'https://www-he.scphys.kyoto-u.ac.jp/theses/index.html'
print(tocurl)

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

req = urllib.request.Request(tocurl, headers=hdr)
tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
recs = []
table = tocpage.body.find_all('table')[0]
for thead in table.find_all('thead'):
    thead.replace_with('')
for tr in table.find_all('tr'):
    rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK'}
    tds = tr.find_all('td')
    i = len(tds)-3
    rec['autaff'] = [[tds[i].text.strip(), 'Kyoto U.']]
    rec['tit'] = re.sub('[\n\t]', ' ', tds[1+i].text.strip())
    for a in tds[1+i].find_all('a'):
        rec['link'] = 'https://www-he.scphys.kyoto-u.ac.jp/theses/' + a['href'][2:]
        rec['FFT'] = 'https://www-he.scphys.kyoto-u.ac.jp/theses/' + a['href'][2:]
        rec['doi'] = '20.2000/KYOTO/' + re.sub('\W', '', a['href'])
    rec['date'] = tds[2+i].text.strip()
    if 'doi' in rec:
        if skipalreadyharvested and rec['doi'] in alreadyharvested:
            print('  %s already in backup' % (rec['doi']))
        else:        
            recs.append(rec)
            ejlmod3.printrecsummary(rec)
    else:
        print(tr)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
