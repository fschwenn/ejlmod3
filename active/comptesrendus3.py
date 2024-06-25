# -*- coding: UTF-8 -*-
#program to harvest Comptes Rendus by the French academy of sciences
# FS 2020-10-20
# FS 2023-03-27

import os
import ejlmod3
import re
import sys
#import unicodedata
#import string
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import time

publisher = 'Academie des sciences'

skipalreadyharvested = True

jnl = sys.argv[1]
vol = sys.argv[2]
if len(sys.argv) > 3:
    iss = sys.argv[3]
else:
    iss = False



if iss:
    jnlfilename = 'cr%s%s.%s_%s' % (jnl, vol, iss, ejlmod3.stampoftoday())
else:
    jnlfilename = 'cr%s%s_%s' % (jnl, vol, ejlmod3.stampoftoday())

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

#journals have quite different number of articles per month
if jnl == 'mathematique':
    year = str(1662 + int(vol))
    if iss:
        tocurl = 'https://comptes-rendus.academie-sciences.fr/mathematique/issues/CRMATH_%s__%s_%s' % (year, vol, iss)
    else:
        tocurl = 'https://comptes-rendus.academie-sciences.fr/mathematique/volume/CRMATH_%s__%s' % (year, vol)
    jnlname = 'Compt.Rend.Math.'
elif jnl == 'physique':
    year = str(1999 + int(vol))
    if iss:
        tocurl = 'https://comptes-rendus.academie-sciences.fr/physique/issues/CRPHYS_%s__%s_%s' % (year, vol, iss)
        tocurl = 'https://comptes-rendus.academie-sciences.fr/physique/item/CRPHYS_%s__%s_%s' % (year, vol, iss)
    else:
        tocurl = 'https://comptes-rendus.academie-sciences.fr/physique/volume/CRPHYS_%s__%s' % (year, vol)
        tocurl = 'https://comptes-rendus.academie-sciences.fr/physique/volume_general/CRPHYS_%s__%s' % (year, vol)
    jnlname = 'Comptes Rendus Physique'

hdr = {'User-Agent' : 'Mozilla/5.0'}
try:
    print(tocurl)
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
except:
    try:
        time.sleep(1)
        print(tocurl + '_S1')
        req = urllib.request.Request(tocurl + '_S1', headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    except:
        time.sleep(1)
        print(tocurl + '_G1')
        req = urllib.request.Request(tocurl + '_G1', headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
prerecs = []
for span in tocpage.body.find_all('span', attrs = {'class' : 'article-title'}):
    for a in span.find_all('a'):
        rec = {'jnl' : jnlname, 'tc' : 'P', 'keyw' : [], 'autaff' : [],
               'year' : year, 'vol' : vol, 'refs' : []}
        if iss:
            rec['issue'] = iss
        rec['artlink'] = 'https://comptes-rendus.academie-sciences.fr' + a['href']
        prerecs.append(rec)

i = 0
recs = []
for rec in prerecs:
    i += 1
    time.sleep(3)
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    req = urllib.request.Request(rec['artlink'], headers=hdr)
    artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['citation_doi', 'citation_title', 'citation_firstpage',
                                        'citation_lastpage', 'citation_pdf_url'])
    #abstract
    for div in artpage.body.find_all('div', attrs = {'id' : 'abstract-en'}):
        for p in div.find_all('p'):
            rec['abs'] = p.text.strip()
    #authors
    for div in artpage.body.find_all('div', attrs = {'class' : 'article-author'}):
        for a in div.find_all('a'):
            if re.search('orcid.org', a['href']):
                rec['autaff'][-1].append(re.sub('.*\/', 'ORCID:', a['href']))
            else:
                rec['autaff'].append([a.text.strip()])
    #date
    for div in artpage.body.find_all('div', attrs = {'id' : 'info-tab'}):
        divt = re.sub('[\n\t\r]', ' ', div.text.strip())
        if re.search('Published online: ', divt):
            rec['date'] = re.sub('.*Published online: ([\d\-]+).*', r'\1', divt)
    #references
    for div in artpage.body.find_all('div', attrs = {'id' : 'references-tab'}):
        for p in div.find_all('p', attrs = {'class' : 'bibitemcls'}):
            for a in p.find_all('a'):
                if a.has_attr('href') and re.search('doi.org', a['href']):
                    rdoi = re.sub('.*doi.org\/', r', DOI: ', a['href'])
                    a.replace_with(rdoi)

            pt = p.text.strip()
            pt = re.sub(', Volume ', ' ', pt)
            #replace ';' in names by ','
            numbers = False
            parts = re.split(';', pt)
            ptnew = parts[0]
            if re.search('\d', re.sub('^[\[\]\d]+', '', ptnew)):
                numbers = True
            for part in parts[1:]:
                if numbers:
                    ptnew += '; ' + part
                else:
                    ptnew += ', ' + part
                if re.search('\d', part):
                    numbers = True
            rec['refs'].append([('x', ptnew)])
    if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
