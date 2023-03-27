# -*- coding: utf-8 -*-
#harvest Wisconsin U., Milwaukee theses
#FS: 2021-12-17
#FS: 2023-03-26


import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
from inspire_utils.date import normalize_date


publisher = 'Wisconsin U., Milwaukee'
jnlfilename = 'THESES-WisconsinMilwaukee-%s' % (ejlmod3.stampoftoday())

pages = 2+1
skipalreadyharvested = True

basetocurl = 'https://dc.uwm.edu/etd/index.'
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
          'Business Administration', 'Engineering', 'Environmental &amp; Occupational Health',
          'Information Technology Management', 'Library and Information Science',
          'Medical Informatics', 'Performing Arts', 'Social Work', 'Urban Planning',
          'Urban Studies']
boring += ['Master of Arts', 'Master of Science', 'Master of Music', 'Master of Fine Arts',
           'Master of Library and Information Science', 'Master of Urban Planning']

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

prerecs = []
date = False
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
                if int(date) >= ejlmod3.year() - 1:
                    rec = {'jnl' : 'BOOK', 'tc' : 'T', 'date' : date, 'note' : []}
                    for a in child.find_all('a'):
                        if not re.search('(viewcontent.cgi|proquest.com|network.bepress.com)', a['href']):
                            rec['tit'] = a.text.strip()
                            rec['artlink'] = a['href']
                            a.replace_with('')
                            if ejlmod3.checkinterestingDOI(rec['artlink']):
                                prerecs.append(rec)
    print('  ', len(prerecs))
    tocextension = '%i.html' % (i+2)

recs = []
i = 0
for rec in prerecs:
    i += 1
    keepit = True
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
    rec['autaff'][-1].append(publisher)
    #thesis type
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'bepress_citation_dissertation_name'}):
                rec['note'] = [ meta['content'] ]
                if meta['content'] in boring:
                    print('    skip "%s"' % (meta['content']))
                    keepit = False
                else:
                    rec['note'].append(meta['content'])
    #supervisor
    for div in artpage.body.find_all('div', attrs = {'id' : 'advisor1'}):
        for p in div.find_all('p'):
            rec['supervisor'] = [[ re.sub('^Dr. ', '', p.text.strip()) ]]
    for div in artpage.body.find_all('div', attrs = {'id' : 'advisor2'}):
        for p in div.find_all('p'):
            rec['supervisor'].append( [re.sub('^Dr. ', '', p.text.strip())] )
    if 'doi' not in rec:
        rec['doi'] = '30.3000/WisconsinMilwaukee/' + re.sub('\W', '', re.sub('.*edu', '', rec['artlink']))
        rec['link'] = rec['artlink']
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
            else:
                rec['note'].append(department)
    if keepit:
        if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
            ejlmod3.printrecsummary(rec)
            recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['artlink'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
