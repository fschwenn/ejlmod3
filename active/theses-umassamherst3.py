# -*- coding: utf-8 -*-
#harvest thesis from UMass Amherst
#FS: 2022-11-10


import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'UMass Amherst'
jnlfilename = 'THESES-UMassAmherst-%s' % (ejlmod3.stampoftoday())

pages = 1
years = 2
skipalreadyharvested = True
boring = ['Afro-American Studies', 'Animal Biotechnology & Biomedical Sciences', 'Anthropology',
          'Biomedical Engineering', 'Chemical Engineering', 'Chemistry', 'Civil and Environmental Engineering',
          'Civil Engineering', 'Communication Disorders', 'Communication', 'Comparative Literature',
          'Economics', 'Education', 'Electrical and Computer Engineering', 'English',
          'Environmental Conservation', 'Food Science', 'Geosciences', 'Hispanic Literatures & Linguistics',
          'History', 'Hospitality & Tourism Management', 'Industrial Engineering & Operations Research',
          'Kinesiology', 'Linguistics', 'Management', 'Microbiology', 'Molecular and Cellular Biology',
          'Music', 'Neuroscience and Behavior', 'Nursing', 'Organismic and Evolutionary Biology', 'Philosophy',
          'Plant Biology', 'Political Science', 'Polymer Science and Engineering', 'Psychology',
          'Public Health', 'Regional Planning', 'Resource Economics', 'School Psychology', 'Sociology',
          'Wildlife & Fisheries Conservation', 'American Studies', 'Biochemistry', 'Biology', 
          'Education (also CAGS)', 'Education; Children and Family Studies', 'Isenberg School of Management',
          'Education; Language, Literacy and Culture', 'Educational Policy and Leadership',
          'Education Policy, Research and Administration; Educational Policy and Leadership',
          'Education; Teacher Education & Curriculum Studies', 'English - American Studies', 'Entomology',
          'Forest Resources', 'German and Scandinavian Studies', 'Germanic Languages & Literatures',
          'Hispanic Literatures and Linguistics', 'Industrial Engineering and Operations Research',          
          'Languages, Literatures, and Cultures; Hispanic Literatures and Linguistics',
          'Lusophone Literatures and Cultures', 'Marine Sciences and Technology',
          'Mechanical and Industrial Engineering', 'Mechanical Engineering', 'Plant and Soil Sciences',
          'Plant, Soil & Insect Sciences', 'Psychology; Clinical Psychology',
          'Psychometric Methods, Education Statistics and Research Methods', 'Sport Management',
          'Wildlife and Fisheries Conservation', 'Animal Biotechnology and Biomedical Sciences',
          'Biostatistics and Epidemiology', 'Clinical Psychology',
          'Educational Planning, Research, and Administration', 'Language, Literacy, & Culture',
          'Educational Policy and Leadership; International Education',
          'Educational Policy, Research, and Administration', 'Education; Educational Policy and Leadership',
          'Education, Educational Policy Research, and Administration Research',
          'Education; Education Policy, Research, and Administration', 'Education; Research and Evaluation Methods',
          'Education; Student Development', 'Education; Teacher Education & School Improvement',
          'Epidemiology and Biostatistics', 'Isenberg School of Management; Operations Management',          
          'Mechanical and Industrial Engineering; Industrial Engineering and Operations Research',
          'Neuroscience & Behavior', 'Organismic and Evolutionary Biology; Entomology',
          'Research and Evaluating Methods', 'Social Justice Education',
          'Teacher Education and Curriculum Studies; Language, Literacy, & Culture',
          'Teacher Education and Curriculum Studies', 'Teacher Education']

basetocurl = 'https://scholarworks.umass.edu/dissertations_2/index.'
tocextension = 'html'

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

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
    for div in tocpage.body.find_all('div'):
        if div.has_attr('class') and re.search('locks', div['class'][0]):
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
    if 'doi' in rec:
        rec['doi'] = re.sub('.*doi.org\/', '', rec['doi'])
    #supervisor
    for div in artpage.body.find_all('div', attrs = {'id' : 'advisor1'}):
        for p in div.find_all('p'):
            rec['supervisor'] = [[ re.sub('^Dr. ', '', p.text.strip()) ]]
    for div in artpage.body.find_all('div', attrs = {'id' : 'advisor2'}):
        for p in div.find_all('p'):
            rec['supervisor'].append( [re.sub('^Dr. ', '', p.text.strip())] )
    #ORCID
    for div in artpage.body.find_all('div', attrs = {'id' : 'orcid'}):
        for h4 in div.find_all('h4'):
            if re.search('uthor', h4.text):
                for p in div.find_all('p'):
                    if re.search('orcid', p.text):
                        rec['autaff'][-1].append(re.sub('.*orcid.*?\/', 'ORCID:', p.text.strip()))
                    else:
                        rec['autaff'][-1].append('ORCID:'+p.text.strip())
            else:
                print(div)
    #keywords
    for div in artpage.body.find_all('div', attrs = {'id' : 'bp_categories'}):
        for p in div.find_all('p'):
            rec['keyw'] = re.split(' *\| *', p.text.strip())
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
                rec['autaff'][-1].append('UMASS, Amherst, Dept. Math. Stat.')
            elif department in ['Statistics']:
                rec['fc'] = 's'
                rec['autaff'][-1].append('UMASS, Amherst, Dept. Math. Stat.')
            elif department in ['Physics and Astronomy', 'Physics & Astronomy', 'Physics']:
                rec['autaff'][-1].append('Massachusetts U., Amherst')
            else:
                rec['note'].append(department)
    #license
    for link in artpage.find_all('link', attrs = {'rel' : 'license'}):
        rec['license'] = {'url' : link['href']}
    if keepit:
        if len(rec['autaff'][-1]) == 1:
            rec['autaff'][-1].append(publisher)            
        if skipalreadyharvested and 'doi' in rec and rec['doi'] in alreadyharvested:
            print('   %s already in backup' % (rec['doi']))
        else:
            ejlmod3.printrecsummary(rec)
            recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['artlink'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
