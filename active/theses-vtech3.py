# -*- coding: utf-8 -*-
#harvest theses from Virginia Tech., Blacksburg
#FS: 2020-05-29
#FS: 2023-04-03

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import json

publisher = 'Virginia Tech., Blacksburg'
jnlfilename = 'THESES-VTECH-%s' % (ejlmod3.stampoftoday())
skipalreadyharvested = True

rpp = 50
pages = 6

boringdisciplines = ['Mechanical Engineering', 'Engineering Education', 'Biological Sciences',
                     'Civil Engineering', 'Electrical Engineering',
                     #'Computer Science and Applications',
                     'Engineering Mechanics', 'Plant Pathology, Physiology and Weed Science',
                     'Accounting and Information Systems', 'Aerospace Engineering',
                     'Agricultural and Extension Education', 'Animal and Poultry Sciences',
                     'Architecture and Design Research', 'Biomedical and Veterinary Sciences',
                     'Biomedical Engineering', 'Chemical Engineering', 'Chemistry',
                     #'Computer Engineering',
                     'Counselor Education', 'Crop and Soil Environmental Sciences',
                     'Curriculum and Instruction', 'Educational Leadership and Policy Studies',
                     'Educational Research and Evaluation', 'Environmental Design and Planning',
                     'Fisheries and Wildlife Science', 'Food Science and Technology',
                     'Human Development', 'Industrial and Systems Engineering',
                     'Materials Science and Engineering', 'Mining Engineering', 'Psychology',
                     'Public Administration/Public Affairs', 'Biochemistry',
                     'Social, Political, Ethical, and Cultural Thought',
                     'Biological Systems Engineering', 'Business, Finance',
                     'Economics, Agriculture and Life Sciences',
                     'Business, Executive Business Research',
                     'Genetics, Bioinformatics, and Computational Biology',
                     'Geosciences', 'Geospatial and Environmental Analysis',
                     'Horticulture', 'Human Nutrition, Foods, and Exercise',
                     'Leadership and Social Change', 'Nuclear Engineering',
                     'Planning, Governance, and Globalization', 'Rhetoric and Writing',
                     'Science and Technology Studies', 'Translational Biology, Medicine and Health',
                     'Agricultural, Leadership, and Community Education', 'Animal Sciences, Dairy',
                     'Business, Business Information Technology', 'Business, Management',
                     'Business, Marketing', 'Career and Technical Education',
                     'Economics, Science', 'Economics', 'Entomology', 'Forest Products',
                     'Forestry', 'Genetics, Bioinformatics and Computational Biology',
                     'Higher Education','Hospitality and Tourism Management',
                     'Macromolecular Science and Engineering',
                     'Plant Pathology, Physiology, and Weed Science',
                     'Public Administration and Public Affairs', 'Sociology']
boringdegrees = []
boringdisciplines += ['Aerospace+Engineering', 'Agricultural+and+Extension+Education',
                      'Animal+Sciences%2C+Dairy', 'Architecture+and+Design+Research',
                      'Biochemistry', 'Biological+Sciences', 'Biomedical+and+Veterinary+Sciences',
                      'Biomedical+Engineering', 'Business%2C+Business+Information+Technology',
                      'Business%2C+Executive+Business+Research', 'Chemical+Engineering', 'Chemistry',
                      'Civil+Engineering', 'Counselor+Education', 'Crop+and+Soil+Environmental+Sciences',
                      'Curriculum+and+Instruction', 'Educational+Leadership+and+Policy+Studies',
                      'Electrical+Engineering', 'Engineering+Education', 'Engineering+Mechanics',
                      'Entomology', 'Environmental+Design+and+Planning', 'Neurotrauma',
                      'Fisheries+and+Wildlife+Science', 'Food+Science+and+Technology', 'Forest+Products',
                      'Genetics%2C+Bioinformatics%2C+and+Computational+Biology', 'Geosciences',
                      'Geospatial+and+Environmental+Analysis', 'Higher+Education', 'Horticulture',
                      'Human+Nutrition%2C+Foods%2C+and+Exercise', 'Industrial+and+Systems+Engineering',
                      'Materials+Science+and+Engineering', 'Mechanical+Engineering',
                      'Planning%2C+Governance%2C+and+Globalization', 'Landscape+Architecture',
                      'Plant+Pathology%2C+Physiology+and+Weed+Science', 'Psychology',
                      'Public+Administration%2FPublic+Affairs', 'Sociology', 
                      'Social%2C+Political%2C+Ethical%2C+and+Cultural+Thought',
                      'Translational+Biology%2C+Medicine+and+Health']

hdr = {'User-Agent' : 'Magic Browser'}
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

prerecs = []
for page in range(pages):
    tocurl = 'https://vtechworks.lib.vt.edu/handle/10919/11041/discover?sort_by=dc.date.issued_dt&order=desc&filtertype=etdlevel&filter_relational_operator=equals&filter=doctoral&rpp=' + str(rpp) + '&page=' + str(page+1)
    ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features='lxml')
    for rec in ejlmod3.getdspacerecs(tocpage, 'https://vtechworks.lib.vt.edu', alreadyharvested=alreadyharvested):
        keepit = True
        if 'degrees' in rec:
            for degree in rec['degrees']:
                if degree in boringdisciplines:
                    keepit = False
                elif degree in ['Computer+Engineering', 'Computer+Science+%26+Applications']:
                    rec['fc'] = 'c'
                elif degree in ['Mathematics']:
                    rec['fc'] = 'm'
                elif degree in ['Statistics']:
                    rec['fc'] = 's'
        if keepit:
            prerecs.append(rec)
    print('  %4i records so far' % (len(prerecs)))
    time.sleep(3)

i = 0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link'] + '?show=full'), features='lxml')
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link'] + '?show=full'), features='lxml')
        except:
            print("no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['DC.title', 'DCTERMS.issued', 'DC.subject', 'DCTERMS.abstract', 'citation_pdf_url'])
    #author
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'DC.creator'}):
        if re.search('\d{4}\-\d{4}\-', meta['content']):
            rec['autaff'][-1].append('ORCID:' + meta['content'])
        else:
            author = re.sub(', \d+.*', '', meta['content'])
            rec['autaff'] = [[ author ]]
    rec['autaff'][-1].append(publisher)
    for tr in artpage.body.find_all('tr', attrs = {'class' : 'ds-table-row'}):
        for td in tr.find_all('td', attrs = {'class' : 'label-cell'}):
            label = td.text.strip()
        for td in tr.find_all('td', attrs = {'class' : 'word-break'}):
            word = td.text.strip()
        if label == 'dc.rights':
            rec['note'].append(word)
            rec['rights'] = word
        elif label == 'dc.description.degree':
            if word != 'Doctor of Philosophy':
                rec['note'].append(word)
                rec['degree'] = word
        elif label == 'thesis.degree.discipline':
            rec['note'].append(word)
            rec['discipline'] = word
    skipit = False
    if 'discipline' in list(rec.keys()) and rec['discipline'] in boringdisciplines:
        print('    skip', rec['discipline'])
        skipit = True
    if not skipit and 'degree' in list(rec.keys()) and rec['degree'] in boringdegrees:
        print('    skip', rec['degree'])
        skipit = True
    if skipit:
        ejlmod3.adduninterestingDOI(rec['hdl'])
    else:
        recs.append(rec)
        ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
