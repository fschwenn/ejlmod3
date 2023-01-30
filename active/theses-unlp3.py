# -*- coding: utf-8 -*-
#harvest theses from Universidad Nacional de La Plata
#FS: 2020-06-30
#FS: 2023-01-27

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'UNLP, La Plata (main) '
rpp = 50
pages = 2
uninteresting = ['Tesis de maestria', 'Tesis de grado']
uninteresting += ['Doctor en Ciencias Exactas, área Ciencias Biológicas',
                  'Doctor en Ciencias Exactas, área Química',
                  'Doctor en Tecnología e Higiene de los Alimentos',
                  'Doctor en Biotecnología y Biología Molecular',
                  'Doctor en Ciencia y Tecnología de los Alimentos',
                  'Doctor en Química y Tecnología Ambiental',
                  'Doctor de la Facultad de Ciencias Exactas, area Ciencias Biológicas',
                  'Doctor de la Facultad de Ciencias Exactas, Química',
                  'Doctor en Química']

jnlfilename = 'THESES-UNLP-%s' % (ejlmod3.stampoftoday())

hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
handles = []
for page in range(pages):
    tocurl = 'http://sedici.unlp.edu.ar/handle/10915/23/discover?rpp=' + str(rpp) + '&etal=0&group_by=none&page=' + str(page+1) + '&sort_by=dc.date.issued_dt&order=desc'
    ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    time.sleep(3)
    for rec in ejlmod3.getdspacerecs(tocpage, 'http://sedici.unlp.edu.ar'):
        if not rec['hdl'] in handles and ejlmod3.checkinterestingDOI(rec['hdl']):
            prerecs.append(rec)
            handles.append(rec['hdl'])
    print('  %4i records so far' % (len(prerecs)))
        
recs = []
for (i, rec) in enumerate(prerecs):
    keepit = True
    ejlmod3.printprogress("-", [[i+1, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link'] + '?show=full'), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link'] + '?show=full'), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['DC.contributor', 'DC.title', 'DCTERMS.issued',
                                        'DC.subject', 'DC.language', 'citation_pdf_url',
                                        'DCTERMS.abstract', 'DC.rights', 'DC.identifier',
                                        'DC.type'])
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'DC.creator'}):
        author = re.sub(' *\[.*', '', meta['content'])
        rec['autaff'] = [[ author, publisher ]]

    #degree - level
    for subject in rec['note']:
        if subject in uninteresting:
            keepit = False
    #degree - exact
    for tr in artpage.body.find_all('tr'):
        for th in tr.find_all('td', attrs = {'class' : 'label-cell'}):
            tht = th.text.strip()
            th.decompose()
        if tht == 'thesis.degree.name':
            for td in tr.find_all('td'):
                degree = td.text.strip()
                if degree in uninteresting:
                    keepit = False
                elif degree in ['Doctor en Ciencias Exactas, área Matemática']:
                    rec['fc'] = 'm'
                elif not degree in ['Doctor en Ciencias Exactas, área Física']:
                    rec['note'].append(degree)        
    if keepit:
        recs.append(rec)
        ejlmod3.printrecsummary(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['hdl'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
