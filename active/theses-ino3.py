# -*- coding: utf-8 -*-
#harvest theses from INO
#FS: 2019-11-13
#FS: 2023-03-19


import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'INO'
jnlfilename = 'THESES-INO-%s' % (ejlmod3.stampoftoday())

skipalreadyharvested = True

tocurl = 'http://www.ino.tifr.res.in/ino/inoTheses.php'

print(tocurl)

hdr = {'User-Agent' : 'Magic Browser'}
req = urllib.request.Request(tocurl, headers=hdr)
tocpage = BeautifulSoup(urllib.request.urlopen(req))
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

recs = []
for tr in tocpage.body.find_all('tr'):
    rec = {'tc' : 'T',  'jnl' : 'BOOK'}
    tds = tr.find_all('td')
    if len(tds) == 3:
        #date
        if re.search('\d\d\d\d', tds[0].text):
            rec['date'] = re.sub('.*(\d\d\d\d).*', r'\1', tds[0].text.strip())
        #author
        for strong in tds[1].find_all('strong'):
            rec['autaff'] = [[ strong.text.strip() ]]
            strong.replace_with('')
        #title, supervisor, aff
        tdt = re.split(' *Supervisor: *', tds[1].text.strip())
        rec['tit'] = tdt[0]
        supervisor = re.sub(' *\(.*', '', tdt[1])
        supervisor = re.sub('(Dr|Prof)\. ', '', supervisor)
        if re.search('\(', tdt[1]):
            aff = re.sub('.*\( *(.*?) *\).*', r'\1', tdt[1])
            rec['supervisor'] = [[ supervisor, aff ]]
            rec['autaff'][0].append(aff)
        else:
            rec['supervisor'] = [[ supervisor ]]
        #pdf
        for a in tds[2].find_all('a'):
            rec['FFT'] = 'http://www.ino.tifr.res.in/ino/' + a['href']
            rec['link'] = 'http://www.ino.tifr.res.in/ino/' + a['href']
            rec['doi'] = '20.2000/' + a['href'][:-4]
        if not skipalreadyharvested or not 'doi' in rec or not rec['doi'] in alreadyharvested:
            recs.append(rec)
            ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
