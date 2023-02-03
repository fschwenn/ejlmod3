# -*- coding: utf-8 -*-
#harvest theses from Munster
#FS: 2021-02-10
#FS: 2023-02-01

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'U. Munster'
jnlfilename = 'THESES-MUNSTER-%s' % (ejlmod3.stampoftoday())

pages = 1
skipalreadyharvested = True
boring = []
hdr = {'User-Agent' : 'Magic Browser'}

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

prerecs = []
for dep in ['FB+10%3A+Mathematik+und+Informatik', 'FB+11%3A+Physik']:
    for page in range(pages):
        tocurl = 'https://miami.uni-muenster.de/Search/Results?sort=year&page=' + str(page+1) + '&filter%5B%5D=ulb_DocumentType_facet%3A%22Dissertation%2FHabilitation%22&filter%5B%5D=ulb_affiliation_facet%3A%22' + dep + '%22&type=AllFields'
        ejlmod3.printprogress("=", [[dep], [page+1, pages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")    
        for div in tocpage.body.find_all('div', attrs = {'class' : 'media'}):
            rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'note' : [dep[9:]], 'supervisor' : []}
            for a in div.find_all('a', attrs = {'class' : ['title', 'getFull']}):
                rec['artlink'] = 'https://miami.uni-muenster.de' + a['href']
                rec['tit'] = a.text.strip()
                prerecs.append(rec)
        time.sleep(10)

i = 0
recs = []
for rec in prerecs:
    keepit = True
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['artlink']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        except:
            print("no access to %s" % (rec['artlink']))
            continue
    for table in artpage.find_all('table'):
        for tr in table.find_all('tr'):
            for th in tr.find_all('th'):
                tht = th.text.strip()
            for td in tr.find_all('td'):
                #author
                if tht in ['Author:', 'Verfasser:']:
                    for a in td.find_all('a'):
                        if re.search('GND', a.text):
                            gndlink = a['href']
                            a.decompose()
                        elif re.search('VIAF', a.text):
                            a.decompose()
                    for a in td.find_all('a'):
                        rec['autaff'] = [[ a.text.strip(), publisher ]]
                #supervisor
                elif tht in ['Further contributors:', 'Weitere Beteiligte:']:
                    for a in td.find_all('a'):
                        if re.search('GND', a.text):
                            gndlink = a['href']
                            a.decompose()
                        elif re.search('VIAF', a.text):
                            a.decompose()
                    for a in td.find_all('a'):
                        rec['supervisor'].append([a.text.strip()])
                #date
                elif tht in ['Publication date:', 'Erscheinungsdatum:']:
                    rec['date'] = td.text.strip()
                #keywords
                elif tht == 'Subjects:' or re.search('^Schlagw', tht):
                    rec['keyw'] += re.split('; ', td.text.strip())
                #URN
                elif tht == 'URN:':
                    rec['urn'] = td.text.strip()
                elif tht == 'Permalink:':
                    rec['link'] = td.text.strip()
                #DOI
                elif tht in ['Other Identifiers:', 'Weitere Identifikatoren:']:
                    tdt = re.sub('[\n\t\r]', ' ', td.text)
                    if re.search('10.17879\/', tdt):
                        rec['doi'] = re.sub('.*(10.17879\/\d+).*', r'\1', tdt)
                #license
                elif tht in ['License:', 'Lizenz:']:
                    for a in td.find_all('a'):
                        rec['license'] = {'url' : a['href']}
                #PDF
                elif tht in ['Digital documents:', 'Onlinezugriff:']:
                    for a in td.find_all('a'):
                        rec['pdf_url'] = a['href']
                #language
                elif tht in ['Language:', 'Sprache']:
                    if td.text.strip() == 'German':
                        rec['language'] = 'German'
    #abstract
    for p in artpage.find_all('p', attrs = {'class' : 'summary'}):
        if re.search(' the ', p.text.strip()):
            rec['abs'] = p.text.strip()
        else:
            rec['abs_de'] = p.text.strip()
    if not 'abs' in list(rec.keys()) and 'abs_de' in list(rec.keys()):
        rec['abs'] = rec['abs_de']
    if skipalreadyharvested:
        if 'urn' in rec and rec['urn'] in alreadyharvested:
            keepit = False
        elif 'doi' in rec and rec['doi'] in alreadyharvested:
            keepit = False
    if keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
