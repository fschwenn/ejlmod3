# -*- coding: utf-8 -*-
#harvest theses from Brwon U.
#FS: 2020-08-10
#FS: 2023-01-18

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

departments = [('Physics', 'bdr:qe4nbxku', ''),
               ('Applied Mathematics', 'bdr:8jst2uj2', 'm'),
               ('Computer Science', 'bdr:bfttpwkj', 'c'),
               ('Mathematics', 'bdr:y88ydcty', 'm')]
boringsubjects = ['Biophysics', 'Bacteriology', 'Extrasolar planets', 'ocean modeling', 'DNA',
                  'picosecond ultrasonics', 'nanofabrication', 'Urbanization',
                  'Liquid crystals', 'Acoustic microscopy<', 'Africana Studies']

publisher = 'Brown U.'

rpp = 20
pages = 1
skipalreadyharvested = True

jnlfilename = 'THESES-BROWN-%s' % (ejlmod3.stampoftoday())

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

hdr = {'User-Agent' : 'Magic Browser'}

prerecs = []

for (dep, cod, fc) in departments:
    for page in range(pages):
        tocurl = 'https://repository.library.brown.edu/studio/collections/' + cod + '/?page=' + str(page+1) + '&per_page=' + str(rpp) + '&sort=date_d'
        ejlmod3.printprogress('=', [[dep], [page+1, pages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        for div in tocpage.body.find_all('div', attrs = {'class' : 'results-normal'}):
            for div2 in div.find_all('div', attrs = {'class' : 'panel-default'}):
                rec = {'tc' : 'T', 'jnl' : 'BOOK', 'keyw' : [], 'fc' : ''}
                if fc: rec['fc'] = fc
                keepit = True
                #title
                for h4 in div2.find_all('h4'):
                    rec['tit'] = h4.text.strip()
                #link
                for div3 in div2.find_all('div', attrs = {'class' : 'full-record-link'}):
                    for a in div3.find_all('a'):
                        rec['artlink'] = 'https://repository.library.brown.edu' + a['href']
                for dl in div2.find_all('dl'):
                    for child in dl.children:
                        try:
                            child.name
                        except:
                            continue
                        if child.name == 'dt':
                            dtt = child.text
                        elif child.name == 'dd':
                            #year
                            if dtt == 'Year:':
                                rec['year'] = child.text.strip()
                                rec['date'] = child.text.strip()
                            #contributors
                            elif dtt == 'Contributor:':
                                ddt = child.text.strip()
                                if re.search('\([Cc]reator', ddt):
                                    rec['autaff'] = [[ re.sub(' *\(.*', '', child.text.strip()), publisher ]]
                                elif re.search('\([Aa]dvisor', ddt):
                                    rec['supervisor'] = [[ re.sub(' *\(.*', '', child.text.strip()) ]]
                            #Subjects
                            elif dtt == 'Subject:':
                                ddt = child.text.strip()
                                if ddt in boringsubjects:
                                    print('  skip', ddt)
                                    keepit = False
                                else:
                                    rec['keyw'].append(ddt)
                                if ddt in ['Cosmology', 'Galaxy Clusters',
                                           'Dark matter (Astronomy)',
                                           'Astrophysics', 'Radio astronomy']:
                                    if not 'a' in rec['fc']:
                                        rec['fc'] += 'a'
                                elif ddt in ['Experimental Particle Physics',
                                             'CMS Experiment', 'Experiment-HEP']:
                                    if not 'e' in rec['fc']:
                                        rec['fc'] += 'e'
                                elif ddt in ['Gravitational lenses',
                                             'Quantum gravity', 'Gravity']:
                                    if not 'g' in rec['fc']:
                                        rec['fc'] += 'g'
                if keepit:
                    prerecs.append(rec)
        print('  %4i records so far' % (len(prerecs)))
        time.sleep(2)

i = 0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        time.sleep(3)
    except:
        try:
            print("   retry %s in 60 seconds" % (rec['artlink']))
            time.sleep(60)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        except:
            print("   no access to %s" % (rec['artlink']))
            continue
    for dl in artpage.body.find_all('dl'):
        for child in dl.children:
            try:
                child.name
            except:
                continue
            if child.name == 'dt':
                dtt = child.text
            elif child.name == 'dd':
                #pages
                if dtt == 'Extent:':
                    ddt = child.text.strip()
                    if re.search('\d\d', ddt):
                        rec['pages'] = re.sub('\D*(\d\d+).*', r'\1', ddt)
                #DOI
                elif dtt == 'DOI':
                    rec['doi'] = re.sub('.*doi.org\/(.*)', r'\1', child.text.strip())
                #abstract
                elif dtt == 'Abstract:':
                    rec['abs'] = child.text.strip()
                #author
                elif dtt == 'Contributor:':
                    if not 'autaff' in rec:
                        if re.search('\(author\)', child.text):
                            rec['autaff'] = re.sub(' *\(.*', '', child.text.strip())
                #fulltext
    for ul in artpage.body.find_all('ul', attrs = {'class' : 'list-inline'}):
        for li in ul.find_all('li'):
            for span in li.find_all('span'):
                if re.search('Download PDF', span.text):
                    for a in li.find_all('a'):
                        rec['hidden'] = 'https://repository.library.brown.edu' + a['href']
    #pseudDOI
    if not 'doi' in rec.keys():
        rec['link'] = rec['artlink']
        rec['doi'] = '20.2000/BROWN/' + re.sub('\D', '', rec['link'])
    if rec['doi'] in alreadyharvested:
        print('   already in backup')
    else:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
