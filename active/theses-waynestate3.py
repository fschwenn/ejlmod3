# -*- coding: utf-8 -*-
#harvest Wayne State U. theses
#FS: 2020-04-29
#FS: 2022-11-09


import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Wayne State U., Detroit'
pages = 2
years = 2
boring = ['Civil and Environmental Engineering', 'Industrial and Manufacturing Engineering',
          'Biological Sciences', 'Sociology', 'Molecular Biology and Genetics',
          'Political Science', 'Communication', 'Cancer Biology', 'Anthropology',
          'Biomedical Engineering', 'Chemical Engineering and Materials Science', 'Chemistry',
          'Classical and Modern Languages, Literatures, and Cultures', 'English', 
          'Curriculum and Instruction', 'Economics', 'Educational Leadership and Policy',
          'Health Education', 'History', 'Immunology and Microbiology', 'Nursing',
          'Nutrition and Food Science', 'Pharmaceutical Sciences', 'Pharmacology',
          'Physiology', 'Psychology', 'Social Work', 'Anatomy and Cell Biology', 'Theatre',
          'Biochemistry and Molecular Biology', 'Communication Sciences and Disorders',
          'Counselor Education', 'Educational Psychology', 'Education Evaluation and Research',
          'Instructional Technology', 'Materials Engineering', 'Mechanical Engineering',
          'Medical Physics', 'Otolaryngology, Head and Neck Surgery', 'Pathology',
          'Psychiatry and Behavioral Neurosciences', 'Science Education', 'Special Education']          
          

jnlfilename = 'THESES-WAYNESTATE-%s' % (ejlmod3.stampoftoday())

basetocurl = 'https://digitalcommons.wayne.edu/oa_dissertations/index.'
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
    rec['autaff'][-1].append(publisher)
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
            elif department in ['Computer Science']:
                rec['fc'] = 'c'
            elif department in ['Mathematics']:
                rec['fc'] = 'm'
            elif not department in ['Physics and Astronomy']:
                rec['note'].append(department)
    if keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['artlink'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
