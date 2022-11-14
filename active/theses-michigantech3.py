# -*- coding: utf-8 -*-
#harvest theses from Michigan Tech. U.
#FS: 2022-11-10

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Michigan Tech. U.'
pages = 4
years = 2
boring = ['Department of Mechanical Engineering-Engineering Mechanics',
          'Department of Geological and Mining Engineering and Sciences',
          'College of Business', 'College of Forest Resources and Environmental Science',
          'Department of Biological Sciences', 'Department of Biomedical Engineering',
          'Department of Chemical Engineering', 'Department of Chemistry',
          'Department of Civil and Environmental Engineering',
          'Department of Civil, Environmental, and Geospatial Engineering',
          'Department of Cognitive and Learning Sciences',
          'Department of Electrical and Computer Engineering', 'Department of Humanities',
          'Department of Kinesiology and Integrative Physiology',
          'Department of Materials Science and Engineering',
          'School of Forest Resources and Environmental Science',
          'Department of Social Sciences']
remaster = re.compile('(Master of|Master in|Bachelor in|Bachelor of|Masters of|M\.S\.|M\.A\.|Doctor of Education|M\.F\.|MFA|M\.R.)')
redoctor = re.compile('(Doctor of Philosophy|PhD)')

jnlfilename = 'THESES-MICHIGANTECH-%s' % (ejlmod3.stampoftoday())

basetocurl = 'https://digitalcommons.mtu.edu/etdr/index.'
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
                        rec = {'jnl' : 'BOOK', 'tc' : 'T', 'date' : date, 'note' : [], 'supervisor' : []}
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
    for div in artpage.body.find_all('div', attrs = {'id' : ['advisor1', 'advisor2', 'advisor3', 'advisor4']}):
        for h4 in div.find_all('h4'):
            if re.search('visor', h4.text):
                for p in div.find_all('p'):
                    sv = re.sub('^Dr. ', '', p.text.strip())
                    if re.search(',.*,', sv):
                        rec['supervisor'].append([re.sub(',.*', '', sv)])
                    else:
                        rec['supervisor'].append([sv])
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
            elif department in ['Department of Computer Science', 'Department of Applied Computing']:
                rec['fc'] = 'c'
            elif department in ['Department of Mathematical Sciences']:
                rec['fc'] = 'm'
            elif not department in ['Department of Physics']:
                rec['note'].append(department)
    #license
    for link in artpage.find_all('link', attrs = {'rel' : 'license'}):
        rec['license'] = {'url' : link['href']}
    if keepit:
        rec['autaff'][-1].append(publisher)
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['artlink'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
