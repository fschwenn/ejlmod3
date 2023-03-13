# -*- coding: utf-8 -*-
#harvest theses from Brasilia U.
#FS: 2022-07-22

import urllib.request, urllib.error, urllib.parse
import urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time


publisher = 'Brasilia U.'
jnlfilename = 'THESES-BRASILIA-%s' % (ejlmod3.stampoftoday())
rpp = 20
numofpages = 1
skipalreadyharvested = True

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

hdr = {'User-Agent' : 'Magic Browser'}
recs = []
for (dep, fc) in [('829', ''), ('5364', 'c'), ('817', 'm')]:
    for i in range(numofpages):
        tocurl = 'https://repositorio.unb.br/handle/10482/' + dep + '/browse?rpp=%i&sort_by=2&type=dateissued&offset=%i&etal=-1&order=DESC' % (rpp, i*rpp)
        ejlmod3.printprogress('=', [[dep], [i+1, numofpages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        time.sleep(2)
        for td in tocpage.body.find_all('td', attrs = {'headers' : 't3'}):
            for a in td.find_all('a'):
                rec = {'tc' : 'T', 'jnl' : 'BOOK', 'autaff' : [], 'keyw' : []}
                rec['link'] = 'https://repositorio.unb.br' + a['href']
                rec['doi'] = '20.2000/BrasiliaU' + a['href']
                if skipalreadyharvested and rec['doi'] in alreadyharvested:
                    pass
                else:
                    rec['tit'] = a.text.strip()
                    if fc: rec['fc'] = fc
                    recs.append(rec)
        print('  %4i records so far' % (len(recs)))
            
j = 0
for rec in recs:
    j += 1
    ejlmod3.printprogress('-', [[j, len(recs)], [rec['link']]])
    try:
        req = urllib.request.Request(rec['link'] + '?mode=full')
        artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        time.sleep(5)
    except:
        print('    try again in 120 seconds')
        time.sleep(120)
        req = urllib.request.Request(rec['link'] + '?mode=full')
        artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        time.sleep(5)
    ejlmod3.metatagcheck(rec, artpage, ['citation_date', 'citation_author', 
                                        'citation_language', 'citation_pdf_url', "DC.subject"])
    rec['autaff'][-1].append(publisher)                        
    for tr in artpage.find_all('tr'):
        for td in tr.find_all('td', attrs = {'class' : 'metadataFieldLabel'}):
            tdlabel = td.text.strip()
        for td in tr.find_all('td', attrs = {'class' : 'metadataFieldValue'}):
            #supervisor
            if tdlabel == 'dc.contributor.advisor':
                if len(td.text) > 6:
                    rec['supervisor'] = [[td.text.strip()]]
            #abstract
            elif tdlabel in ['dc.description.abstract', 'dc.description.abstract1']:
                if re.search(' the ', td.text):
                    rec['abs'] = td.text.strip()
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
