# -*- coding: utf-8 -*-
#harvest CLAS theses
#FS: 2018-01-29
#FS: 2023-01-20

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'CLAS'

jnlfilename = 'THESES-CLAS-%s' % (ejlmod3.stampoftoday())

tocurl = 'https://www.jlab.org/Hall-B/general/clas_thesis.html'

try:
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
    time.sleep(3)
except:
    print("retry %s in 180 seconds" % (tocurl))
    time.sleep(180)
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")

recs = []
for table in tocpage.body.find_all('table', attrs = {'class' : 'sortable'}):
    isnew = True
    for tbody in table.find_all('tbody'):
        for tr in tbody.find_all('tr'):
            tds = tr.find_all('td')
            if len(tds) == 8:
                rec = {'jnl' : 'BOOK', 'tc' : 'T', 'supervisor' : []}
                rec['date'] = re.sub('(.*) (.*)', r'\2 \1', tds[2].text.strip())
                inst = tds[3].text.strip()
                for sv in re.split(' *[&,] ', tds[4].text.strip()):
                    rec['supervisor'].append([sv])
                rec['autaff'] = [ [ '%s, %s' % (tds[1].text.strip(), tds[0].text.strip()), tds[3].text.strip() ] ]
                rec['tit'] = tds[5].text.strip()
                for a in tds[5].find_all('a'):
                    rec['link'] = 'https://www.jlab.org/Hall-B/general/' + a['href']
                    rec['FFT'] = 'https://www.jlab.org/Hall-B/general/' + a['href']
                    rec['doi'] = '20.2000/CLAS/' + re.sub('\W', '', a['href'])
                rawexperiment = tds[7].text.strip()
                if re.search('^E(\d+)\-(\d+)', rawexperiment):
                    exp = re.sub('^E\d?(\d\d)\-(\d+)', r'JLAB-E-\1-\2', rawexperiment)
                    #if search_pattern(p='980__a:EXPERIMENT 119__a:%s' % (exp)):
                    #    rec['exp'] = exp
                    rec['keyw'] = [exp]
                if re.search('20\d\d', rec['date']):
                    year = int(re.sub('.*(20\d\d).*', r'\1', rec['date']))
                elif re.search('19\d\d', rec['date']):
                    year = int(re.sub('.*(19\d\d).*', r'\1', rec['date']))
                if year >= ejlmod3.year() - 1:
                    recs.append(rec)
                    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
