# -*- coding: utf-8 -*-
#harvest theses from Toronto U.
#FS: 2019-12-12
#FS: 2023-03-18

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Toronto U.'
jnlfilename = 'THESES-TORONTO-%s' % (ejlmod3.stampoftoday())

rpp = 50
pages = 10
skipalreadyharvested = True
boringdeps = ['Adult Education and Counselling Psychology', 'Aerospace Science and Engineering',
              'Anthropology', 'Applied Psychology and Human Development', 'Biochemistry',
              'Biomedical Engineering', 'Cell and Systems Biology', 'Cinema Studies',
              'Civil Engineering', 'Classics', 'Comparative Literature', 'Criminology',
              'Curriculum, Teaching and Learning', 'Dalla Lana School of Public Health',
              'Dentistry', 'Drama', 'Earth Sciences', 'East Asian Studies', 'English',
              'Exercise Sciences', 'French Language and Literature', 'Geography', 'Law',
              'Leadership, Higher and Adult Education', 'Linguistics', 'Management', 'Policy Analysis',
              'Materials Science and Engineering', 'Mechanical and Industrial Engineering',
              'Health Policy, Management and Evaluation', 'Immunology', 'Medical Biophysics',
              'Industrial Relations and Human Resources', 'Information Studies', 'Medical Science',
              'Medieval Studies', 'Molecular and Medical Genetics', 'Molecular Genetics', 'Music',
              'Near and Middle Eastern Civilizations', 'Nursing Science', 'Nutritional Sciences',
              'Pharmaceutical Sciences', 'Pharmacology', 'Philosophy', 'Religion, Study of',
              'Social Justice Education', 'Social Work', 'Sociology', 'Spanish', 'Statistics',
              'Psychological Clinical Science', 'Psychology', 'Rehabilitation Science',
              'Physical and Environmental Sciences', 'Physiology', 'Political Science',
              'Architecture, Landscape, and Design', 'Forestry', 'Human Development and Applied Psychology',
              'Kinesiology and Physical Education', 'Laboratory Medicine and Pathobiology',
              'History and Philosophy of Science and Technology', 'History of Art', 'History',
              'Ecology and Evolutionary Biology', 'Economics', 'Electrical and Computer Engineering',
              'Chemical Engineering Applied Chemistry', 'Chemistry', 'Women and Gender Studies Institute',
              'Chemical Engineering Applied Chemistry', 'Germanic Languages and Literatures',
              'Sociology and Equity Studies in Education', 'Speech-Language Pathology', 'Italian Studies',
              'Chemical Engineering Applied Chemistry', 'Chemical Engineering Applied Chemistry']

hdr = {'User-Agent' : 'Magic Browser'}

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

prerecs = []
for i in range(pages):
    tocurl = 'https://tspace.library.utoronto.ca/handle/1807/9945/browse?rpp=' + str(rpp) + '&sort_by=2&type=dateissued&offset=' + str(i*rpp) + '&etal=-1&order=DESC'
    ejlmod3.printprogress("=", [[i+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    for tr in tocpage.body.find_all('tr'):
        for td in tr.find_all('td', attrs = {'headers' : 't2'}):
            rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'supervisor' : [], 'note' : []}
            for a in td.find_all('a'):
                rec['link'] = 'https://tspace.library.utoronto.ca' + a['href']
                rec['hdl'] = re.sub('.*handle\/', '', a['href'])
                if ejlmod3.checkinterestingDOI(rec['hdl']):
                    if not skipalreadyharvested or not rec['hdl'] in alreadyharvested:
                        prerecs.append(rec)
    print('  %4i records so far' % (len(prerecs)))
    time.sleep(15)

i = 0
recs = []
for rec in prerecs:
    i += 1
    keepit = True
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['DC.title', 'DCTERMS.issued', 'DC.subject', 'citation_pdf_url'])
    #author
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'DC.creator'}):
                if re.search('\d\d\d\d\-\d\d\d\d', meta['content']):
                    rec['autaff'][-1].append('ORCID:' + meta['content'])
                else:
                    author = re.sub(' *\[.*', '', meta['content'])
                    rec['autaff'] = [[ author ]]
    if 'autaff' in list(rec.keys()):
        rec['autaff'][-1].append(publisher)
        #license
        ejlmod3.globallicensesearch(rec, artpage)
        #other metadata
        for div in artpage.body.find_all('div', attrs = {'class' : 'item-container'}):
            for tr in div.find_all('tr'):
                for span in tr.find_all('span'):
                    spant = span.text.strip()
                for a in tr.find_all('a'):
                    at = a.text.strip()
                    #supervisor
                    if spant == 'Advisor:':
                        rec['supervisor'].append([at])
                    #department
                    elif spant == 'Department:':
                        if at == 'Astronomy and Astrophysics':
                            rec['fc'] = 'a'
                        elif at == 'Mathematics':
                            rec['fc'] = 'm'
                        elif at == 'Computer Science':
                            rec['fc'] = 'c'
                        elif at in boringdeps:
                            keepit = False
                        elif not at in ['Physics']:
                            rec['note'].append(at)
    if not 'tit' in list(rec.keys()):
        keepit = False
    if keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['hdl'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
