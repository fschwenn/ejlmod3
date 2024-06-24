# -*- coding: utf-8 -*-
#harvest thesis from Embry-Riddle Aeronautical U.
#FS: 2023-11-15

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Embry-Riddle Aeronautical U.'
pages = 2
years = 2
skipalreadyharvested = True
boring = ['Aerospace Engineering', 'Mechanical Engineering', 'Aviation Business Administration',
          'College of Aviation', 'College of Business', 'Human Factors and Behavioral Neurobiolog',
          'Aviation Business Administration', 'College of Aviation', 'College of Business',
          'College of Engineering', 'Human Factors and Behavioral Neurobiology',
          'Human Factors and Systems']


jnlfilename = 'THESES-EmbryRiddleAeronautical-%s' % (ejlmod3.stampoftoday())

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

basetocurl = 'https://commons.erau.edu/edt/index.'
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
            if name == 'h3':
                for span in child.find_all('span'):
                    date = re.sub('.*(20\d\d).*', r'\1', span.text.strip())
            elif name == 'p':
                if int(date) > ejlmod3.year(backwards=years):
                    if child.has_attr('class') and 'article-listing' in child['class']:
                        rec = {'jnl' : 'BOOK', 'tc' : 'T', 'date' : date, 'note' : [], 'supervisor' : []}
                        for a in child.find_all('a'):                    
                            rec['tit'] = a.text.strip()
                            rec['artlink'] = a['href']
                            rec['doi'] = '20.2000/EmbryRiddleAeronautical/' + re.sub('\D', '', rec['artlink'])
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
    for div in artpage.body.find_all('div', attrs = {'id' : ['advisor1', 'advisor2']}):
        for p in div.find_all('p'):
            rec['supervisor'].append( [re.sub('^Dr. ', '', p.text.strip())] )
    #degree
    for div in artpage.body.find_all('div', attrs = {'id' : 'degree_name'}):
        for p in div.find_all('p'):
            degree = p.text.strip()
            if re.search('Master', degree):
                keepit = False
                #print('    skip "%s"' % (degree))
            elif not re.search('Doctor', degree):
                rec['note'].append('DEGREE=' + degree)
    #department
    for div in artpage.body.find_all('div', attrs = {'id' : 'department'}):
        for p in div.find_all('p'):
            department = p.text.strip()
            if department in boring:
                keepit = False
                #print('    skip "%s"' % (department))
            else:
                rec['note'].append('DEPARTMENT='+department)
    #license
    ejlmod3.globallicensesearch(rec, artpage)
    for link in artpage.find_all('link', attrs = {'rel' : 'license'}):
        rec['license'] = {'url' : link['href']}
    if keepit:
        if not skipalreadyharvested or not 'doi' in rec or not rec['doi'] in alreadyharvested:
            ejlmod3.printrecsummary(rec)
            recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['artlink'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
