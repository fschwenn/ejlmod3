# -*- coding: utf-8 -*-
#harvest UPenn, Philadelphia
#FS: 2022-11-10

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'UPenn, Philadelphia'
pages = 6
years = 2
boring = ['City & Regional Planning', 'Romance Languages', 'Cell & Molecular Biology',
          'History of Art', 'Applied Economics', 'Accounting', 'Africana Studies', 'Anthropology', 'Architecture',
          'Art & Archaeology of Mediterranean World', 'Biochemistry & Molecular Biophysics', 'Bioengineering',
          'Biology', 'Chemical and Biomolecular Engineering', 'Chemistry', 'Classical Studies', 'Communication',
          'Comparative Literature and Literary Theory', 'Demography', 'Economics', 'Education', 'English',
          'Epidemiology & Biostatistics', 'Finance', 'Genomics & Computational Biology',
          'Health Care Management & Economics', 'History and Sociology of Science', 'History', 'Immunology',
          'Legal Studies & Business Ethics', 'Linguistics', 'Management', 'Marketing', 'Chemistry',
          'Materials Science & Engineering', 'Mechanical Engineering & Applied Mechanics', 'Music', 'Neuroscience',
          'Nursing', 'Operations & Information Management', 'Pharmacology', 'Political Science', 'Psychology',
          'Social Welfare', 'Sociology', 'South Asia Regional Studies', 'History and Sociology of Science',
          'Immunology', 'Ancient History', 'Criminology', 'East Asian Languages & Civilizations',
          'Germanic Languages and Literature', 'Managerial Science and Applied Economics',
          'Near Eastern Languages & Civilizations', 'Philosophy', 'Religious Studies',
          'Earth & Environmental Science', 'Healthcare Systems', 'Insurance & Risk Management']

jnlfilename = 'THESES-UPENN-%s' % (ejlmod3.stampoftoday())

basetocurl = 'https://repository.upenn.edu/edissertations/index.'
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
                if int(date) > ejlmod3.year(backwards=years):
                    if child.has_attr('class') and 'article-listing' in child['class']:
                        rec = {'jnl' : 'BOOK', 'tc' : 'T', 'date' : date, 'note' : []}
                        for a in child.find_all('a'):                    
                            rec['tit'] = a.text.strip()
                            rec['artlink'] = a['href']
                            a.replace_with('')
                        if ejlmod3.ckeckinterestingDOI(rec['artlink']):
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
    for div in artpage.body.find_all('div', attrs = {'id' : 'advisor2'}):
        for p in div.find_all('p'):
            rec['supervisor'].append( [re.sub('^Dr. ', '', p.text.strip())] )
    #department
    for div in artpage.body.find_all('div', attrs = {'id' : 'department'}):
        for p in div.find_all('p'):
            department = p.text.strip()
            if department in boring:
                keepit = False
            elif department in ['Computer Science', 'Computer and Information Science']:
                rec['fc'] = 'c'
            elif department in ['Applied Mathematics', 'Mathematics']:
                rec['fc'] = 'm'
                rec['autaff'][-1].append('Pennsylvania U., Dept. Math.')
            elif department in ['Statistics']:
                rec['fc'] = 's'
                rec['autaff'][-1].append('Pennsylvania U., Dept. Math.')
            elif department in ['Physics and Astronomy', 'Physics & Astronomy']:
                rec['autaff'][-1].append('Pennsylvania U.')
            else:
                rec['note'].append(department)
    if keepit:
        if len(rec['autaff'][-1]) == 1:
            rec['autaff'][-1].append(publisher)
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['artlink'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
