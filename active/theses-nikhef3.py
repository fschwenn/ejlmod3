# -*- coding: utf-8 -*-
#program to harvest theses from NIKHEF
# FS 2018-02-26
# FS 2023-02-01

import sys
import os
import ejlmod3
import re
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import time 

publisher = 'NIKHEF'
years = 2
jnlfilename = 'THESES-NIKHEF-%s' % (ejlmod3.stampoftoday())
skipalreadyharvested = True

tocurl = 'https://www.nikhef.nl/pub/services/newbiblio/theses.php'
print(tocurl)

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

try:
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
    time.sleep(3)
except:
    print("retry %s in 180 seconds" % (tocurl))
    time.sleep(180)
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")

for fieldset in tocpage.body.find_all('fieldset'):
    fieldset.replace_with('')

recs = []
divs = tocpage.body.find_all('div', attrs = {'id' : 'main'})
for (i, div) in enumerate(divs):
    for child in div.children:
        try:
            child.name
        except:
            continue
        if child.name == 'dt':
            i += 1
            ejlmod3.printprogress('-', [[i+1, len(divs)]])
            rec = {'tc' : 'T', 'auts' : [ child.text.strip() ], 'jnl' : 'BOOK'}
        elif child.name == 'dd':
            ct = re.sub('^\n', '', re.sub('\n$', '', child.text.strip()))            
            parts = re.split('\n', child.text.strip())
            for a in child.find_all('a'):
                rec['tit'] = a.text.strip()
                rec['link'] = a['href']
                rec['doi'] = '20.2000/' + re.sub('.*\/', '', rec['link']) + '_' + re.sub('\W', '', rec['auts'][0])
                if re.search('pdf$', rec['link']):
                    rec['FFT'] = a['href']
            if len(parts) > 1:
                rec['date'] = re.sub('Okt', 'Oct', re.sub('\.', '', parts[-1]))
                if re.search('20\d\d', rec['date']):
                    year = int(re.sub('.*(20\d\d).*', r'\1', rec['date']))
                    if year > ejlmod3.year(backwards=years):
                        if skipalreadyharvested and rec['doi'] in alreadyharvested:
                            print('  already in backup')
                        else:
                            ejlmod3.printrecsummary(rec)
                            recs.append(rec)
                    else:
                        print('  too old')
                elif re.search('19\d\d', rec['date']):
                    year = int(re.sub('.*(19\d\d).*', r'\1', rec['date']))
                    print('  too old')
                else:
                    print(rec['tit'])
                    print(' problematic date', rec['date'], '\n')
                
ejlmod3.writenewXML(recs, publisher, jnlfilename)
