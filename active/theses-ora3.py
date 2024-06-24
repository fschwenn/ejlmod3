# -*- coding: utf-8 -*-
#harvest Oxford University Reseach Archive for theses
#FS: 2018-01-25
#FS: 2023-01-20

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

years = 2
#pagesdate = 1
pagesnodate = 12
rpp = 100
skipalreadyharvested = True

publisher = 'Oxford University'
jnlfilename = 'THESES-ORA-%s' % (ejlmod3.stampoftoday())

boring = ['Biochemistry', 'Biomedical Services', 'Chemistry', 'Classics Faculty',
          'Clinical Neurosciences', 'Education', 'Engineering Science',
          'English Faculty', 'Experimental Psychology', 'History Faculty', 'Law',
          'Materials', 'Medieval & Modern Languages Faculty', 'Oriental Studies Faculty',
          'Pathology Dunn School', 'Pharmacology', 'Philosophy Faculty', 'Economics',
          'Physiology Anatomy & Genetics', 'Social Policy & Intervention', 'Sociology',
          'Surgical Sciences', 'Theology Faculty', 'NDORMS', 'Earth Sciences', 
          'International Development', 'Oncology', 'OSGA', 'Plant Sciences', 
          'RDM', 'Ruskin School of Art', 'SAME', 'School of Archaeology', 'SOGE', 
          'Blavatnik School of Government', 'Continuing Education', 'Zoology',
          'Linguistics Philology and Phonetics Faculty', 'Music Faculty', 'Psychiatry',
          'Oxford Internet Institute', 'Paediatrics', 'Politics & Int Relations',
          'Primary Care Health Sciences', 'Saïd Business School',
          "Women's & Reproductive Health", 'MSD', 'HUMS', 'SSD',
          'Atmos Ocean & Planet Physics']
supdeptofc= {'Condensed Matter Physics' : 'f',
             'Mathematical Institute' : 'm',
             'Astrophysics' : 'a',
             'Computer Science' : 'c',
             'Statistics' : 's'}

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

tocurls = []
prerecs = []
#include records with unknown date
for page in range(pagesnodate):
    #tocurls.append('https://ora.ox.ac.uk/?f%5Bf_degree_level%5D%5B%5D=Doctoral&f%5Bf_type_of_work%5D%5B%5D=Thesis&page=' + str(page+1) + '&per_page=' + str(rpp) + '&range%5Bf_item_year%5D%5Bmissing%5D=true&search_field=all_fields&sort=publication_date+desc')
    tocurls.append('https://ora.ox.ac.uk/?f%5Bf_thesis_degree_level%5D%5B%5D=Doctoral&f%5Bf_type_of_work%5D%5B%5D=Thesis&per_page=' + str(rpp) + '&q=&search_field=all_fields&sort=record_publication_date+desc&page=' + str(page+1))
#check date range
#for page in range(pagesdate):
#    tocurls.append('https://ora.ox.ac.uk/?f%5Bf_degree_level%5D%5B%5D=Doctoral&f%5Bf_type_of_work%5D%5B%5D=Thesis&page=' + str(page+1) + '&per_page=' + str(rpp) + '&search_field=all_fields&sort=publication_date+desc')

i = 0
for tocurl in tocurls:
    i += 1
    ejlmod3.printprogress("=", [[i, len(tocurls)], [tocurl]])
    try:
        tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
        time.sleep(3)
    except:
        print("retry %s in 180 seconds" % (tocurl))
        time.sleep(180)
        tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")

    #for div in tocpage.find_all('div', attrs = {'class' : 'response_doc'}):
    for div in tocpage.find_all('section', attrs = {'class' : 'document-metadata-header'}):
        year = False
        rec = {'jnl' : 'BOOK', 'tc' : 'T', 'keyw' : [], 'note' : [],
               'autaff' : [], 'supervisor' : []}
        for li in div.find_all('li'):
            lit = li.text.strip()
            if re.search('^[12]\d\d\d', lit):
                rec['date'] = li.text.strip()
                year = int(re.sub('.*([12]\d\d\d).*', r'\1', rec['date']))
        for h3 in div.find_all('h3'):
            rec['tit'] = h3.text.strip()
            for a in h3.find_all('a'):
                rec['link'] = 'https://ora.ox.ac.uk' + a['href']
                rec['doi'] = re.sub('.*:', '20.2000/', a['href'])
        if rec['link'] in ['https://ora.ox.ac.uk/objects/uuid:86748e44-8ac2-4883-8e20-933ee40d20f2',
                           'https://ora.ox.ac.uk/objects/uuid:49a473a0-3d35-4e2e-966a-613ac5c0406b']:
            continue
        if year:
            if year > ejlmod3.year(backwards=years):
                if ejlmod3.checkinterestingDOI(rec['doi']):
                    if not rec['doi'] in alreadyharvested:
                        prerecs.append(rec)
    print('  %4i records so far' % (len(prerecs)))

i = 0
recs = []
for rec in prerecs:
    interesting = True
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(3)
    except:
        print("retry %s in 180 seconds" % (rec['link']))
        time.sleep(180)
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['citation_pdf_url', 'citation_abstract', 'prism.keyword',
                                        'DC.subject'])
    #detailed author/supervisor informations
    for div in artpage.body.find_all('div', attrs = {'style' : 'padding-bottom:10px'}):
        (division, dep, subdep, role, orcid) = ('', '', '', '', '')
        for a in div.find_all('a', attrs = {'style' : 'text-decoration:none;'}):
            for span in a.find_all('span'):
                span.decompose()
            person = [re.sub('\n', '', a.text).strip()]
        for div2 in div.find_all('div', attrs = {'id' : ['authorsDetails0', 'contributorsDetails0']}):
            for child in div2.children:
                try:
                    cn = child.name
                    ct = child.text.strip()
                except:
                    continue
                if cn == 'dt':
                    dt = ct
                elif cn == 'dd':
                    if dt == 'Department:':
                        dep = ct
                    elif dt == 'Sub department:':
                        subdep = ct
                    elif dt == 'Division:':
                        division = ct
                    elif dt == 'Role:':
                        role = ct
                    elif dt == 'ORCID:':
                        person.append('ORCID:'+ re.sub('.*org\/', '', ct))
            #rec['note'].append('XX %s | %s | %s | %s' % (role, division, dep, subdep))
        if role in ['Supervisor', 'Supervisor, Contributor']:
            rec['supervisor'].append(person)
        elif role in ['Author', 'Author, Author']:
            rec['autaff'].append(person + [publisher])
        elif role:
            rec['note'].append('ROLE:%s ???' % (role))
        if dep in boring or division in boring or subdep in boring:
            interesting = False
        elif subdep in list(supdeptofc.keys()):
            rec['fc'] = supdeptofc[subdep]
        elif dep in list(supdeptofc.keys()):
            rec['fc'] = supdeptofc[dep]
        else:
            if division:
                if not 'division' in ['MPLS']:
                    rec['note'].append('division:::'+division)
            if dep:
                if not dep in ['Physics']:
                    rec['note'].append('dep:::'+dep)
            if subdep:
                rec['note'].append('subdep:::'+subdep)            
    #license
    ejlmod3.globallicensesearch(rec, artpage)
    #bad metadata
    if len(rec['autaff']) == 0:
        rec['autaff'] = [[ 'Mustermann, Martin' ]]
    if interesting:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['doi'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
