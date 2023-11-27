# -*- coding: utf-8 -*-
#harvest theses from U. Tennessee, Knoxville
#FS: 2022-03-25
#FS: 2023-03-25

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
from inspire_utils.date import normalize_date

publisher = 'U. Tennessee, Knoxville'
jnlfilename = 'THESES-TennesseeKnoxville-%s' % (ejlmod3.stampoftoday())

pages = 6
skipalreadyharvested = True

basetocurl = 'https://trace.tennessee.edu/utk_graddiss/index.'
tocextension = 'html'

boring = ['Psychology', 'English', 'Ecology and Evolutionary Biology', 'Life Sciences',
          'Nuclear Engineering', 'Materials Science and Engineering', 'Public Health', 
          'Anthropology', 'Educational Psychology', 'Environmental and Soil Sciences',
          'Environmental Engineering', 'Geography', 'Kinesiology and Sport Studies',
          'Nutrition', 'Philosophy', 'Retail, Hospitality, and Tourism Management',
          'Spanish', 'Biomedical Engineering', 'Chemical Engineering', 'Child and Family Studies',
          'Communication and Information', 'Computer Engineering', 'Political Science', 
          'Educational Psychology and Research', 'Engineering Science', 'Food Science', 'History',
          'Kinesiology', 'Modern Foreign Languages', 'Natural Resources', 'Nutritional Sciences',
          'Teacher Education', 'Data Science and Engineering', 'Economics', 'Nursing',
          'Electrical Engineering', 'Microbiology', 'Plant, Soil and Environmental Sciences', 
          'Social Work', 'Business Administration', 'Civil Engineering', 'Education',
          'Higher Education Administration', 'School Psychology', 'Industrial Engineering', 
          'Biochemistry and Cellular and Molecular Biology', 'Counselor Education', 'Chemistry',
          'Energy Science and Engineering', 'Mechanical Engineering', 'Business Analytics',
          'Instructional Technology and Educational Studies', 'Management Science',
          'Plants, Soils, and Insects', 'Animal Science', 'Biosystems Engineering',
          'Entomology and Plant Pathology', 'Entomology, Plant Pathology and Nematology',
          'Experimental Psychology', 'Plant Sciences', 'Aerospace Engineering', 'Geology',
          'Communication', 'Counseling', 'Food Science and Technology', 'French', 'German',
          'Industrial and Organizational Psychology', 'Information Sciences', 'American History',
          'Polymer Engineering', 'Sport Studies', 'Wildlife and Fisheries Science',
          'Educational Administration', 'Sociology', 'Comparative and Experimental Medicine',
          'Botany', 'Exercise and Sport Sciences', 'Health and Human Sciences', 'Exercise Science',
          ']Human Ecology', 'Human Resource Management', 'Speech and Hearing Science']
boring += ['Master of Arts', 'Master of Science', 'Master of Music', 'Master of Fine Arts',           
           'Master of Library and Information Science', 'Master of Urban Planning',
           'Doctor of Education']

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

prerecs = []
date = False
tocextension = 'html'
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
    for div in tocpage.body.find_all('div'):
        if div.has_attr('class') and re.search('^lockss_\d', div['class'][0]):
            for child in div.children:
                try:
                    name = child.name
                except:
                    continue
                if name in ['h3', 'h4']:
                    for span in child.find_all('span'):
                        date = span.text.strip()
                elif name == 'p':
                    #year = int(re.sub('.*(20\d\d).*', r'\1', rec['date']))
                    if int(date) >= ejlmod3.year() - 1*100:
                        rec = {'jnl' : 'BOOK', 'tc' : 'T', 'date' : date, 'note' : [], 'supervisor' : []}
                        for a in child.find_all('a'):
                            if not re.search('(viewcontent.cgi|proquest.com|network.bepress.com)', a['href']):
                                rec['tit'] = a.text.strip()
                                rec['artlink'] = a['href']
                                a.replace_with('')
                                if ejlmod3.checkinterestingDOI(rec['artlink']):
                                    prerecs.append(rec)
    print('  %4i records so far' % len(prerecs))
    tocextension = '%i.html' % (i+2)

recs = []
i = 0
for rec in prerecs:
    i += 1
    keepit = True
    department = False
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        time.sleep(3)
    except:
        print("retry %s in 180 seconds" % (rec['artlink']))
        time.sleep(180)
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['description', 'keywords', 'bepress_citation_pdf_url',
                                        'bepress_citation_doi', 'bepress_citation_date'])
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #thesis type
            if meta['name'] == 'bepress_citation_dissertation_name':
                rec['note'] = [ meta['content'] ]
                if meta['content'] in boring:
                    print('    skip "%s"' % (meta['content']))
                    keepit = False
                else:
                    rec['note'].append(meta['content'])
            #author
            elif meta['name'] == 'bepress_citation_author':
                rec['autaff'] = [[ meta['content'] ]]
                for div2 in artpage.body.find_all('div', attrs = {'id' : 'author1_orcid'}):
                    for p in div2.find_all('p'):
                        rec['autaff'][-1].append('ORCID:'+re.sub('.*org\/', '', p.text))
    #supervisor
    for div in artpage.body.find_all('div', attrs = {'id' : 'advisor1'}):
        for p in div.find_all('p'):
            rec['supervisor'] = [[ re.sub('^Dr. ', '', p.text.strip()) ]]
    #for div in artpage.body.find_all('div', attrs = {'id' : 'advisor2'}):
    #    for p in div.find_all('p'):
    #        rec['supervisor'].append( [re.sub('^Dr. ', '', p.text.strip())] )
    if 'doi' not in rec:
        rec['doi'] = '30.3000/TennesseeKoxville/' + re.sub('\W', '', re.sub('.*edu', '', rec['artlink']))
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
            elif department == 'Mathematics':
                rec['fc'] = 'm'
            elif department == 'Computer Science':
                rec['fc'] = 'c'
            else:
                rec['note'].append(department)
    if department and department == 'Physics':
        rec['autaff'][-1].append('Tennessee U.')
    else:
        rec['autaff'][-1].append(publisher)
    if keepit:
        if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
            ejlmod3.printrecsummary(rec)
            recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['artlink'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
