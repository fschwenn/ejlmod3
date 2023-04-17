# -*- coding: utf-8 -*-
#harvest theses from Montana State U.
#FS: 2020-11-27
#FS: 2023-04-17

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Montana State U.'
jnlfilename = 'THESES-MONTANASTATEU-%s' % (ejlmod3.stampoftoday())

rpp = 100
pages = 4
skipalreadyharvested = True

hdr = {'User-Agent' : 'Firefox'}

boringdeps = ['American Studies.', 'Chemical+%26+Biological+Engineering.',
              'Chemistry+%26+Biochemistry.', 'Ecology',
              'Doctor+of+Nursing+Practice+%28DNP%29', 'Ecology.', 'EdD',
              'Education.', 'Graduate+Studies', 'Graduate+Studies.',
              'History+%26+Philosophy.', 'Land+Resources+%26+Environmental+Sciences.',
              'Mechanical+%26+Industrial+Engineering.', 'MEd',
              'Microbiology+%26+Cell+Biology.', 'M+Nursing', 'Nursing.',
              'Plant+Sciences+%26+Plant+Pathology.', 'Professional+Paper',
              'Psychology.', 'Animal+%26+Range+Sciences.',
              'Microbiology+%26+Immunology.', 'Civil+Engineering.',
              'Earth+Sciences.']
boringdegrees = ['MS', 'MFA', 'MA']

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

prerecs = []
for page in range(pages):
    tocurl = 'https://scholarworks.montana.edu/xmlui/handle/1/733/discover?rpp=' + str(rpp) + '&etal=0&group_by=none&page=' + str(page+1) + '&sort_by=dc.date.issued_dt&order=desc'
    ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
    tocfilename = '/tmp/montanastateu.%s.%04i.html' % (ejlmod3.stampoftoday(), page)
    if not os.path.isfile(tocfilename):
        os.system('wget -q -O  %s "%s"' % (tocfilename, tocurl))
        time.sleep(5)
    inf = open(tocfilename, 'r')
    tocpage = BeautifulSoup(''.join(inf.readlines()), features="lxml")
    inf.close()
    prerecs += ejlmod3.getdspacerecs(tocpage, 'https://scholarworks.montana.edu', fakehdl=True, alreadyharvested=alreadyharvested, boringdegrees=boringdeps+boringdeps)
    print('   %i recs so far' % (len(prerecs)))

recs = []
i = 0
for rec in prerecs:
    keepit = True
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link'] + '?show=full'], [len(recs)]])
    artfilename = '/tmp/montanastateu.%s.thesis' % (re.sub('\D', '', rec['link']))
    if not os.path.isfile(artfilename):
        os.system('wget -q -O %s "%s"' % (artfilename, rec['link'] + '?show=full'))
        time.sleep(5)
    inf = open(artfilename, 'r')
    artpage = BeautifulSoup(''.join(inf.readlines()), features="lxml")
    inf.close()
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'DC.title', 'DCTERMS.issued',
                                        'DC.subject', 'citation_pdf_url',
                                        'DCTERMS.abstract'])
    rec['autaff'][-1].append(publisher)
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #pages
            if meta['name'] == 'citation_lastpage':
                rec['pages'] = meta['content']
            #abstract
            elif meta['name'] == 'citation_dissertation_name':
                rec['degree'] = meta['content']
    if 'degree' in list(rec.keys()):
        if rec['degree'] in boringdegrees:
            print('  skip "%s"' % (rec['degree']))
            ejlmod3.adduninterestingDOI(rec['doi'])
            keepit = False
    for tr in artpage.body.find_all('tr', attrs = {'class' : 'ds-table-row'}):
        for td in tr.find_all('td', attrs = {'class' : 'label-cell'}):
            tht = td.text.strip()
        for td in tr.find_all('td', attrs = {'class' : 'word-break'}):
            #pages
            if tht == 'thesis.format.extentlastpage':
                rec['pages'] = td.text.strip()
            #degree
            elif tht == 'thesis.degree.name':
                rec['degree'] = td.text.strip()
                if rec['degree'] in boringdegrees:
                    print('  skip "%s"' % (rec['degree']))
                    ejlmod3.adduninterestingDOI(rec['doi'])
                    keepit = False
                elif rec['degree'] != 'PhD':
                    rec['note'].append(rec['degree'])
            #department
            elif tht == 'thesis.degree.department':
                rec['dep'] = td.text.strip()
                if rec['dep'] == 'Mathematical Sciences.':
                    rec['fc'] = 'm'
                elif rec['dep'] == 'Computing.':
                    rec['fc'] = 'c'
                elif rec['dep'] in boringdeps:
                    print('  skip "%s"' % (rec['dep']))
                    ejlmod3.adduninterestingDOI(rec['doi'])
                    keepit = False
                elif rec['dep'] != 'Physics.':
                    rec['note'].append(rec['dep'])
    if keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
        
ejlmod3.writenewXML(recs, publisher, jnlfilename)
