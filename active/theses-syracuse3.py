# -*- coding: utf-8 -*-
#harvest Syracuse U. theses
#FS: 2021-08-13
#FS: 2023-04-05


import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

pages = 2
skipalreadyharvested = True

publisher = 'Syracuse U.'
jnlfilename = 'THESES-SYRACUSE-%s' % (ejlmod3.stampoftoday())

basetocurl = 'https://surface.syr.edu/etd/index.'
tocextension = 'html'

boringdepartments = ['Biology', 'Mechanical and Aerospace Engineering', 'Chemistry',
                     'Psychology',
                     'Teaching and Leadership', 'Political Science', 'Design',
                     'Cultural Foundations of Education', 'Reading and Language Arts',
                     'Mass Communications', 'Earth Sciences', 'Anthropology',
                     'School of Information Studies', 'Religion', 'Philosophy',
                     'Marriage and Family Therapy', 'Human Development and Family Science',
                     'Geography', 'Counseling and Human Services', 'Sociology',
                     'Social Sciences', 'History', 'Entrepreneurship and Emerging Enterprises',
                     'English', 'Communication Sciences and Disorders', 'Writing Program',
                     'Higher Education', 'Finance', 'Business Administration',
                     'Biomedical and Chemical Engineering', 'Economics',
                     'Civil and Environmental Engineering', 'Public Administration',
                     'Child and Family Studies', 'Instructional Design, Development and Evaluation',
                     'Media Studies', 'Science Teaching', 'Communication and Rhetorical Studies',
                     'African American Studies', 'Public Relations', 'Accounting',
                     'Information Science and Technology', 'Exercise Science',
                     'Nutrition Science and Dietetics', 'Marketing', 'Communications Management',
                     'Information Management and Technology', 'Management', 
                     'Languages, Literatures, and Linguistics', 'Supply Chain Management']

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
    #supervisor
    for div in artpage.body.find_all('div', attrs = {'id' : 'advisor1'}):
        for p in div.find_all('p'):
            rec['supervisor'] = [[ re.sub('^Dr. ', '', p.text.strip()) ]]
    for div in artpage.body.find_all('div', attrs = {'id' : 'advisor2'}):
        for p in div.find_all('p'):
            rec['supervisor'].append( [re.sub('^Dr. ', '', p.text.strip())] )
    if 'doi' not in rec:
        rec['doi'] = '20.2000/Syracuse' + re.sub('\W', '', re.sub('.*edu', '', rec['artlink']))
        rec['link'] = rec['artlink']
    #department
    for div in artpage.body.find_all('div', attrs = {'id' : 'department'}):
        for p in div.find_all('p'):
            department = p.text.strip()
            if department in boringdepartments:
                print('    skip "%s"' % (department))
                ejlmod3.adduninterestingDOI(rec['artlink'])
            else:
                if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
                    rec['note'].append(department)
                    ejlmod3.printrecsummary(rec)
                    recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
