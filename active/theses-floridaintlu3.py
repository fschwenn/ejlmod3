# -*- coding: utf-8 -*-
#harvest Florida Intl. U.
#FS: 2021-12-10
#FS: 2023-02-24

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Florida Intl. U.'

pages = 2
skipalreadyharvested = True

jnlfilename = 'THESES-FloridaIntlU-%s' % (ejlmod3.stampoftoday())

basetocurl = 'https://digitalcommons.fiu.edu/etd/index.'
tocextension = 'html'

boringdepartments = ['English', 'Electrical Engineering', 'International Relations', 'International Studies',
                     'Civil Engineering', 'Adult Education and Human Resource Development', 'Biochemistry',
                     'Biology', 'Biomedical Engineering', 'Biomedical Sciences', 'Business Administration',
                     'Chemistry', 'Computer Engineering', 'Construction Management',
                     #'Computer Science',
                     'Creative Writing', 'Curriculum and Instruction', 'Dietetics and Nutrition',
                     'Earth Systems Science', 'Economics', 'Educational Administration and Supervision',
                     'Electrical and Computer Engineering', 'Engineering Management', 'Environmental Studies',
                     'Exceptional Student Education', 'Forensic Science', 'Global and Sociocultural Studies',
                     'Higher Education', 'History', 'Hospitality Management', 'International Crime and Justice',
                     'Materials Science and Engineering', 'Mechanical Engineering', 'Music Education', 'Nursing',
                     'Political Science', 'Psychology', 'Public Affairs', 'Public Health', 'Social Welfare',
                     'Comparative Sociology', 'Earth and Environment', 'Geosciences',
                     'Higher Education Administration', 'Management Information Systems', 'Music',
                     'Public Administration', 'Religious Studies', 'Social Work',
                     'Accounting', 'Adult Education', 'Athletic Training', 'Early Childhood Education',
                     'Educational Leadership', 'Environmental Engineering', 'Finance', 'International Business',
                     'Latin American and Caribbean Studies', 'Medicine', 'Special Education',
                     'Spanish', 'Speech-Language Pathology', 'Teaching and Learning']
boringdegrees = ['Master of Arts (MA)', 'Master of Fine Arts (MFA)',
                 'Master of Science (MS)', 'Doctor of Education (EdD)',
                 'Master of Music (MM)']

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

prerecs = []
date = 9999
checked = 0
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
                if child.has_attr('class') and 'article-listing' in child['class']:
                    checked += 1
                    #year = int(re.sub('.*(20\d\d).*', r'\1', rec['date']))
                    if int(date) >= ejlmod3.year(backwards=1):
                        rec = {'jnl' : 'BOOK', 'tc' : 'T', 'date' : date, 'note' : []}
                        for a in child.find_all('a'):                    
                            rec['tit'] = a.text.strip()
                            rec['artlink'] = a['href']
                            a.replace_with('')
                            if ejlmod3.checkinterestingDOI(rec['artlink']):
                                prerecs.append(rec)
    print('   %4i records so far (checked %i)' % (len(prerecs), checked))
    tocextension = '%i.html' % (i+2)

recs = []
i = 0
for rec in prerecs:
    keepit = True
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        time.sleep(3)
    except:
        print("retry %s in 180 seconds" % (rec['artlink']))
        time.sleep(180)
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['description', 'keywords', 'bepress_citation_author',
                                        'bepress_citation_pdf_url', 'bepress_citation_doi',
                                        'bepress_citation_date'])
    #degree
    for div in artpage.body.find_all('div', attrs = {'id' : 'thesis_degree_name'}):
        for p in div.find_all('p'):
            degree = p.text.strip()
            rec['note'].append(degree)
            if degree in boringdegrees:
                print('    skip "%s"' % (degree))
                keepit = False                
    #peusoDOI
    if 'doi' not in rec:
        rec['doi'] = '20.2000/FloridaNatlU/' + re.sub('\W', '', re.sub('.*edu', '', rec['artlink']))
        rec['link'] = rec['artlink']
    #ORCID
    for div in artpage.body.find_all('div', attrs = {'id' : 'orcid_id'}):
        for p in div.find_all('p'):
            rec['autaff'][-1].append('ORCID:'+re.sub('.*org\/', '', p.text.strip()))
    rec['autaff'][-1].append(publisher)
    #license
    ejlmod3.globallicensesearch(rec, artpage)
    #discipline    
    for div in artpage.body.find_all('div', attrs = {'id' : 'thesis_degree_discipline'}):
        for p in div.find_all('p'):
            department = p.text.strip()
            rec['note'].append(department)                
            if department in boringdepartments:
                print('    skip "%s"' % (department))
                keepit = False
    if keepit:
        if skipalreadyharvested and rec['doi'] in alreadyharvested:
            print('   %s already in backup' % (rec['doi']))
        else:
            ejlmod3.printrecsummary(rec)
            recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['artlink'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
