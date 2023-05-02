# -*- coding: utf-8 -*-
#harvest theses from Taiwan, Natl. Taiwan U.
#FS: 2021-11-14
#FS: 2023-04-29

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Taiwan, Natl. Taiwan U.'
jnlfilename = 'THESES-TaiwanNatlU-%s' % (ejlmod3.stampoftoday())

rpp = 20
pages = 4
skipalreadyharvested = True
departments = [('PHYS', '65'), ('PHYS', '69'), ('MATH', '64'), ('MATH', '66'), ('ASTRO', '62')]
hdr = {'User-Agent' : 'Magic Browser'}
timespan = 2

departmentdict = {'應用物理研究所' : 'Institute of Applied Physics',
                  '應用物理所' : 'Institute of Applied Physics',
                  '物理研究所' : 'Institute of Physics',
                  '物理學研究所' : 'Institute of Physics',
                  '應用數學科學研究所' : 'Institute of Applied Mathematics',
                  '數學研究所' : 'Institute of Mathematics',
                  '天文物理研究所' : 'Institute of Astrophysics'}

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

j = 0
prerecs = []
recs = []
for (subj, dep) in departments:
    j += 1
    for page in range(pages):
        tocurl = 'https://tdr.lib.ntu.edu.tw/handle/123456789/' + dep + '/simple-search?query=&start=' + str(rpp*page) + '&rpp=' + str(rpp) + '&locale=en&sort_by=dc.date.issued_dt&order=DESC&etal=0'
        ejlmod3.printprogress("=", [[subj], [page+1 + (j-1)*pages, pages*len(departments)], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        time.sleep(6)
        #for td in tocpage.find_all('td', attrs = {'headers', 't2'}):
        for td in tocpage.find_all('tr'):
            year = 9999
            rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'supervisor' : [], 'note' : [],
                   'aff' : [publisher], 'refs' : []}
            for em in td.find_all('em'):
                emt = em.text.strip()
                if re.search('^\d\d\d\d$', emt):
                    year = int(emt)
            if year >= ejlmod3.year(backwards=timespan):
                if subj == 'MATH':
                    rec['fc'] = 'm'
                elif subj == 'ASTRO':
                    rec['fc'] = 'a'
                for a in td.find_all('a'):
                    if a.has_attr('href') and re.search('handle\/', a['href']):
                        rec['link'] = 'https://tdr.lib.ntu.edu.tw' + a['href']  + '?mode=full&locale=en'
                        rec['doi'] = '20.2000/TaiwanNatlU/' + re.sub('.*handle\/', '', a['href'])
                        if ejlmod3.checkinterestingDOI(rec['doi']):
                            if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
                                prerecs.append(rec)
                                rec['nodoi'] = '20.2000/TaiwanNatlU/' + re.sub('.*handle\/', '', a['href'])
            else:
                print('   %i too old' % (year))
        print('\n  %4i records so far\n' % (len(prerecs)))

i = 0
for rec in prerecs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(5)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']))
        except:
            print("no access to %s" % (rec['link']))
            continue
    (author, altauthor, zhtitle, entitle) = (False, False, False, False)
    keepit = True
    ejlmod3.metatagcheck(rec, artpage, ['DCTERMS.issued', 'citation_pdf_url',
                                        'DC.subject', 'DC.identifier'])
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #author
            if meta['name'] == 'DC.creator':
                if meta.has_attr('xml:lang') and meta['xml:lang'] == 'zh_TW':
                    altauthor = meta['content']
                else:
                    author = meta['content']
            #title
            elif meta['name'] == 'DC.title':
                if meta.has_attr('xml:lang'):
                    if meta['xml:lang'] == 'zh_TW':
                        zhtitle =  meta['content']
                    elif  meta['xml:lang'] == 'en':
                        entitle = meta['content']
                else:
                    rec['tit'] = meta['content']
            #abstract
            elif meta['name'] == 'DCTERMS.abstract':
                if meta.has_attr('xml:lang') and meta['xml:lang'] == 'en':
                    rec['abs'] = meta['content']
            #pages
            elif meta['name'] == 'DC.relation':
                rec['pages'] = meta['content']
    #author
    if altauthor:
        author += ', CHINESENAME: %s' % (altauthor)
    rec['auts'] = [ author ]
    #more metadata
    for table in artpage.body.find_all('table', attrs = {'class' : 'panel-body'}):
        for tr in table.find_all('tr'):
            for td in tr.find_all('td', attrs = {'class' : 'metadataFieldLabel'}):
                label = td.text.strip()
            for td in tr.find_all('td', attrs = {'class' : 'metadataFieldValue', 'headers' : 's2'}):
                #references
                if label == 'dc.identifier.citation':
                    for br in td.find_all('br'):
                        br.replace_with('BRBRBR')
                    for ref in re.split('BRBRBR', td.text.strip()):
                        rec['refs'].append([('x', ref)])
                #supervisor
                if label == 'dc.contributor.advisor':
                    if td.text.strip():
                        rec['supervisor'].append([re.sub('.*\((.*)\)', r'\1', td.text.strip())])
                #language
                if label == 'dc.language.iso':
                    if td.text.strip() == 'en':
                        if entitle:
                            rec['tit'] = entitle
                        if zhtitle:
                            rec['transtit'] = zhtitle
                    elif td.text.strip():
                        if td.text.strip() in ['zh_TW', 'zh-TW']:
                            rec['language'] = 'Chinese'
                        else:
                            rec['note'].append('LANGUAGE=%s' % (td.text.strip()))
                        if zhtitle:
                            rec['otits'] = [ zhtitle ]
                        if entitle:
                            rec['tit'] = entitle
                #degree
                elif label == 'dc.description.degree':
                    degree = td.text.strip()
                    if not degree == '博士':
                        if degree == '碩士':
                            print('   skip master thesis')
                            keepit = False
                        elif degree:
                            rec['note'].append('unknown degree: %s' % (degree))
                #department
                elif label == 'dc.contributor.author-dept':
                    department = td.text.strip()
                    if department:
                        if department in list(departmentdict.keys()):
                            rec['note'].append('DEPARTMENT=%s' % (departmentdict[department]))
                        else:
                            rec['note'].append('DEPARTMENT=%s' % (department))
    if keepit:
        if not skipalreadyharvested or not rec['doi'] in alreadyharvested:                 
            recs.append(rec)
            ejlmod3.printrecsummary(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['nodoi'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
