# -*- coding: utf-8 -*-
#harvest theses from Bochum
#FS: 2021-02-09
#FS: 2022-11-01

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Ruhr U., Bochum (main)'
jnlfilename = 'THESES-BOCHUM-%s' % (ejlmod3.stampoftoday())

rpp = 100
pages = 5
skipalreadyharvested = True

boring = ['Literatur / Englische Literatur Amerikas', 'Philosophie und Psychologie / Philosophie',
          'Philosophie und Psychologie / Psychologie', 'Allgemeines, Informatik, Informationswissenschaft / Informatik',
          'Naturwissenschaften und Mathematik / Biowissenschaften, Biologie, Biochemie',
          'Naturwissenschaften und Mathematik / Chemie, Kristallographie, Mineralogie',
          'Naturwissenschaften und Mathematik / Geowissenschaften, Geologie', 'Religion / Bibel',
          'Allgemeines, Informatik, Informationswissenschaft / Nachrichtenmedien, Journalismus, Verlagswesen',
          'Naturwissenschaften und Mathematik / Pflanzen (Botanik)',
          'Naturwissenschaften und Mathematik / Tiere (Zoologie)',
          'Technik, Medizin, angewandte Wissenschaften / Industrielle und handwerkliche Fertigung',
          'Technik, Medizin, angewandte Wissenschaften',
          'Technik, Medizin, angewandte Wissenschaften / Technische Chemie']
hdr = {'User-Agent' : 'Magic Browser'}

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

prerecs = []
for page in range(pages):
    tocurl = 'https://hss-opus.ub.ruhr-uni-bochum.de/opus4/solrsearch/index/search/searchtype/all/start/' + str(rpp*page) + '/rows/' + str(rpp) + '/doctypefq/doctoralthesis/sortfield/year/sortorder/desc'    
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    for div in tocpage.body.find_all('div', attrs = {'class' : 'result_box'}):
        for div2 in div.find_all('div', attrs = {'class' : 'results_title'}):
            rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'note' : [], 'supervisor' : []}
            for a in div2.find_all('a'):
                rec['artlink'] = 'https://hss-opus.ub.ruhr-uni-bochum.de' + a['href']
                if ejlmod3.checkinterestingDOI(rec['artlink']):
                    prerecs.append(rec)
    time.sleep(10)

i = 0
recs= []
for rec in prerecs:
    i += 1
    keepit = True
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['artlink']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']))
        except:
            print("no access to %s" % (rec['artlink']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['DC.Creator', 'DC.Identifier', 'DC.title',
                                        'citation_date', 'DC.subject', 'citation_pdf_url',
                                        'DC.rights'])
    #abstract
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'DC.Description'}):
        if re.search(' the ', meta['content']):
            rec['abs'] = meta['content']
        else:
            rec['abs_de'] = meta['content']
    for table in artpage.find_all('table', attrs = {'class' : 'result-data'}):
        for tr in table.find_all('tr'):
            for th in tr.find_all('th'):
                tht = th.text.strip()
            for td in tr.find_all('td'):
                #author
                if tht == 'Author:':
                    for a in td.find_all('a', attrs = {'class' : 'orcid-link'}):
                        rec['autaff'][-1].append(re.sub('.*orcid.org\/', 'ORCID:', a['href']))
                    for a in td.find_all('a', attrs = {'class' : 'gnd-link'}):
                        gndlink = a['href']
                #URN
                elif tht == 'URN:':
                    rec['urn'] = td.text.strip()
                #DOI
                elif tht == 'DOI:':
                    rec['doi'] = re.sub('.*doi.org\/', '', td.text.strip())
                #supervisor
                elif tht == 'Referee:':
                    for a in td.find_all('a'):
                        if re.search('opus4.solrsearch', a['href']):
                            rec['supervisor'].append([a.text.strip()])
                        elif re.search('orcid.org', a['href']):
                            rec['supervisor'][-1].append(re.sub('.*orcid.org\/', 'ORCID:', a['href']))
                        elif re.search('nv.info.gnd', a['href']):
                            gnd = a['href']
                #language
                elif tht == 'Language:':
                    if td.text.strip() == 'German':
                        rec['language'] = 'German'
                #aff
                elif tht == 'Granting Institution:':
                    rec['autaff'][-1].append('%s, Bochum, Germany' % (td.text.strip()))
                #Dewey
                elif tht == 'Dewey Decimal Classification:':
                    if td.text.strip() in boring:
                        keepit = False
                        #print('  skip', td.text.strip())
                    elif td.text.strip() == 'Naturwissenschaften und Mathematik / Mathematik':
                        rec['fc'] = 'm'
                    elif re.search('(K.nste |Literatur|Geografie|Sozialw|Sprache|Religion|Medizin)', td.text):
                        keepit = False
                        #print('  skip')
                    else:
                        rec['note'].append(td.text.strip())
    #abstract
    if not 'abs' in list(rec.keys()) and 'abs_de' in list(rec.keys()):
        rec['abs'] = rec['abs_de']
    if keepit:
        if skipalreadyharvested and 'doi' in rec and rec['doi'] in alreadyharvested:
            print('   already in backup')
        else:
            recs.append(rec)
            print('  ', list(rec.keys()))
    else:
        ejlmod3.adduninterestingDOI(rec['artlink'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
