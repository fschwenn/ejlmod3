# -*- coding: utf-8 -*-
#harvest theses from Dartmouth College
#FS: 2023-12-19

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Dartmouth Coll.'
jnlfilename = 'THESES-DARTMOUTH-%s' % (ejlmod3.stampoftoday())
years = 2
pages = 2
skipalreadyharvested = True

boring = ['Molecular and Systems Biology', 'Biological Sciences',
          'Biochemistry and Cell Biology', 'Cancer Biology', 'Chemistry',
          'Cognitive Neuroscience', 'Ecology, Evolution, Environment and Society',
          'Psychological & Brain Sciences', 'Earth Sciences',
          'Health Policy and Clinical Practice', 'Integrative Neuroscience',
          'Microbiology and Immunology', 'Quantitative Biomedical Sciences']
tocurl = 'https://digitalcommons.dartmouth.edu/dissertations'

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []
    
prerecs = []
date = False
for page in range(pages):
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
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
                    date = span.text.strip()
                    print('  %s' % (date))
            elif name == 'p':
                if int(date) >= ejlmod3.year(backwards=years):
                    if child.has_attr('class') and 'article-listing' in child['class']:
                        rec = {'jnl' : 'BOOK', 'tc' : 'T', 'date' : date, 'note' : [], 'supervisor' : []}
                        for a in child.find_all('a'):
                            rec['tit'] = a.text.strip()
                            rec['artlink'] = a['href']
                            a.replace_with('')
                        if ejlmod3.checkinterestingDOI(rec['artlink']):
                            if not '30.3000/DartMouthCollege/' + re.sub('\D', '', rec['artlink']) in alreadyharvested:
                                prerecs.append(rec)
    tocurl = 'https://digitalcommons.dartmouth.edu/dissertations/index.%i.html' % (page+2)
    print('    %i recs so far' % (len(prerecs)))

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
    ejlmod3.metatagcheck(rec, artpage, ['description', 'keywords', 'bepress_citation_author',
                                        'bepress_citation_pdf_url',
                                        'bepress_citation_doi', 'bepress_citation_online_date'])
    #departmemt
    for div in artpage.body.find_all('div', attrs = {'id' : 'department'}):
        for p in div.find_all('p'):
            for category in re.split(' \| ', p.text.strip()):
                if category in boring:
                    keepit = False
                elif category in ['Computer Science', 'Department of Computer Science']:
                    rec['fc'] = 'c'
                elif category in ['Condensed Matter Physics']:
                    rec['fc'] = 'f'
                elif category in ['Mathematics']:
                    rec['fc'] = 'm'
                elif not category in ['Physics and Astronomy', 'Engineering Sciences']:
                    rec['note'].append('DEP:::%s' % (category))
    #supervisor
    for div in artpage.body.find_all('div', attrs = {'id' : ['advisor1', 'advisor2', 'advisor3']}):
        for p in div.find_all('p'):
            rec['supervisor'].append([ re.sub('^Dr. ', '', p.text.strip())])
    #ORCID
    for div in artpage.body.find_all('div', attrs = {'id' : 'orcid'}):
        for h2 in div.find_all('h2'):
            if re.search('Author ORCID', h2.text):
                for a in div.find_all('p'):
                    rec['autaff'][-1].append(re.sub('.*\/', 'ORCID:', a.text.strip()))
    if keepit:
        if 'doi' in rec and rec['doi'] in alreadyharvested:
            print('   %s already in backup' % (rec['doi']))
        else:
            if not 'doi' in rec:
                rec['doi'] = '30.3000/DartMouthCollege/' + re.sub('\D', '', rec['artlink'])
            rec['autaff'][-1].append(publisher)
            ejlmod3.printrecsummary(rec)
            recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['artlink'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
