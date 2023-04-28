# -*- coding: utf-8 -*-
#harvest Western Ontario U. theses
#FS: 2022-03-05
#FS: 2023-04-28

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import json

publisher = 'Western Ontario U.'
jnlfilename = 'THESES-WesternOntario-%s' % (ejlmod3.stampoftoday())

pages = 2+2
skipalreadyharvested = True

basetocurl = 'https://ir.lib.uwo.ca/etd/index.'
tocextension = 'html'

boring = ['Educational Psychology', 'Art History', 'Communication',
          'African and African Diaspora Studies', 'Anthropology', 'Architecture',
          'Atmospheric Science', 'Biological Sciences', 'Economics',
          'Biomedical and Health Informatics', 'Biostatistics', 'Chemistry',
          'Communication Sciences and Disorders', 'Biomedical Sciences'
          'Engineering', 'English', 'Freshwater Sciences', 'Geosciences',
          'Health Care Informatics', 'Health Sciences', 'History',
          'Information Studies', 'Kinesiology', 'Linguistics', 'Management Science',
          'Music', 'Nursing', 'Occupational Therapy', 'Political Science', 'Psychology',
          'Public Health', 'Social Welfare', 'Sociology', 'Urban Education',
          'Curriculum and Instruction', 'Environmental Health Sciences',
          'Epidemiology', 'Geography', 'Management', 'Administrative Leadership',
          'Africology', 'Art Education', 'Art', 'Biomedical Sciences',
          'Business Administration', 'Engineering', 'Environmental & Occupational Health',
          'Information Technology Management', 'Library and Information Science',
          'Medical Informatics', 'Performing Arts', 'Social Work', 'Urban Planning',
          'Mechanical and Materials Engineering', 'Art and Visual Culture',
          'Biochemistry', 'Biology', 'Biomedical Engineering',
          'Civil and Environmental Engineering', 'Education',
          'Orthodontics', 'Pathology and Laboratory Medicine', 'Physiology and Pharmacology',
          'Health and Rehabilitation Sciences', 'Comparative Literature',
          'Epidemiology and Biostatistics', 'Geophysics', 'Health Information Science',
          'Health Promotion', 'Media Studies', 'Physical Therapy', 'Theory and Criticism',
          'Gender, Sexuality & Women’s Studies', 'Law', 'Library & Information Science',
          'Microbiology and Immunology', 'Anatomy and Cell Biology', 'Medical Biophysics',
          'Electrical and Computer Engineering', 'Philosophy', 'Statistics and Actuarial Sciences',
          'Computer Science', 'Geology', 'Neuroscience', 'Business',
          'Family Medicine', 'French', 'Gender, Sexuality & Women’s Studies',
          'Hispanic Studies', 'Library & Information Science', 'Visual Arts',
          "Women's Studies and Feminist Research",
          'Chemical and Biochemical Engineering', 'Urban Studies']
boring += ['Master of Arts', 'Master of Science', 'Master of Music', 'Master of Fine Arts',
           'Master of Clinical Dentistry', 'Master of Engineering Science',
           'Master of Laws', 'Master of Clinical Science',
           'Epidemiology and Biostatistics/Computer Science',
           'Geography and Environment',
           'Master of Library and Information Science', 'Master of Urban Planning']

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

prerecs = []
date = False
reproperlink = re.compile('ir.lib.uwo.ca\/etd\/\d')
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
            if name == 'h4':
                for span in child.find_all('span'):
                    date = span.text.strip()
            elif name == 'p':
                #year = int(re.sub('.*(20\d\d).*', r'\1', rec['date']))
                if int(date) >= ejlmod3.year() - 1*10:
                    rec = {'jnl' : 'BOOK', 'tc' : 'T', 'date' : date, 'note' : [], 'supervisor' : []}
                    for a in child.find_all('a'):
                        if reproperlink.search(a['href']):
                            rec['tit'] = a.text.strip()
                            rec['link'] = a['href']
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
        rec['note'] = [ meta['content'] ]
        if meta['content'] in boring:
            print('    skip "%s"' % (meta['content']))
            keepit = False                    
    #supervisor
    for div in artpage.body.find_all('div', attrs = {'id' : ['advisor1', 'advisor2', 'advisor3']}):
        for p in div.find_all('p'):
            rec['supervisor'] = [[ re.sub('^Dr. ', '', p.text.strip()) ]]
    if 'doi' not in rec:
        rec['doi'] = '30.3000/WesternOntario/' + re.sub('\W', '', re.sub('.*ca', '', rec['link']))
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
            elif department in ['Applied Mathematics', 'Mathematics']:
                rec['fc'] = 'm'
            elif department in ['Astronomy']:
                rec['fc'] = 'a'
            else:
                rec['note'].append(department)
    if keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['link'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
