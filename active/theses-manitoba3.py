# -*- coding: utf-8 -*-
#harvest theses from Manitoba U.
#FS: 2020-08-25
#FS: 2023-02-08

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

jnlfilename = 'THESES-MANITOBA-%s' % (ejlmod3.stampoftoday())

publisher = 'Manitoba U.'

hdr = {'User-Agent' : 'Magic Browser'}

rpp = 50
pages = 10
years = 2

boringdisciplines = ['Pharmacology and Therapeutics', 'Disability Studies', 'History',
                     'Educational Administration, Foundations and Psychology',
                     'Political Studies', 'Psychology', 'Religion', 'School of Art', 'Soil Science',
                     'Biomedical Engineering', 'Biosystems Engineering', 'Chemistry', 'Economics',
                     'English, Film, and Theatre', 'Food and Human Nutritional Sciences',
                     'Geological Sciences', 'Natural Resources Institute', 'Oral Biology',
                     'Peace and Conflict Studies', 'Preventive Dental Science', 'Sociology',
                     'Applied Health Sciences', 'Civil Engineering', 'Social Work', 'Animal Science',
                     'Anthropology', 'Biological Sciences', 'City Planning',
                     'Community Health Sciences', 'Education', 'Electrical and Computer Engineering',
                     'Entomology', 'Environment and Geography', 'Human Anatomy and Cell Science',
                     'Human Nutritional Sciences', 'Law', 'Management', 'Mechanical Engineering',
                     'Medical Microbiology and Infectious Diseases', 'Microbiology',
                     'Native Studies', 'Nursing', 'Pharmacy', 'Physiology and Pathophysiology',
                     'Plant Science', 'Biochemistry and Medical Genetics', 'Business Administration',
                     'Cancer Control', 'Curriculum, Teaching and Learning', 'English, Theatre, Film and Media'
                     'Agribusiness and Agricultural Economics', 'Food Science',
                     'Medical Microbiology', 'Accounting and Finance', 'Architecture',
                     'English', 'Family Social Sciences', 'History (Archival Studies)',
                     'Interior Design', 'Kinesiology and Recreation Management',
                     'Landscape Architecture', 'Management/Business Administration',
                     'Mechanical and Manufacturing Engineering', 'Pathology', 'Physiology',
                     'Food and Nutritional Sciences', 'French, Spanish and Italian', 'Immunology',
                     'Interdisciplinary Program', 'Linguistics', 'Natural Resources Management',
                     'Études canadiennes', 'Indigenous Studies', 'Sociology and Criminology', 
                     'Preventive Dental Science (Pediatric Dentistry)']

boringdegrees = ['Master of Science (M.Sc.)', 'Master of Arts (M.A.)',  'Master of Education (M.Ed.)',
                 'Master of Fine Art (M.F.A.)',  'Master of Interior Design (M.I.D.)',
                 'Master of Landscape Architecture (M.Land.Arch.)',  'Master of Dentistry (M. Dent.)',
                 'Master of Natural Resources Management (M.N.R.M.)', 'Master of Nursing (M.N.)',
                 'Master of Social Work (M.S.W.)', 'Master of City Planning (M.C.P.)',
                 'Master of Mathematical, Computational and Statistical Sciences (M.M.C.S.S.)',
                 'Master of Laws (LL.M.)', 'Bachelor of Science (B.Sc.)',
                 'Maîtrise ès arts (Université de Saint-Boniface)', 'Master of Dentistry (M.Dent.)']

prerecs = []
for page in range(pages):
    tocurl = 'https://mspace.lib.umanitoba.ca/xmlui/handle/1993/6/discover?rpp='+str(rpp)+'&etal=0&group_by=none&page=' + str(page+1) + '&sort_by=dc.date.issued_dt&order=desc'
    ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    for rec in ejlmod3.getdspacerecs(tocpage, 'https://mspace.lib.umanitoba.ca'):
        new = True
        if 'year' in rec and int(rec['year']) <= ejlmod3.year(backwards=years):
            print('  skip',  rec['year'])
        else:
            prerecs.append(rec)
    print('  %4i records so far' % (len(prerecs)))
    time.sleep(2)

i = 0
recs = []
for rec in prerecs:
    keepit = True
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link'] + '?show=full'], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link'] + '?show=full'), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link'] + '?show=full'))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link'] + '?show=full'), features="lxml")
        except:
            print("no access to %s" % (rec['link'] + '?show=full'))
            continue    
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'citation_title', 'DCTERMS.issued', 'DCTERMS.abstract',
                                        'citation_pdf_url'])
    rec['autaff'][-1].append(publisher)
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'citation_keywords'}):
        for keyw in re.split('[,;] ', meta['content']):
            if not re.search('^info.eu.repo', keyw):
                rec['keyw'].append(keyw)
    for tr in artpage.body.find_all('tr'):
        for td in tr.find_all('td', attrs = {'class' : 'label-cell'}):
            tdt = td.text.strip()
            td.decompose()
        for td in tr.find_all('td'):
            if td.text.strip() == 'en_US':
                continue
            #supervisor
            if tdt == 'dc.contributor.supervisor':
                rec['supervisor'] = [[ re.sub(' \(.*', '', td.text.strip()) ]]
            #discipline
            elif tdt == 'dc.degree.discipline':
                discipline = td.text.strip()
                if discipline in boringdisciplines:
                    print('  skip "%s"' % (discipline))
                    keepit = False
                elif discipline == 'Computer Science':
                    rec['fc'] = 'c'
                elif discipline == 'Mathematics':
                    rec['fc'] = 'm'
                elif discipline == 'Statistics':
                    rec['fc'] = 's'
                elif discipline != 'Physics and Astronomy':
                    rec['note'].append(discipline)
            #degree
            elif tdt == 'dc.degree.level':
                degree = td.text.strip()
                if degree in boringdegrees:
                    print('  skip "%s"' % (degree))
                    keepit = False
                else:
                    rec['note'].append(degree)
    if keepit:
        recs.append(rec)
        ejlmod3.printrecsummary(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['hdl'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
