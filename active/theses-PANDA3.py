# -*- coding: utf-8 -*-
#harvest theses from PANDA
#FS: 2018-02-16
#FS: 2023-05-19

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import ssl

skipalreadyharvested = True

publisher = 'PANDA'
jnlfilename = 'THESES-PANDA-%s' % (ejlmod3.stampoftoday())

tocurl = 'https://panda.gsi.de/panda-publications/thesis-th'

#bad cerificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

try:
    tocpage = BeautifulSoup(urllib.request.urlopen(tocurl, context=ctx))
    time.sleep(3)
except:
    print("retry %s in 180 seconds" % (tocurl))
    time.sleep(180)
    tocpage = BeautifulSoup(urllib.request.urlopen(tocurl, context=ctx), features='lxml')

recs = []
for div in tocpage.body.find_all('div', attrs = {'role' : 'article'}):
    rec = {'tc' : 'T', 'jnl' : 'BOOK', 'exp' : 'GSI-FAIR-PANDA', 'keyw' : []}
    for d2 in div.find_all('div', attrs = {'property' : 'dc:title'}):
        rec['rn'] = [ d2.text.strip() ]
        rec['doi'] = '20.2000/PANDA/' + d2.text.strip()
    for section in div.find_all('section', attrs = {'class' : 'field field-name-field-publication-title field-type-text field-label-above view-mode-teaser'}):
        for d2 in section.find_all('div', attrs = {'class' : 'field-items'}):
            rec['tit'] = d2.text.strip()
    for section in div.find_all('section', attrs = {'class' : 'field field-name-field-publication-author field-type-text field-label-above view-mode-teaser'}):
        for d2 in section.find_all('div', attrs = {'class' : 'field-items'}):
            rec['auts'] = [ d2.text.strip() ]
    for section in div.find_all('section', attrs = {'class' : 'field field-name-field-file-upload field-type-file field-label-above view-mode-teaser'}):
        for a in section.find_all('a'):
            rec['link'] = a['href']
            if re.search('pdf$',  a['href']):
                rec['FFT'] = a['href']
    for section in div.find_all('section', attrs = {'class' : 'field field-name-field-publication-classification field-type-taxonomy-term-reference field-label-above view-mode-teaser'}):
        for li in section.find_all('li'):
            rec['keyw'].append(li.text.strip())
    for section in div.find_all('section', attrs = {'class' : 'field field-name-field-publication-date field-type-datetime field-label-above view-mode-teaser'}):
        for span in section.find_all('span'):
            rec['date'] = span['content'][:10] 
    for section in div.find_all('section', attrs = {'class' : 'field field-name-field-publication-abstract field-type-text-long field-label-above view-mode-teaser'}):
        for d2 in section.find_all('div', attrs = {'class' : 'field-items'}):
            rec['abs'] = re.sub('[\r\n\t]', ' ', d2.text.strip())
    if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
        recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
