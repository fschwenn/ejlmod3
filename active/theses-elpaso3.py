# -*- coding: utf-8 -*-
#harvest Texas U., El Paso theses
#FS: 2023-08-22

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import json

publisher = 'Texas U., El Paso'
jnlfilename = 'THESES-ELPASO-%s' % (ejlmod3.stampoftoday())

pages = 2
skipalreadyharvested = True
years = 2

basetocurl = 'https://scholarworks.utep.edu/open_etd/index.'
tocextension = 'html'

boring = ['Criminal Justice', 'Biological Sciences', 'Psychology',
          'Business Administration', 'Chemistry', 'Civil Engineering Infrastructure Systems',
          'Civil Engineering', 'College of Business', 'Economics', 'Educational Administration.',
          'Educational Administration', 'Educational Leadership and Administration', 'Education',
          'English Rhetoric and Composition', 'English Teaching', 'Geophysics',
          'Environmental Science and Engineering', 'Geological Sciences', 'Geology', 
          'History', 'Interdisciplinary Health Sciences', 'International Business',
          'Material Science and Engineering', 'Material Sciences And Engineering',
          'Materials Science And Engineering', 'Mechanical Engineering',
          'Metal And Material Engineering', 'Metallurgical and Materials Engineering',
          'Music Education', 'Public Health', 'Teaching , Learning and Culture',
          'Teaching, Learning and Culture', 'Teaching',
          'Theses & dissertations (College of Business)',
          'Theses & Dissertations (College of Business)']
boring += ['Master of Arts', 'Master of Science', 'Master of Music', 'Master of Fine Arts',
           'Master of Library and Information Science', 'Master of Urban Planning',
           'M.M.', 'Master of Arts in Teaching', 'Master of Education', 'M.P.H.', 'Ed.D.',
           'Ed. Leadership and Administration', 'M.S.En.E.',
           'M. S. Environmental Engineering', 'M.S.E.']

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

prerecs = []
date = False
reproperlink = re.compile('utep.edu\/open_etd\/\d')
for i in range(pages):
    tocurl = basetocurl + tocextension
    ejlmod3.printprogress("=", [[i+1, pages], [tocurl]])
    try:
        tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
        time.sleep(3)
    except:
        print("retry %s in 180 seconds" % (tocurl))
        time.sleep(180)
        tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
    for div in tocpage.body.find_all('div', attrs = {'id' : 'series-home'}):
        for child in div.children:
            try:
                name = child.name
            except:
                continue
            if name in ['h3',  'h4']:
                for span in child.find_all('span'):
                    date = span.text.strip()
                    ejlmod3.printprogress('~~~', [[date]])
            elif name == 'p':
                #year = int(re.sub('.*(20\d\d).*', r'\1', rec['date']))
                if int(date) > ejlmod3.year(backwards=years):
                    rec = {'jnl' : 'BOOK', 'tc' : 'T', 'date' : date, 'note' : [], 'supervisor' : []}
                    for a in child.find_all('a'):
                        if reproperlink.search(a['href']):
                            rec['tit'] = a.text.strip()
                            rec['link'] = a['href']
                            print('  ', a['href'])
                            a.replace_with('')                            
                            if ejlmod3.checkinterestingDOI(rec['link']):
                                prerecs.append(rec)
    print('  ', len(prerecs))
    tocextension = '%i.html' % (i+2)

recs = []
i = 0
for rec in prerecs:
    i += 1
    keepit = True
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(3)
    except:
        print("retry %s in 180 seconds" % (rec['link']))
        time.sleep(180)
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['description', 'keywords', 'bepress_citation_author',
                                        'bepress_citation_pdf_url', 'bepress_citation_doi',
                                        'bepress_citation_date'])
    rec['autaff'][-1].append(publisher)
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'bepress_citation_dissertation_name'}):
        if not meta['content'] in ['Doctor of Philosophy']:
            rec['note'].append('DEG:::'+meta['content'])
            if meta['content'] in boring:
                print('    skip "%s"' % (meta['content']))
                keepit = False                    
    #supervisor
    for div in artpage.body.find_all('div', attrs = {'id' : ['advisor1', 'advisor2', 'advisor3']}):
        for p in div.find_all('p'):
            rec['supervisor'] = [[ re.sub('^Dr. ', '', p.text.strip()) ]]
    if 'doi' not in rec:
        rec['doi'] = '30.3000/ElPaso/' + re.sub('\W', '', re.sub('.*ca', '', rec['link']))
        rec['link'] = rec['link']
    #license
    ejlmod3.globallicensesearch(rec, artpage)
    #embargo
    for div in artpage.body.find_all('div', attrs = {'id' : 'embargo_date'}):
        for p in div.find_all('p'):
            rec['embargo'] = normalize_date(p.text.strip())
    if 'pdf_url' in list(rec.keys()):
        if 'embargo' in list(rec.keys()):
            if rec['embargo'] > ejlmod3.stampoftoday():
                print('    embargo until %s' % (rec['embargo']))
            else:
                rec['FFT'] = rec['pdf_url']
        else:
            rec['FFT'] = rec['pdf_url']
    #department
    for div in artpage.body.find_all('div', attrs = {'id' : 'department'}):
        for p in div.find_all('p'):
            department = p.text.strip()
            if department in boring:
                print('    skip "%s"' % (department))
                keepit = False
            elif department in ['Applied Mathematics', 'Mathematics',
                                'Mathematical Sciences']:
                rec['fc'] = 'm'
            elif department in ['Computational Science', 'Computer Engineering',
                                'Computer Science']:
                rec['fc'] = 'c'
            elif department in ['Astronomy']:
                rec['fc'] = 'a'
            elif not department in ['Electrical Engineering', 'Engineering',
                                    'Information Technology']:
                rec['note'].append('DEP:::'+department)
    if keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['link'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)#, retfilename='retfiles_special')
