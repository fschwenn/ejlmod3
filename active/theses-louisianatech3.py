# -*- coding: utf-8 -*-
#harvest theses from Louisiana Tech. U.
#FS: 2022-11-14

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Louisiana Tech. U.'
pages = 1
years = 2
boring = ['Educational Leadership', 'Biomedical Engineering', 'Cyberspace Engineering', 'Engineering Education',
          'Management', 'Marketing and Analysis', 'Materials and Infrastructure Systems',
          'Psychology and Behavioral Sciences', 'Psychology', 'Business Administration',
          'Curriculum, Instruction, and Leadership', 'Economics and Finance',
          'School of Accountancy', 'Civil Engineering']

jnlfilename = 'THESES-LOUSIANATECH-%s' % (ejlmod3.stampoftoday())

basetocurl = 'https://digitalcommons.latech.edu/dissertations/index.'
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
    for div in artpage.body.find_all('div', attrs = {'id' : ['advisor1', 'advisor2', 'advisor3', 'advisor4']}):
        for h4 in div.find_all('h4'):
            if re.search('visor', h4.text):
                for p in div.find_all('p'):
                    sv = re.sub('^Dr. ', '', p.text.strip())
                    if re.search(',.*,', sv):
                        rec['supervisor'].append([re.sub(',.*', '', sv)])
                    else:
                        rec['supervisor'].append([sv])
    #department
    for div in artpage.body.find_all('div', attrs = {'id' : 'department'}):
        for p in div.find_all('p'):
            department = p.text.strip()
            if department in boring:
                keepit = False
            elif department in ['Computational Analysis and Modeling', 'Computer Information SystemsDepartment of Computer Science']:
                rec['fc'] = 'c'
#            elif department in ['Department of Mathematical Sciences']:
#                rec['fc'] = 'm'
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
