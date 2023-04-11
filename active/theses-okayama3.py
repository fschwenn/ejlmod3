# -*- coding: utf-8 -*-
#harvest theses from Okayama U.
#FS: 2020-08-31
#FS: 2023-04-11

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Okayama U.'
jnlfilename = 'THESES-OKAYAMA_U-%s' % (ejlmod3.stampoftoday())

pages = 1
skipalreadyharvested = True
hdr = {'User-Agent' : 'Magic Browser'}

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

recs = []
#first get links of year pages
for degree in ['%E5%8D%9A%E5%A3%AB%EF%BC%88%E5%AD%A6%E8%A1%93%EF%BC%89', '%E5%8D%9A%E5%A3%AB%EF%BC%88%E7%90%86%E5%AD%A6%EF%BC%89']:
    for page in range(pages):
        tocurl = 'http://ousar.lib.okayama-u.ac.jp/en/list/thesis_types/%s/p/%i' % (degree, page+1)
        ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        for div in tocpage.body.find_all('div', attrs = {'class' : 'view-result-item'}):
            rec = {'tc' : 'T', 'jnl' : 'BOOK'}
            for div2 in div.find_all('div', attrs = {'class' : 'title'}):
                for a in div2.find_all('a'):
                    rec['link'] = 'http://ousar.lib.okayama-u.ac.jp' + a['href']
                    rec['tit'] = a.text.strip()
                    rec['doi'] = '20.2000/OKAYAMA/' + re.sub('\W', '', a['href'][21:])
            for tr in div.find_all('tr'):
                for th in tr.find_all('th'):
                    tht = th.text.strip()
                for td in tr.find_all('td'):
                    if tht == 'Author':
                        for span in td.find_all('span', attrs = {'class' : 'delim'}):
                            span.decompose()
                        rec['autaff'] = [[ td.text.strip(), publisher ]]
                    elif tht == 'Published Date':
                        rec['date'] = td.text.strip()
            if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
                recs.append(rec)
                ejlmod3.printrecsummary(rec)
        time.sleep(5)
    
ejlmod3.writenewXML(recs, publisher, jnlfilename)
