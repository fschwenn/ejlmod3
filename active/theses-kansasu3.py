# -*- coding: utf-8 -*-
#harvest theses from Kansas U.
#FS: 2021-01-05
#FS: 2023-04-26

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Kansas U.'
jnlfilename = 'THESES-KANSAS_U-%s' % (ejlmod3.stampoftoday())

rpp = 50
pages = 2
skipalreadyharvested = True

boringdisciplines = ['Nursing', 'Bioengineering', 'Civil, Environmental & Architectural Engineering',
                     'Aerospace Engineering', 'Biostatistics',
                     #'Electrical Engineering & Computer Science',
                     'English', 'Mechanical Engineering', 'Molecular Biosciences', 'Music',
                     'Pharmaceutical Chemistry', 'Physical Therapy & Rehabilitation Sciences',
                     'Slavic Languages & Literatures', 'Anthropology', 'Chemical & Petroleum Engineering',
                     'Chemistry', 'Curriculum and Teaching', 'Dietetics & Nutrition', 'Geology',
                     'Psychology', 'Geography', 'Psychology & Research in Education',
                     'History of Art', 'Clinical Child Psychology', 'Counseling Psychology',
                     'Hearing and Speech', 'Applied Behavioral Science', 'American Studies',
                     'Public Administration', 'Anatomy & Cell Biology', 'Business', 'Cancer Biology',
                     'Health Policy & Management', 'History', 'Molecular & Integrative Physiology',
                     'Occupational Therapy Education', 'Pharmacology & Toxicology',
                     'Pharmacology, Toxicology & Therapeutics', 'Population Health', 'Special Education',
                     'Biochemistry & Molecular Biology', 'Biostatistics and Data Science', 
                     'Film & Media Studies', 'Communication Studies', 'Economics', 'Theatre',
                     'Ecology & Evolutionary Biology', 'Educational Leadership and Policy Studies',
                     'Health, Sport and Exercise Sciences', 'Medicinal Chemistry', 'Anthropology',
                     'Chemical & Petroleum Engineering', 'Chemistry', 'Curriculum and Teaching',
                     'Dietetics & Nutrition', 'Ecology & Evolutionary Biology', 'Geology', 'Social Welfare'
                     'Educational Leadership and Policy Studies', 'Health, Sport and Exercise Sciences',
                     'Medicinal Chemistry', 'Microbiology, Molecular Genetics & Immunology',
                     'Music Education & Music Therapy', 'Neurosciences', 'Pathology & Laboratory Medicine', 
                     'Microbiology, Molecular Genetics & Immunology', 'Music Education & Music Therapy',
                     'Neurosciences', 'Pathology & Laboratory Medicine', 'Social Welfare']
boringdegrees = []

if skipalreadyharvested:    
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
for page in range(pages):
    tocurl = 'https://kuscholarworks.ku.edu/handle/1808/1952/discover?sort_by=dc.date.issued_dt&order=desc&rpp=' + str(rpp) + '&page=' + str(page+1)
    tocurl = 'https://kuscholarworks.ku.edu/handle/1808/1952/discover?rpp=' + str(rpp) + '&etal=0&scope=&group_by=none&page=' + str(page+1) + '&sort_by=dc.date.accessioned_dt&order=desc&filtertype_0=dateIssued&filter_relational_operator_0=equals&filter_0=%5B2010+TO+2050%5D'
    ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    prerecs += ejlmod3.getdspacerecs(tocpage, 'https://kuscholarworks.ku.edu', alreadyharvested=alreadyharvested)
    time.sleep(3)

i = 0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link'] + '?show=full'), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link'] + '?show=full'), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['DC.title', 'DCTERMS.issued', 'DC.subject', 'DCTERMS.abstract',
                                        'citation_pdf_url', 'DCTERMS.extent'])
    #author
    for meta in artpage.head.find_all('meta', attrs = {'name' :  'DC.creator'}):
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
        #License
        if label == 'dc.rights':
            rec['note'].append(word)
            rec['rights'] = word
        #Degree
        elif label == 'dc.thesis.degreeLevel':
            if word != 'Doctor of Philosophy':
                rec['note'].append(word)
                rec['degree'] = word
        #Discipline
        elif label == 'dc.thesis.degreeDiscipline':
            rec['note'].append(word)
            rec['discipline'] = word
        #ORCID
        elif label == 'dc.identifier.orcid':
            rec['autaff'][-1].append(re.sub('.*\/', 'ORCID:', word))
        #supervisor
        elif label == 'dc.contributor.advisor':
            rec['supervisor'].append([word])
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
