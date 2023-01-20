# -*- coding: utf-8 -*-
#harvest BELLE theses
#FS: 2018-01-31
#FS: 2023-01-20

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'BELLE'

jnlfilename = 'THESES-BELLE-%s' % (ejlmod3.stampoftoday())

recs = []

#server1
tocurl = 'http://belle.kek.jp/bdocs/theses.html'
#not valid html :(

#server2
tocurl = 'http://docs.belle2.org/search?ln=en&cc=PhD+Theses&p=&f=&action_search=Search&c=PhD+Theses&c=&sf=&so=d&rm=&rg=25&sc=1&of=xm'
try:
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
    time.sleep(3)
except:
    print("retry %s in 180 seconds" % (tocurl))
    time.sleep(180)
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")

for record in tocpage.find_all('record'):
    rec = {'tc' : 'T', 'jnl' : 'BOOK', 'MARC' : [], 'supervisor' : []}
    for df in record.find_all('datafield', attrs = {'tag' : '037'}):
        for sf in df.find_all('subfield', attrs = {'code' : 'a'}):
            rec['MARC'].append(('037', [('a', sf.text)]))
    for df in record.find_all('datafield', attrs = {'tag' : '100'}):
        for sf in df.find_all('subfield', attrs = {'code' : 'a'}):
            rec['auts'] = [ sf.text ]
    for df in record.find_all('datafield', attrs = {'tag' : '700'}):
        for sf in df.find_all('subfield', attrs = {'code' : 'a'}):
            rec['supervisor'] = [ sf.text ]
    for df in record.find_all('datafield', attrs = {'tag' : '245'}):
        for sf in df.find_all('subfield', attrs = {'code' : 'a'}):
            rec['tit'] = sf.text
    for df in record.find_all('datafield', attrs = {'tag' : '300'}):
        for sf in df.find_all('subfield', attrs = {'code' : 'a'}):
            if re.search('^\d+$', sf.text.strip()):
                         rec['pages'] = sf.text.strip()
    for df in record.find_all('datafield', attrs = {'tag' : '520'}):
        for sf in df.find_all('subfield', attrs = {'code' : 'a'}):
            rec['abs'] = sf.text
    for df in record.find_all('datafield', attrs = {'tag' : '856'}):
        for sf in df.find_all('subfield', attrs = {'code' : 'u'}):
            rec['FFT'] = re.sub('\?.*', '', sf.text)
            rec['link'] = re.sub('\/files.*', '', sf.text)
            rec['doi'] = '20.2000/BELLE/' + re.sub('\W', '', rec['link'])
    for df in record.find_all('datafield', attrs = {'tag' : '260'}):
        for sf in df.find_all('subfield', attrs = {'code' : 'b'}):
            rec['aff'] = [ sf.text ]
        for sf in df.find_all('subfield', attrs = {'code' : 'c'}):
            rec['date'] = sf.text
            year = int(re.sub('.*(20\d\d).*', r'\1', rec['date']))
            if year >= ejlmod3.year() - 1:
                recs.append(rec)
                ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
