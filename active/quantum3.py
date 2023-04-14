# -*- coding: utf-8 -*-
#program to harvest Journal "Quantum"
# FS 2020-11-20
# FS 2023-04-12

import sys
import os
import ejlmod3
import re
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import time

skipalreadyharvested = True

regexpref = re.compile('[\n\r\t]')

publisher = 'Verein zur Foerderung des Open Access Publizierens in den Quantenwissenschaften'
vol = sys.argv[1]
jnlfilename = 'quantum%s_%s' % (vol, ejlmod3.stampoftoday())

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

urltrunk = 'https://quantum-journal.org/volumes/%s/' % (vol)
print(urltrunk)
try:
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(urltrunk), features="lxml")
    time.sleep(3)
except:
    print("retry %s in 180 seconds" % (urltrunk))
    time.sleep(180)
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(urltrunk), features="lxml")


prerecs = []
for div in tocpage.body.find_all('div', attrs = {'class' : 'list-article-content'}):
    for h2 in div.find_all('h2'):
        for a in h2.find_all('a'):
            rec = {'jnl' : 'Quantum', 'tc' : 'P', 'autaff' : [], 'vol' : vol, 'refs' : []}
            rec['artlink'] = a['href']
            prerecs.append(rec)

i = 0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        time.sleep(3)
    except:
        print("retry %s in 180 seconds" % (artlink))
        time.sleep(180)
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
    ejlmod3.globallicensesearch(rec, artpage)
    ejlmod3.metatagcheck(rec, artpage, ['citation_title', 'citation_author', 'citation_author_institution',
                                        'citation_firstpage', 'citation_doi', 'citation_arxiv_id',
                                        'citation_reference', 'dc.date', 'citation_pdf_url'])
    #abstract
    for p in artpage.body.find_all('p', attrs = {'class' : 'abstract'}):
        rec['abs'] = p.text.strip()
    #references
    for refs in artpage.body.find_all('div', attrs = {'id' : 'references'}):
        rec['refs'] = []
        for p in refs.find_all('p', attrs = {'class' : 'break'}):
            x = p.text.strip()
            rdoi = ''
            for a in p.find_all('a'):
                if a.has_attr('href') and re.search('doi.org\/10', a['href']):
                    rdoi = re.sub('.*doi.org\/', 'doi:', a['href'])
            if rdoi:
                if re.search('^\[\d+\]', x):
                    o = re.sub('.(\d+).*', r'\1', x)
                    rec['refs'].append([('o', o), ('a', rdoi), ('x', x)])
                else:
                    rec['refs'].append([('a', rdoi), ('x', x)])
            else:
                rec['refs'].append([('x', p.text)])
    if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
 
ejlmod3.writenewXML(recs, publisher, jnlfilename)
