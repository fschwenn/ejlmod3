# -*- coding: utf-8 -*-
#program to harvest ANNALES DE L'INSTITUT FOURIER
# FS 2019-10-22
# FS 2023-05-30

import sys
import os
import ejlmod3
import re
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import time

def tfstrip(x): return x.strip()
regexpref = re.compile('[\n\r\t]')

publisher = 'Annales de lInstitut Fourier'
vol = sys.argv[1]
iss = sys.argv[2]
year = str(int(vol) + 1950)
if iss == '7':
    typecode = 'C'
else:
    typecode = 'P'
jnlfilename = 'annif%s.%s' % (vol, iss)
tocurl = 'https://aif.centre-mersenne.org/issues/AIF_%s__%s_%s/' % (year, vol, iss)
print(tocurl)

try:
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features='lxml')
    time.sleep(10)
except:
    print("retry %s in 180 seconds" % (tocurl))
    time.sleep(180)
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features='lxml')

recs = []
for span in tocpage.body.find_all('span', attrs = {'class' : 'article-title'}):
    rec = {'jnl' : 'Annales Inst.Fourier', 'vol' : vol, 'issue' : iss, 'tc' : typecode, 
           'refs' : [], 'year' : year}
    for a in span.find_all('a'):
        rec['artlink'] = 'https://aif.centre-mersenne.org' + a['href']
        rec['tit'] = a.text.strip()
        recs.append(rec)

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}
i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['artlink']]])
    time.sleep(2)
    req = urllib.request.Request(rec['artlink'], headers=hdr)
    artpage = BeautifulSoup(urllib.request.urlopen(req), features='lxml')
    #artpage = BeautifulSoup(urllib2.build_opener(urllib2.HTTPCookieProcessor).open(rec['artlink']))
    ejlmod3.metatagcheck(rec, artpage, ['citation_firstpage', 'citation_lastpage', 'citation_pdf_url',
                                        'citation_author'])
    #abstract
    for div in artpage.body.find_all('div', attrs = {'id' : 'abstract-en'}):
        rec['abs'] = div.text.strip()
    #DOI and keywords and date
    for div in artpage.body.find_all('div', attrs = {'id' : 'info-tab'}):
        for a in div.find_all('a'):
            rec['doi'] = re.sub('.*org\/', '', a['href'])
        divt = re.sub('[\n\t\r]', ' ', div.text.strip())
        keywords = re.sub('.*Keywords: *', '', divt)
        rec['keyw'] = re.split(', ', keywords)
        if re.search('Published online', divt):
            rec['date'] = re.sub('.*Published online *: *([\d\-]+).*', r'\1', divt)
        elif re.search('Publi. le', divt):
            rec['date'] = re.sub('.*Publi. le *: *([\d\-]+).*', r'\1', divt)
    #references
    for p in artpage.body.find_all('p', attrs = {'class' : 'bibitemcls'}):
        doi = False
        for a in p.find_all('a'):
            if re.search('doi.org', a['href']):
                doi = re.sub('.*org\/', 'doi:', a['href'])
                a.replace_with('')
        pt = re.sub('[\n\t\r]', ' ', p.text.strip())
        if doi:
            nr = re.sub('^ *\[(\d+)\].*', r'\1', pt)
            rec['refs'].append([('o', nr), ('a', doi), ('x', pt)])
        else:
            rec['refs'].append([('x', pt)])
    #translated title
    for span in artpage.body.find_all('span', attrs = {'class' : 'article-trans-title'}):
        rec['language'] = 'french'
        rec['transtit'] = re.sub('.*?\[(.*)\].*', r'\1', span.text)
    #license
    if int(vol) >= 65:
        rec['license'] =  {'statement' : 'CC-BY-ND-3.0'}
    ejlmod3.printrecsummary(rec)
 
ejlmod3.writenewXML(recs, publisher, jnlfilename)
