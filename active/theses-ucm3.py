# -*- coding: utf-8 -*-
#harvest theses from UCM, Somosaguas
#FS: 2021-11-30
#FS: 2023-04-28

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'UCM, Somosaguas'
jnlfilename = 'THESES-UniversidadComplutenseDeMadrid-%s' % (ejlmod3.stampoftoday())

hdr = {'User-Agent' : 'Magic Browser'}
years = 1
skipalreadyharvested = True

deps = [('216', 'Madrid U.', ''),
        ('219', 'UCM, Madrid, Dept. Phys.', 'a'),
        ('222', 'UCM, Madrid, Dept. Phys.', ''),
        ('217', 'UCM, Madrid, Dept. Phys.', ''),
        ('6', 'UCM, Madrid, Dept. Phys.', ''),
        ('256', 'UCM, Madrid, Dept. Math.', 'm'),
        ('255', 'UCM, Madrid, Dept. Math.', 'm'),
        ('257', 'UCM, Madrid, Dept. Math.', 'm'),
        ('9132', 'UCM, Madrid, Dept. Math.', 'm'),
        ('251', 'UCM, Madrid, Dept. Math.', 'c'),
        ('9152', 'UCM, Madrid, Dept. Math.', 'a'),
        ('9', 'UCM, Madrid, Dept. Math.', 'm'),
        ('252', 'UCM, Madrid, Dept. Math.', 'a'),
        ('9149', 'ICMAT, Madrid', 'm'),
        ('9150', 'UCM, Somosaguas', 'm'),
        ('9141', 'UCM, Somosaguas', ''),
        ('18', 'UCM, Somosaguas', 'c'),
        ('2403', 'UCM, Somosaguas', 'c'),
        ('457', 'UCM, Somosaguas', 'c')]

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

links = []
recs = []
for (depnr, aff, fc) in deps:
    tocurl = 'https://eprints.ucm.es/view/divisions/%s.html' % (depnr)
    print(tocurl)
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    time.sleep(5)
    for div in tocpage.body.find_all('div', attrs = {'class' : 'ep_view_page'}):
        h2t = ''
        for child in div.children:
            try:
                child.name
            except:
                continue
            if child.name == 'h2':
                h2t = child.text
            if child.name == 'p' and h2t in ['Thesis', 'Tesis']:
                rec = {'tc' : 'T', 'jnl' : 'BOOK', 'supervisor' : [], 'note' : []}
                rec['affiliation'] = aff
                if fc:
                    rec['fc'] = fc
                for a in child.find_all('a'):
                    rec['link'] = a['href']
                    rec['doi'] = '30.3000/UniversidadComplutenseDeMadrid/' + re.sub('\D', '', a['href'])
                    a.decompose()
                pt = re.sub('[\n\t\r]', '', child.text.strip())
                if re.search('\([12]\d\d\d\)', pt):
                    rec['date'] = re.sub('.*\(([12]\d\d\d)\).*', r'\1', pt)
                if not skipalreadyharvested or not 'doi' in rec or not rec['doi'] in alreadyharvested:
                    if not rec['link'] in links:
                        if 'date' in list(rec.keys()):
                            if int(rec['date']) >= ejlmod3.year()-years:
                                recs.append(rec)
                        else:
                            recs.append(rec)
                        links.append(rec['link'])
        print('  %4i records so far' % (len(recs)))

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['link']]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(5)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['DC.title', 'DC.language', 'DC.contributor',
                                        'DC.description'])
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #date
            if meta['name'] == 'DC.date':
                if not re.search('embargo', meta['content']):
                    rec['date'] = meta['content']
            #FFT
            elif meta['name'] == 'DC.identifier':
                if re.search('\.pdf$', meta['content']):
                    rec['hidden'] = meta['content']
            #author
            elif meta['name'] == 'DC.creator':
                rec['autaff'] = [[ meta['content'], rec['affiliation'] ]]
            #subject
            elif meta['name'] == 'DC.subject':
                rec['note'].append(meta['content'])
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
