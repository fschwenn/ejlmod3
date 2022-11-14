# -*- coding: utf-8 -*-
#harvest thesis from U. South Carolina, Columbia
#FS: 2022-11-10


import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'U. South Carolina, Columbia'
pages = 3
years = 2
boring = ['Educational Studies', 'Health Promotion, Education and Behavior',
          'English Language and Literatures', 'Exercise Science', 'Anthropology', 'Biological Sciences',
          'Biomedical Engineering', 'Biomedical Science', 'Chemical Engineering', 'Chemistry and Biochemistry',
          'Civil and Environmental Engineering', 'College of Pharmacy', 'Educational Leadership and Policies',
          'Electrical Engineering', 'Environmental Health Sciences', 'Epidemiology and Biostatistics',
          'Geography', 'Health Services and Policy Management', 'Languages, Literatures and Cultures',
          'Mechanical Engineering', 'Moore School of Business', 'Philosophy', 'Psychology',
          'School of Information Science', 'School of Journalism and Mass Communications', 'School of Music',
          'Sociology', 'College of Nursing', 'Communication Sciences and Disorders', 'Comparative Literature',
          'Criminology and Criminal Justice', 'Earth and Ocean Sciences', 'History', 'Linguistics',
          'Pharmacology, Physiology and Neuroscience', 'Physical Education', 'Political Science',
          'School of Hotel, Restaurant and Tourism Management', 'Marine Science']
remaster = re.compile('(Master of|Master in|Bachelor in|Bachelor of|Masters of|M\.S\.|M\.A\.|Doctor of Education|M\.F\.|MFA|M\.R.|Doctor of Music)')
redoctor = re.compile('(Doctor of Philosophy|PhD)')

jnlfilename = 'THESES-SOUTHCAROLINA-%s' % (ejlmod3.stampoftoday())

basetocurl = 'https://scholarcommons.sc.edu/etd/index.'
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
    #degree
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'bepress_citation_dissertation_name'}):
        degree = meta['content']
        if remaster.search(degree):
            keepit = False
        elif not redoctor.search(degree):
            rec['note'].append('DEGREE=' + degree)
    #department
    for div in artpage.body.find_all('div', attrs = {'id' : 'department'}):
        for p in div.find_all('p'):
            department = p.text.strip()
            if department in boring:
                keepit = False
            elif department in ['Computer Science']:
                rec['fc'] = 'c'
            elif department in ['Astronomy']:
                rec['fc'] = 'a'
            elif department in ['Applied Mathematics', 'Mathematics']:
                rec['fc'] = 'm'
            elif department in ['Statistics']:
                rec['fc'] = 's'
            elif department in ['Physics and Astronomy', 'Physics & Astronomy', 'Physics']:
                rec['autaff'][-1].append('South Carolina U.')
            else:
                rec['note'].append(department)
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
