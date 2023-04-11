# -*- coding: utf-8 -*-
#harvest theses from Cracow
#FS: 2019-12-05
#FS: 2023-04-08

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Jagiellonian U. (main)'
jnlfilename = 'THESES-CRACOW-%s' % (ejlmod3.stampoftoday())

years = [str(ejlmod3.year(backwards=1)), str(ejlmod3.year())]
skipalreadyharvested = True

hdr = {'User-Agent' : 'Magic Browser'}

tocurl = 'https://fais.uj.edu.pl/dla-studentow/studia-doktoranckie/prace-doktorskie'
req = urllib.request.Request(tocurl, headers=hdr)
tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

recs = []
for div in tocpage.find_all('div', attrs = {'class' : 'post-folded__nav'}):
    for h3 in div.find_all('h3'):
        for span in h3.find_all('button'):
            year = span.text.strip()
            ejlmod3.printprogress("-", [[year]])
    if year in years:
        for tr in div.find_all('tr'):
            rec = {'tc' : 'T', 'year' : year, 'date' : year, 'jnl' : 'BOOK',
                   'note' : ['Vorsicht! Keine Abstracts vorhanden!']}
            tds = tr.find_all('td')
            if len(tds) == 3:
                for a in tds[1].find_all('a'):
                    if re.search('http', a['href']):
                        rec['FFT'] = re.sub('\.pdf\/.*', '.pdf', a['href'])
                    else:
                        rec['FFT'] = 'https://fais.uj.edu.pl' + re.sub('\.pdf\/.*', '.pdf', a['href'])
                    rec['doi'] = '20.2000/cracow/' + re.sub('\W', '', re.sub('.*documents', '', a['href']))
                    rec['link'] = rec['FFT']
                    rec['tit'] = a.text.strip()
                    rec['autaff'] = [[tds[0].text.strip(), publisher]]
                    if re.search('PL', tds[2].text):
                        rec['language'] = 'polish'
                    if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
                        recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
