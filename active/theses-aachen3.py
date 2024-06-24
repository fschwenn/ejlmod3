# -*- coding: utf-8 -*-
#harvest theses from RWTH Aachen U. 
#FS: 2019-12-13

import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

rg = '100'
years = 2
skipalreadyharvested = True

publisher = 'RWTH Aachen U.'
jnlfilename = 'THESES-AACHEN_%s' % (ejlmod3.stampoftoday())

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename, years=3)

hdr = {'User-Agent' : 'Magic Browser'}
recs = {}
for fachgruppe in ['130000', '110000']:
    tocurl = 'http://publications.rwth-aachen.de/search?ln=de&p=980__a%3Aphd+9201_k%3A' + fachgruppe + '&f=&action_search=Suchen&c=RWTH+Publications&sf=&so=d&rm=&rg=' + rg + '&sc=1&of=xd'
    print(tocurl)
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    time.sleep(5)
    for oai in tocpage.find_all('oai_dc:dc'):
        rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'supervisor' : [], 'note' : [ fachgruppe ]}
        #title
        for dc in oai.find_all('dc:title'):
            rec['tit'] = dc.text
        #language
        for dc in oai.find_all('dc:language'):
            rec['language'] = dc.text
        #keywords
        for dc in oai.find_all('dc:subject'):
            if re.search('\/ddc\/', dc.text):
                rec['note'].append(dc.text)
            else:
                rec['keyw'].append(dc.text)
        #author
        for dc in oai.find_all('dc:creator'):
            rec['autaff'] = [[ dc.text, publisher ]]
        #supervisor
        for dc in oai.find_all('dc:contributor'):
            rec['supervisor'].append([dc.text])
        #abstract
        for dc in oai.find_all('dc:description'):
            rec['abs'] = dc.text
        #date
        for dc in oai.find_all('dc:date'):
            rec['date'] = dc.text
            rec['year'] = re.sub('.*([12]\d\d\d).*', r'\1', rec['date'])
        #FFT
        for dc in oai.find_all('dc:rights'):
            if re.search('[oO]pen', dc.text):
                for dc2 in oai.find_all('dc:identifier'):
                    dc2t = dc2.text.strip()
                    if re.search('\.pdf$', dc2t):
                        rec['FFT'] = dc2t
        #DOI
        for dc in oai.find_all('dc:relation'):
            if re.search('10\.18154', dc.text):
                rec['doi'] = re.sub('.*(10\.18154.*)', r'\1', dc.text)
        #article link
        for dc in oai.find_all('dc:identifier'):
            dct = dc.text
            if re.search('http...publications.rwth.aachen.de.record.\d+', dct):
                rec['artlink'] = dct
            if not 'doi' in list(rec.keys()):
                rec['doi'] = re.sub('.*\/', '20.2000/AACHEN/', dct)
                rec['link'] = dct
        if int(rec['year']) > ejlmod3.year(backwards=years):
            recs[rec['doi']] = rec
        ejlmod3.printrecsummary(rec)

realrecs = []
for doi in recs:
    if not skipalreadyharvested or not doi in alreadyharvested:
        realrecs.append(recs[doi])
print(len(realrecs), '/', len(recs))

ejlmod3.writenewXML(realrecs, publisher, jnlfilename)

