# -*- coding: utf-8 -*-
#harvest thesis from West Virginia U.
#FS: 2022-11-10

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'West Virginia U.'
pages = 5
years = 2
skipalreadyharvested = True
boring = ['Psychology', 'History', 'Accounting', 'Agricultural and Resource Economics', 'Anesthesiology',
          'Animal and Nutritional Sciences', 'Art History', 'Biology', 'Ceramics',
          'Chemical and Biomedical Engineering', 'Chemistry', 'Civil and Environmental Engineering',
          'Communication Sciences and Disorders', 'Sport and Exercise Psychology', 
          'Counseling, Rehabilitation Counseling & Counseling Psychology', 'Special Education', 
          'Curriculum & Instruction/Literacy Studies', 'Design and Technology',
          'Division of Resource Economics & Management', 'Economics', 'English', 'Exercise Physiology',
          'Finance', 'Forensic and Investigative Science', 'Geology and Geography',
          'Industrial and Managements Systems Engineering', 'Sociology and Anthropology', 
          'Lane Department of Computer Science and Electrical Engineering', 'School of Music', 
          'Learning Sciences and Human Development', 'Management', 'Marketing',
          'Mechanical and Aerospace Engineering', 'Medicine', 'Microbiology, Immunology, and Cell Biology',
          'Occupational & Environmental Health Sciences', 'Petroleum and Natural Gas Engineering',
          'Pharmaceutical Sciences', 'Physiology, Pharmacology & Neuroscience', 'Printmaking',
          'Wood Science and Technology', 'World Languages, Literatures and Linguistics',
          'Biochemistry', 'Communication Studies', 'Division of Animal and Nutritional Sciences',
          'Division of Forestry and Natural Resources', 'Division of Plant and Soil Sciences',
          'Epidemiology', 'Family/Community Health', 'Landscape Architecture', 'Mining Engineering',
          'Pharmaceutical Systems and Policy', 'Political Science', 'Wildlife and Fisheries Resources',
          'Adult Health', 'Agricultural & Extension Education', 'Athletic Coaching Education',
          'Community Practice', 'Design Studies', 'Forest Resource Management',
          'Health Policy, Management & Leadership', 'Neurology', 'Physical Education Teacher Education',
          'Recreation, Parks and Tourism Resources', 'Reed College of Media',
          'Social and Behavioral Sciences', 'Sport Management', 'Familiy Medicine',
          'Horticulture', 'Radiology']
boring += ['MS', 'DMA', 'DNP', 'EdD', 'MA', 'MFA', 'MLA', 'MM']

jnlfilename = 'THESES-WESTVIRGINIA-%s' % (ejlmod3.stampoftoday())

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

basetocurl = 'https://researchrepository.wvu.edu/etd/index.'
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
    rec['autaff'][-1].append(publisher)
    #supervisor
    for div in artpage.body.find_all('div', attrs = {'id' : ['advisor1', 'advisor2']}):
        for p in div.find_all('p'):
            rec['supervisor'].append( [re.sub('^Dr. ', '', p.text.strip())] )
    #degree
    for div in artpage.body.find_all('div', attrs = {'id' : 'degree_name'}):
        for p in div.find_all('p'):
            degree = p.text.strip()
            if degree in boring:
                keepit = False
            elif not degree in ['PhD']:
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
            elif not department in ['Physics and Astronomy', 'Physics & Astronomy', 'Physics']:
                rec['note'].append('DEPARTMENT='+department)
    #license
    for link in artpage.find_all('link', attrs = {'rel' : 'license'}):
        rec['license'] = {'url' : link['href']}
    if keepit:
        if not skipalreadyharvested or not 'doi' in rec or not rec['doi'] in alreadyharvested:
            ejlmod3.printrecsummary(rec)
            recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['artlink'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
