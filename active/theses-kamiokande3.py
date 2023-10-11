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
tocurl = 'https://www-sk.icrr.u-tokyo.ac.jp/en/sk/for-reseacher/'
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
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")

for div in tocpage.find_all('div', attrs = {'id' : 'doctor'}):
    for ul in div.find_all('li', attrs = {'class' : 'paperList__thesisList__item'}):
        year = False
        keepit = True
        for p in ul.find_all('p', attrs = {'class' : 'paperList__year'}):
            pt = re.sub('[\n\t\r]', ' ', p.text.strip())
            if re.search('^\d+$', pt):
                year = int(pt)
                if year <= ejlmod3.year(backwards=years):
                    print(year, 'too old')
                    keepit = False
        if keepit:
            for li in ul.find_all('li', attrs = {'class' : 'list__dotList__item'}):
                rec = {'tc' : 'T', 'jnl' : 'BOOK'}
                if year:
                    rec['year'] = year
                for a in li.find_all('a'):
                    if re.search('pdf$', a['href']):
                        rec['link'] = 'http://www-sk.icrr.u-tokyo.ac.jp' + a['href']
                        rec['hidden'] = 'http://www-sk.icrr.u-tokyo.ac.jp' + a['href']
                        rec['doi'] = '20.2000/KAMIOKANDE/' + re.sub('\W', '', a['href'][17:-4])
                    a.decompose()
                for p in li.find_all('p', attrs = {'class' : 'paperList__read'}):
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
                if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
                    recs.append(rec)
                    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
