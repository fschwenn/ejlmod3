# -*- coding: utf-8 -*-
#harvest Theses from London, City U.
#FS: 2023-03-22

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

years = 2
skipalreadyharvested = True
boring = ['H Social Sciences', 'M Music and Books on Music']
boring += ['Department of Economics', 'Department of Management', 'Department of Music', 'Department of Nursing',
           'Department of Psychology', 'Department of Midwifery and Radiography', 'School of Law',
           'Research Centre for Biomedical Engineering', 'Actuarial Science, Bayes Business School',
           'Bayes Business School Faculty of Management', 'Centre for Compressor Technology',
           'Centre for Food Policy, Department of Health Sciences',
           'Centre for Food Policy, School of Health Sciences', 'Centre for Health Services Research',
           'Centre for Human Computer Interaction Design', 'City Law School', 'Composition Department',
           'Department of Civil Engineering', 'Department of Composition', 'Department of English',
           'Department of Finance', 'Department of Journalism', 'Department of Law', 'Department of Pschology',
           'Department of Research', 'Department of Sociology',
           'Department of Health Services and Management', 'Centre for Maternal and Child Health Research',
           'Department: School of Health Sciences, Division of Health Services Research and Management',
           'Division of Language and communication Science', 'Division of Optometry and Visual Sciences',
           'Faculty of Actuarial Science and Insurance', 'Faculty of Finance, Bayes Business School',
           'Faculty of Management', 'Guildhall School of Music and Drama', 'Nursing Division',
           'School of Health Sciences', 'The City Law School', 'Cass Business School',
           'Cultural Policy and Management', 'Department of Cultural Management and Policy',
           'Faculty of Actuarial Science & Insurance', 'Health Sciences', 'Human Computer Interaction Design',
           'Human-Computer Interaction Design', 'Institute of Health Science', 'Law', 'Music', 'Psychology',
           'Radiography', 'School of Engineering and Mathematical Sciences', 'Sociology',
           'Department of Performing Arts', 'Guildhall School of Music & Drama',
           'Department of Language and Communication Science']

publisher = 'London, City U.'
jnlfilename = 'THESES-CityULondon-%s' % (ejlmod3.stampoftoday())

hdr = {'User-Agent' : 'Magic Browser'}

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

j = 0
for y in range(years):
    year = ejlmod3.year(backwards=y)
    prerecs = []
    tocurl = 'https://openaccess.city.ac.uk/view/divisions/CITYPHD/%i.html' % (year)
    ejlmod3.printprogress('=', [[y+1, years], [tocurl]])
    try:
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        time.sleep(2)
        for p in tocpage.find_all('p'):
            for a in p.find_all('a'):
                if a.has_attr('href') and re.search('openaccess.city.ac.uk\/id', a['href']):
                    j += 1
                    rec = {'tc' : 'T', 'jnl' : 'BOOK', 'link' : a['href'], 'year' : str(year), 'supervisor' : [], 'note' : []}
                    rec['tit'] = a.text.strip()
                    rec['doi'] = '30.3000/CityULondon/' + re.sub('\D', '', a['href'])
                    if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
                        if ejlmod3.checkinterestingDOI(rec['doi']):
                            prerecs.append(rec)
    except:
        print('  page not found')
    print('  %4i records so far (%4i checked)' % (len(prerecs), j))

recs = []
for (i, rec) in enumerate(prerecs):
    keepit = True
    ejlmod3.printprogress('-', [[i+1, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(3)
    except:
        try:
            print('retry %s in 180 seconds' % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        except:
            print('no access to %s' % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['eprints.creators_name', 'eprints.keywords', 'eprints.abstract', #'eprints.creators_orcid', 
                                        'DC.date', 'eprints.doi', 'eprints.document_url'])
    #department
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'eprints.department'}):
        department = meta['content']
        if department in ['Department of Mathematics', 'Centre for Mathematical Science']:
            rec['fc'] = 'm'
        elif department in ['Department of Computer Science', 'Computing']:
            rec['fc'] = 'c'
        elif department in boring:
            keepit = False
        elif not department in ['Research Department']:
            rec['note'].append('DEP:::'+department)
    #subjects
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'DC.subject'}):
        subject = meta['content']
        rec['note'].append('SUBJ:::'+department)        
    if keepit:
        recs.append(rec)
        rec['autaff'][-1].append(publisher)
        ejlmod3.printrecsummary(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['doi'])
ejlmod3.writenewXML(recs, publisher, jnlfilename)

