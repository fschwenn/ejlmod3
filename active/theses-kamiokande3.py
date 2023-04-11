# -*- coding: utf-8 -*-
#harvest KAMIOKANDE theses
#FS: 2018-01-31
#FS: 2023-04-05

import sys
#import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
#import json

publisher = 'KAMIOKANDE'
jnlfilename = 'THESES-KAMIOKANDE-%s' % (ejlmod3.stampoftoday())

skipalreadyharvested = True
years = 2

recs = []

#server1
tocurl = 'http://www-sk.icrr.u-tokyo.ac.jp/sk/publications/index-e.html'
print(tocurl)

if skipalreadyharvested:    
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

hdr = {'User-Agent' : 'Magic Browser'}
try:
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req))
    time.sleep(3)
except:
    print("retry %s in 180 seconds" % (tocurl))
    time.sleep(180)
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl))

for p in tocpage.find_all('p'):
    pt = re.sub('[\n\t\r]', ' ', p.text.strip())
    if re.search('PhD', pt):
        rec = {'tc' : 'T', 'jnl' : 'BOOK'}
        for br in p.find_all('br'):
            br.replace_with(', ')
        for a in p.find_all('a'):
            if re.search('pdf$', a['href']):
                rec['link'] = 'http://www-sk.icrr.u-tokyo.ac.jp/sk' + a['href'][2:]
                rec['hidden'] = 'http://www-sk.icrr.u-tokyo.ac.jp/sk' + a['href'][2:]
                rec['doi'] = '20.2000/KAMIOKANDE/' + re.sub('\W', '', a['href'][16:-4])
            a.decompose()
        pt = re.sub('[\n\t\r]', ' ', p.text.strip())
        #print pt
        halfs = re.split(' *,? *PhD Thesis *,? *', pt)
        firstparts = re.split(' *, *', halfs[0])
        secondparts = re.split(' *, *', halfs[1])
        #print 'SP', secondparts
        if re.search('\d', secondparts[-1]):
            rec['date'] = re.sub('.*([12]\d\d\d).*', r'\1', secondparts[-1])
            rec['year'] = rec['date']
            rec['autaff'] = [[ firstparts[-1], ', '.join(secondparts[:-1]) ]]
        else:
            rec['date'] = re.sub('.*([12]\d\d\d).*', r'\1', secondparts[-2])
            rec['year'] = rec['date']
            rec['autaff'] = [[ firstparts[-1], ', '.join(secondparts[:-2]) ]]
        rec['tit'] = ', '.join(firstparts[:-1])
        if int(rec['year']) >= ejlmod3.year(backwards=2):
            if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
                recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
