# -*- coding: utf-8 -*-
#harvest theses from Porto
#FS: 2021-02-24
#FS: 2023-04-18

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Porto U.'
jnlfilename = 'THESES-PORTO-%s' % (ejlmod3.stampoftoday())

rpp = 20
pages = 2
skipalreadyharvested = True

boringdeps = ['Quimica', 'Biological sciences', 'Ciencias biologicas', 'Ciencias da educacao',
              'Educational sciences', 'Ciencias agrarias::Agricultura, silvicultura e pescas',
              'Agrarian Sciences::Agriculture, Forestry, and Fisheries',
              'Agricultura, silvicultura e pescas', 'Agriculture, Forestry, and Fisheries', 
              'Ciencias da terra e ciencias do ambiente', 'Earth and related Environmental sciences',
              'Chemical sciences', 'Ciências exactas e naturais::Química',
              'Ciências da engenharia e tecnologias::Outras ciências da engenharia e tecnologias',              
              'Engineering and technology::Other engineering and technologies',
              'Natural sciences::Chemical sciences', 'Other engineering and technologies',
              'Outras ciências da engenharia e tecnologias', 'Química']

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

hdr = {'User-Agent' : 'Magic Browser'}

prerecs = []
for page in range(pages):
    tocurl = 'https://repositorio-aberto.up.pt/handle/10216/9537/browse?rpp=' + str(rpp) + '&sort_by=2&type=dateissued&offset=' + str(rpp*page) + '&etal=-1&order=DESC'
    ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    for tr in tocpage.body.find_all('tr'):
        for td in tr.find_all('td', attrs = {'headers' : 't2'}):
            rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'autaff' : [], 'note' : [], 'oa' : False}
            for a in td.find_all('a'):
                rec['artlink'] = 'https://repositorio-aberto.up.pt' + a['href'] #+ '?show=full'
                rec['hdl'] = re.sub('.*handle\/', '',  a['href'])
                if ejlmod3.checkinterestingDOI(rec['hdl']):
                    if not skipalreadyharvested or not rec['hdl'] in alreadyharvested:
                        prerecs.append(rec)
    time.sleep(7)

i = 0
recs = []
for rec in prerecs:
    i += 1
    keepit = True
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
  
    ejlmod3.metatagcheck(rec, artpage, ['DC.rights', 'DC.language', 'DC.title',
                                        'DCTERMS.issued', 'DCTERMS.abstract',
                                        'citation_pdf_url'])
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #author
            if meta['name'] == 'DC.creator':
                if re.search('\d\d\d\d\-\d\d\d\d',  meta['content']):
                    rec['autaff'][-1].append('ORCID:' + meta['content'])
                else:
                    author = re.sub(' *\[.*', '', meta['content'])
                    rec['autaff'].append([ author ])
            #department
            elif meta['name'] == 'DC.subject':
                dep = meta['content']
                if dep in boringdeps:
                    print('   skip', dep)
                    keepit = False
                    continue
                elif dep in ['Ciências da computação e da informação',
                             'Ciências exactas e naturais::Ciências da computação e da informação',
                             'Computer and information sciences',
                             'Natural sciences::Computer and information sciences']:
                    rec['fc'] = 'c'
                elif dep in ['Ciências exactas e naturais::Matemática',
                             'Matemática', 'Mathematics',
                             'Natural sciences::Mathematics']:
                    rec['fc'] = 'c'
                elif not dep in ['Física', 'Ciências exactas e naturais::Física',
                                 'Physical sciences']:
                    rec['note'].append('DEP:::'+dep)
    if len(rec['autaff']) == 1:
        rec['autaff'][-1].append(publisher)
    #license
    ejlmod3.globallicensesearch(rec, artpage)
    if keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['hdl'])
ejlmod3.writenewXML(recs, publisher, jnlfilename)
