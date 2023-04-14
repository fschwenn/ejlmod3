# -*- coding: utf-8 -*-
#harvest theses from Bohr Institute
#FS: 2020-11-09
#FS: 2023-04-13

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

startyear = ejlmod3.year(backwards=1)
skipalreadyharvested = True

publisher = 'Bohr Inst.'
jnlfilename = 'THESES-BOHR-%s' % (ejlmod3.stampoftoday())

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
hdr = {'User-Agent' : 'Magic Browser'}
recs = []
tocurl = 'https://www.nbi.ku.dk/english/theses/phd-theses/'
ejlmod3.printprogress("=", [[tocurl]])
req = urllib.request.Request(tocurl, headers=hdr)
tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
time.sleep(2)
for article in tocpage.find_all('article', attrs = {'class' : 'tilebox'}):
    #print(article)
    rec = {'tc' : 'T', 'jnl' : 'BOOK', 'note' : []}
    for h2 in article.find_all('h3'):
        rec['autaff'] = [[ h2.text.strip(), publisher ]]
    for a in article.find_all('a'):
        rec['link'] = 'https://www.nbi.ku.dk' + a['href']
        rec['doi'] = '20.2000/NielsBohrInst/' + re.sub('\W', '', a['href'][26:])
    for div in article.find_all('div', attrs = {'class' : 'date'}):
        rec['date'] = re.sub('\.', '-', div.text.strip())
        rec['year'] = rec['date'][:4]
        if int(rec['year']) >= startyear:
            if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
                recs.append(rec)

j = 0
for rec in recs:
    j += 1
    ejlmod3.printprogress("-", [[j, len(recs)], [rec['link']]])
    try:
        req = urllib.request.Request(rec['link'])
        artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        time.sleep(2)
    except:
        print('wait 10 minutes')
        time.sleep(600)
        try:
            req = urllib.request.Request(rec['link'])
            artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
            time.sleep(30)
        except:
            continue
    for p in artpage.find_all('p'):
        for strong in p.find_all('strong'):
            st = strong.text.strip()
            strong.decompose()
            #title and PDF
            if re.search('[pP]\.?h\.? *[dD]', st):
                for a in p.find_all('a'):
                    at = a.text.strip()
                    if len(at) > 5:
                        rec['hidden'] = 'https://www.nbi.ku.dk' + a['href']
                        rec['tit'] = at
                if not 'tit' in list(rec.keys()):
                    rec['tit'] = p.text.strip()
            #supervisor
            elif st in ['Supervisors:', 'Supervisor:', 'Primary Supervisor:']:
                rec['supervisor'] = [[ re.sub('[Pp]rof\. *', '', re.sub('Dr\. *', '', p.text.strip())) ]]
    ejlmod3.printrecsummary(rec)
    if not 'tit' in list(rec.keys()):
        for meta in artpage.find_all('meta', attrs = {'name' : 'DC.Description'}):
            rec['tit'] = meta['content']

ejlmod3.writenewXML(recs, publisher, jnlfilename)
