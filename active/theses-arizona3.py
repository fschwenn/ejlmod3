# -*- coding: utf-8 -*-
#harvest theses from Arizona State U., Tempe 
#FS: 2019-12-12

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Arizona State U., Tempe'
jnlfilename = 'THESES-ARIZONA_STATE-%s' % (ejlmod3.stampoftoday())
rpp = 50
startyear = ejlmod3.year(backwards=2)
stopyear = ejlmod3.year()
pages = 10
skipalreadyharvested = True

boring = ['Criminology and Criminal Justice', 'Psychology', 'Higher and Postsecondary Education', 'Biomedical Informatics',
          'International Letters and Cultures', 'Agribusiness', 'Anthropology',
          'Applied mathematics for the life and social sciences', 'Applied Mathematics for the Life and Social Sciences',
          'Architecture', 'Art History', 'Asian Languages and Civilizations', 'Biochemistry', 'Bioinformatics',
          'Biological design', 'Biological Design', 'Biology', 'Biomedical Engineering', 'Biomedical informatics',
          'Black history', 'Built Environment', 'Business administration', 'Business Administration',
          'Chemical engineering', 'Chemical Engineering', 'Chemistry', 'Civil engineering',
          'Civil, environmental and sustainable engineering', 'Civil, Environmental and sustainable engineering',
          'Civil, Environmental and Sustainable Engineering', 'Communication studies', 'Communication Studies',
          'Communication', 'Community resources and development', 'Community Resources and Development', 'Composition',
          'Computer engineering', 'Computer Engineering', 'Construction Management', 'Counseling psychology',
          'Counseling Psychology', 'Criminology and criminal justice', 'Cultural anthropology',
          'Curriculum and Instruction', 'Design, environment and the arts', 'Design, Environment and the Arts',
          'Design', 'East Asian Languages and Civilizations', 'Ecology', 'Economics', 'Economic theory',
          'Educational Administration and Supervision', 'Educational leadership and policy studies',
          'Educational Leadership and Policy Studies', 'Educational policy and evaluation',
          'Educational Policy and Evaluation', 'Educational psychology', 'Educational Psychology', 'Educational technology',
          'Educational Technology', 'Electrical engineering', 'Electrical Engineering', 'Engineering', 'English',
          'Entomology', 'Environmental and Resource Management', 'Environmental social science',
          'Environmental Social Science', 'Environment and the Arts', 'Evolutionary Biology',
          'Exercise and nutritional sciences', 'Exercise and Nutritional Sciences', 'Exercise and Wellness',
          'Exploration systems design', 'Family and human development', 'Family and Human Development', 'Gender studies',
          'Gender Studies', 'Genetics', 'Geography', 'Geological sciences', 'Geological Sciences', 'Global health',
          'Global Health', 'History', 'Human and social dimensions of science and technology',
          'Human and Social Dimensions of Science and Technology', 'Human Systems Engineering', 'Industrial engineering',
          'Industrial Engineering', 'Interdisciplinary Studies', 'International letters and cultures',
          'Journalism and mass communication', 'Journalism and Mass Communication', 'Justice studies', 'Justice Studies',
          'Justice Studies,', 'Leadership and innovation', 'Leadership and Innovation',
          'Learning, literacies and technologies', 'Learning, Literacies and Technologies', 'Liberal studies',
          'Linguistics and applied linguistics', 'Linguistics and Applied Linguistics', 'Linguistics',
          'Materials science and engineering', 'Materials Science and Engineering', 'Mathematics Education',
          'Mechanical engineering', 'Mechanical Engineering', 'Microbiology', 'Molecular and cellular biology',
          'Molecular and Cellular Biology', 'Molecular biology', 'Music Education', 'Music', 'Natural Science',
          'Neurosciences', 'Nursing and healthcare innovation', 'Nursing and Healthcare Innovation', 'Nutrition',
          'Performance', 'Philosophy', 'Political science', 'Political Science', 'Public Administration and Policy',
          'Religious studies', 'Religious Studies', 'Rhetoric', 'Science and technology policy',
          'Science and Technology Policy', 'Social Justice and Human Rights', 'Social research', 'Social work',
          'Social Work', 'Spanish', 'Speech and hearing science', 'Speech and Hearing Science', 'Statistics',
          'Sustainability', 'Sustainable Engineering', 'Systems engineering', 'Systems Engineering', 'Theater',
          'Theatre', 'Transportation', 'Urban planning', 'Urban Planning']

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

prerecs = []
hdr = {'User-Agent' : 'Magic Browser'}
lp = pages
for page in range(pages):
    tocurl = 'https://keep.lib.asu.edu/collections/149053/search?search_api_fulltext=&sort_by=field_edtf_date_created_1&items_per_page=' + str(rpp) + '&f%5B0%5D=date_created_year%3A%28min%3A' + str(startyear) + '%2Cmax%3A' + str(stopyear) + '%29&f%5B1%5D=genre%3ADoctoral%20Dissertation&f%5B0%5D=date_created_year%3A%28min%3A' + str(startyear) + '%2Cmax%3A' + str(stopyear) + '%29&f%5B1%5D=genre%3ADoctoral%20Dissertation&page=' + str(page)
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    ejlmod3.printprogress('=', [[page+1, pages, lp], [tocurl]])
    for div in tocpage.find_all('div', attrs = {'class' : 'col-md-10'}):
        rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'supervisor' : [], 'note' : []}
        for h4 in div.find_all('h4'):
            for a in h4.find_all('a'):
                rec['link'] = 'https://repository.asu.edu' + a['href']
                rec['artlink'] = 'https://keep.lib.asu.edu' + a['href'] + '?_format=mods'
                if ejlmod3.checkinterestingDOI(rec['artlink']):
                    prerecs.append(rec)
    print('    %i' % (len(prerecs)))
    for a in tocpage.find_all('a', attrs = {'class' : 'page-link', 'title' : 'Go to last page'}):
        lp = int(re.sub('.*=', '', a['href']))
    time.sleep(10)

i = 0
recs = []
refield = re.compile('Field of study: ')
refield2 = re.compile('Doctoral Dissertation (.*) 20.*')
for rec in prerecs:
    keepit = True
    i += 1
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        time.sleep(5)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['artlink']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        except:
            print("no access to %s" % (rec['artlink']))
            continue
    #title
    for title in artpage.find_all('title'):
        rec['tit'] = title.text
    #abstract
    for abstract in artpage.find_all('abstract'):
        rec['abs'] = abstract.text
    #persons
    for name in artpage.find_all('name', attrs = {'type' : 'personal'}):
        for np in name.find_all('namepart'):
            for r in name.find_all('roleterm', attrs = {'type' : 'code'}):
                rt = r.text.strip()
                if rt == 'aut':
                    rec['autaff'] = [[ np.text, publisher ]]
                elif rt == 'ths':
                    rec['supervisor'].append([np.text])
    #language
    for language in artpage.find_all('languageterm', attrs = {'type' : 'code'}):
        rec['language'] = language.text
    #field
    for note in artpage.find_all('note'):
        field = False
        notet = note.text.strip()
        if refield.search(notet):
            field = refield.sub('', notet).strip()
        elif refield2.search(notet):
            field = refield2.sub(r'\1', notet).strip()
        if field:
            if field in boring:
                keepit = False
            elif field in ['Computer Science']:
                rec['fc'] = 'c'
            elif field in ['Astrophysics']:
                rec['fc'] = 'a'
            elif field in ['Mathematics', 'Applied Mathematics']:
                rec['fc'] = 'm'
            elif not field in ['Physics']:
                rec['note'].append(field)
    #keywords
    for subject in artpage.find_all('subject'):
        for topic in subject.find_all('topic'):
            rec['keyw'].append(topic.text)
    #date
    for date in artpage.find_all('datecreated'):
        rec['date'] = date.text
    #oa
    for ac in artpage.find_all('accesscondition'):
        act = ac.text
        if not act in ['In Copyright', 'All Rights Reserved']:
            rec['note'].append(act)
    #apges
    for extent in artpage.find_all('extent'):
        rec['pages'] = extent.text
    #handle/DOI
    for identifier in artpage.find_all('identifier', attrs = {'type' : 'hdl'}):
        rec['hdl'] = re.sub('.*handle.net\/', '', identifier.text)
    for identifier in artpage.find_all('identifier', attrs = {'type' : 'doi'}):
        rec['doi'] = re.sub('.*doi.org\/', '', identifier.text)
        del(rec['link'])
    #add to list
    if keepit:
        if skipalreadyharvested and 'doi' in rec and rec['doi'] in alreadyharvested:
            print('  %s already in backup' % (rec['doi']))
        elif skipalreadyharvested and 'hdl' in rec and rec['hdl'] in alreadyharvested:
            print('  %s already in backup' % (rec['hdl']))
        else:
            ejlmod3.printrecsummary(rec)
            recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['artlink'])
ejlmod3.writenewXML(recs, publisher, jnlfilename)
