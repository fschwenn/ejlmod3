# -*- coding: utf-8 -*-
#harvest thesis from U. Louisville
#FS: 2022-11-10

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'U. Louisville'
pages = 3
years = 2
boring = ['Criminal Justice', 'Mechanical Engineering', 'Educational Leadership, Evaluation and Organizational Development',
          'Fine Arts', 'Anatomical Sciences and Neurobiology', 'Biochemistry and Molecular Biology', 'Bioengineering',
          'Bioinformatics and Biostatistics', 'Biology', 'Chemical Engineering', 'Chemistry',
          'Civil and Environmental Engineering', 'Counseling and Human Development',
          'Elementary, Middle & Secondary Teacher Education', 'English', 'Entrepreneurship',
          'Epidemiology and Population Health', 'Fine Arts', 'Health and Sport Sciences',
          'Health Promotion and Behavioral Sciences', 'Humanities', 'Interdisciplinary and Graduate Studies',
          'Microbiology and Immunology', 'Music Composition', 'Nursing', 'Pan-African Studies',
          'Pharmacology and Toxicology', 'Physiology and Biophysics', 'Psychological and Brain Sciences', 'Social Work',
          'Sociology', 'Special Education, Early Childhood & Prevention Science', 'Special Education', 'Studio Arts',
          'Theatre Arts', 'Urban and Public Affairs', 'Environmental and Occupational Health Sciences',
          'Health Management and Systems Sciences', 'Industrial Engineering', 'Music Education',
          'College of Business', 'College of Education and Human Development',
          'Department of Early Childhood and Elementary Education',
          'Department of Educational and Counseling Psychology, Counseling, and College Student Personnel',
          'Department of Educational and Counseling Psychology', 'Department of Education',
          'Department of Interdisciplinary Studies', 'Department of Justice Administration',
          'Department of Leadership, Foundations, and Human Resource Education',
          'Department of Teaching and Learning', 'Middle and Secondary Education', 'Oral Health and Rehabilitation']
boring += ['M.S.', 'M.A.', 'Ed. D.', 'M. Eng.', 'M.F.A.', 'M.M.', ' M.P.A.', 'M.M. Ed.', 'M. Ed.']

jnlfilename = 'THESES-LOUISVILLE-%s' % (ejlmod3.stampoftoday())

basetocurl = 'https://ir.library.louisville.edu/etd/index.'
tocextension = 'html'

prerecs = []
date = False
for i in range(pages):
    tocurl = basetocurl + tocextension
    ejlmod3.printprogress('=', [[i+1, pages], [tocurl]])
    try:
        tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
        time.sleep(3)
    except:
        print("retry %s in 180 seconds" % (tocurl))
        time.sleep(180)
        tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
    for div in tocpage.body.find_all('div'):
        if div.has_attr('class') and re.search('locks', div['class'][0]):
            for child in div.children:
                try:
                    name = child.name
                except:
                    continue
                if name in ['h4', 'h3']:
                    for span in child.find_all('span'):
                        date = span.text.strip()
                elif name == 'p':
                    if int(date) > ejlmod3.year(backwards=years):
                        if child.has_attr('class') and 'article-listing' in child['class']:
                            rec = {'jnl' : 'BOOK', 'tc' : 'T', 'date' : date, 'note' : []}
                            for a in child.find_all('a'):                    
                                rec['tit'] = a.text.strip()
                                rec['artlink'] = a['href']
                                a.replace_with('')
                            if ejlmod3.checkinterestingDOI(rec['artlink']):
                                prerecs.append(rec)
    print('  ', len(prerecs))
    tocextension = '%i.html' % (i+2)

i = 0
recs = []
for rec in prerecs:
    keepit = True
    i += 1
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        time.sleep(3)
    except:
        print("retry %s in 180 seconds" % (rec['artlink']))
        time.sleep(180)
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['description', 'bepress_citation_author', 'bepress_citation_pdf_url', 'bepress_citation_doi',
                                        'bepress_citation_online_date'])
    #supervisor
    for div in artpage.body.find_all('div', attrs = {'id' : 'advisor1'}):
        for p in div.find_all('p'):
            rec['supervisor'] = [[ re.sub('^Dr. ', '', p.text.strip()) ]]
    #degree
    for div in artpage.body.find_all('div', attrs = {'id' : 'degree_name'}):
        for p in div.find_all('p'):
            degree = p.text.strip()
            if degree in boring:
                keepit = False
            elif not degree in ['PhD', 'Ph. D.']:
                rec['note'].append('DEGREE=' + degree)
    #keywords
    for div in artpage.body.find_all('div', attrs = {'id' : 'keywords'}):
        for p in div.find_all('p'):
            rec['keyw'] = re.split('; ', p.text.strip())
    #department
    for div in artpage.body.find_all('div', attrs = {'id' : ['department_current', 'department']}):
        for p in div.find_all('p'):
            department = p.text.strip()
            if department in boring:
                keepit = False
            elif department in ['Computer Science', 'Computer Engineering and Computer Science']:
                rec['fc'] = 'c'
            elif department in ['Astronomy']:
                rec['fc'] = 'a'
            elif department in ['Applied Mathematics', 'Mathematics']:
                rec['fc'] = 'm'
            elif department in ['Statistics']:
                rec['fc'] = 's'
            elif department in ['Physics and Astronomy', 'Physics & Astronomy', 'Physics']:
                rec['autaff'][-1].append('Lousville U.')
            else:
                rec['note'].append('DEPARTMENT='+department)
    #license
    for link in artpage.find_all('link', attrs = {'rel' : 'license'}):
        rec['license'] = {'url' : link['href']}
    if keepit:
        if len(rec['autaff'][-1]) == 1:
            rec['autaff'][-1].append(publisher)
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['artlink'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
