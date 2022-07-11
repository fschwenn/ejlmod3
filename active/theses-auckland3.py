# -*- coding: utf-8 -*-
#harvest theses from Auckland U.
#FS: 2022-03-07

import sys
import os
import urllib.request, urllib.error, urllib.parse
import urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

rpp = 50
pages = 8

publisher = 'Auckland U.'

jnlfilename = 'THESES-AUCKLAND-%s' % (ejlmod3.stampoftoday())
boring = ['Mechanical Engineering', 'Politics', 'Biology', 'Chemistry', 'Urban Planning',
          'Anthropology', 'Chemical Sciences', 'Civil Engineering', 'Engineering',
          'General Practice and Primary Health Care', 'Marine Science', 'Marketing',
          'Chemical and Materials Engineering', 'Civil and Environmental Engineering',
          'Computer Systems Engineering', 'Economics', 'Education', 'Health Sciences', 
          'Electrical, Computer and Software Engineering', 'Geology', 'Information Systems',
          'Management and International Business', 'Material Engineering', 'Film',
          'Media and Communication', 'Operations Research', 'Ophthalmology', 'Philosophy',
          'Politics and International Relations', 'Sociology', 'Statistics',
          'Accounting', 'Applied Language Studies and Linguistics', 'Asian Studies',
          'Biological Sciences', 'Biological Science', 'Biomedical Science',
          'Chemical and Material Engineering', 'Computer Science', 'Environmental Science',
          'Finance', 'Fine Arts', 'General Practice', 'History', 'Mathematics Education',
          'Medicine', 'Molecular Medicine and Pathology', 'Optometry and Vision Science',
          'Pharmaceutics', 'Pharmacy', 'Population Health', 'Psychiatry', 'Psychology',
          'Anaesthesiology', 'Anatomy and medical imaging', 'Anatomy', 'Ancient History',
          'Applied Linguistics', 'Architecture and Planning', 'Architecture', 'Art History',
          'Bioengineering', 'Biomedical Engineering', 'Cardio-renal Physiology',
          'Chemical Science', 'Chinese Linguistics', 'Clinical Psychology',
          'Community Health', 'Comparative Literature', 'ComputerScience', 
          'Critical Studies in Education', 'Dance Studies', 'Development Studies',
          'Discipline of Nutrition', 'Education and Social Work', 'Social Work', 
          'Education (Applied Linguistics and TESOL)', 'Electrical and Computer Engineering',
          'Electrical and Electronic Engineering', 'Electrical Engineering',
          'Engineering Science', 'English Literature', 'English', 'Exercise Sciences',
          'Food Science', 'Forensic Science', 'Geography', 'Geophysics', 'Gepphysics',
          'Health Psychology', 'International Business', 'Law', 'Linguistics', 'Management',
          'Marine Science/Computer Science', 'Mechatronics Engineering', 'Music', 
          'Media, Film and Television', 'Medical and Health Sciences', 'Molecular Medicine',
          'Nursing', 'Nutrition and Dietetics', 'Optometry', 'Perinatal Sciences',
          'Perinatal Science', 'Physiology', 'Planning', 'Public Health (Māori Health)',
          'Software Engineering', 'Speech Science', 'Surgery', 'Urban Design',
          'Audiology', 'Behavioural Science', 'Biochemistry', 'Biomedical Sciences',
          'Chemical & Materials Engineering', 'Commercial Law', 'Composition',
          'Computer Sciences', 'Dance Studies, Creative Arts & Industries', 'DMA',
          'Earth Science', 'Educational Technology', 'Education (Applied Linguistics & TESOL)',
          'Electrical and Electronics Engineering', 'EngineeringScience', 'English and Psychology',
          'Film, Media and Television', 'Italian', 'Marine Sciences', 'Media and Communications',
          'Medical Imaging', 'Medical Sciences', 'Microbiology', 'Music Education',
          'Obstetrics and Gynaecology', 'OperationsResearch', 'Pacific Studies', 'Paediatrics',
          'Paediatrics?', 'Pharmacology', 'Property', 'Theology', 'Anatomy and Radiology',
          'Art Histry', 'Biology and Environmental Science', 'Biology Sciences',
          'Business and Economics', 'Chemicals &amp; Materials Engineering', 'chemistry',
          'Commerce', 'Computer System Engineering', 'Criminology', 'Educational Psychology',
          'Education and English', 'Education (Applied Linguistics)', 'Electrical and Computer',
          'Electrical and Computing Engineering', 'English (Drama)', 'Environmental Engineering',
          'Environmental Management', 'Environmental Studies', 'Epidemiology',
          'Fine Arts and Dance Studies', 'French', 'German', 'Healthcare Quality',
          'Health Sciences and Medicine', 'Health Science', 'Māori and Pacific Health', 
          'Information Systems and Operations Management', 'Latin', 'Maori and Pacific Health',
          'Marine Biology', 'Mechatronics', 'Media, Film and Television Studies', 'Medical History',
          'Medical Science', 'Musical Arts', 'Nutrition', 'Oncology', 'Paediatric Endocrinology', 
          'Operations and Supply Chain Management', 'Operations Research,', 'Paediatric Medicine',
          'Pharmacology and Clinical Pharmacology', 'Political Studies', 'Psychological Medicine',
          'Public Health', 'Social work', 'Statistics and Marine Science', 'Translation Studies',
          'Accounting and Finance', 'Anatomy and Medical Imaging', 'Applied Chinese Linguistics',
          'Bioinformatics', 'Chemical Engineering', 'Education and Population Health',
          'Exercise Science', 'Film, Television and Media Studies', 'Film, Television and Media',
          'Information System and Operations Management', 'Language Teaching and Learning',
          'Medical and Health Science', 'Medical Education', 'Molecular Medicine Pathology',
          'Chemical and Mateirals Engineering', 'Musicology', 'PhD Education',
          'Obstetrics', 'Phamacy', 'Sport and Exercise Science', 'Translation and Interpretin',
          'Classics and Ancient History', 'Pharmaceutical Sciences', 'Spanish']

recs = []
prerecs = []
for page in range(pages):        
    tocurl = 'https://researchspace.auckland.ac.nz/handle/2292/2/discover?rpp=' + str(rpp) + '&page=' + str(page+1) + '&sort_by=dc.date.issued_dt&order=desc'
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    try:
        tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
        time.sleep(4)
    except:
        print("retry %s in 180 seconds" % (tocurl))
        time.sleep(180)
        tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
    prerecs += ejlmod3.getdspacerecs(tocpage, 'https://researchspace.auckland.ac.nz')

i = 0
for rec in prerecs:
    keepit = True
    i += 1
    ejlmod3.printprogress('-', [[i, len(prerecs)], [len(recs)], [rec['link']]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']+'?show=full'), features="lxml")
        time.sleep(4)
    except:
        print("retry %s in 180 seconds" % (rec['link']))
        time.sleep(180)
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']+'?show=full'), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'DCTERMS.issued', 'DCTERMS.abstract',
                                        'DC.subject', 'citation_pdf_url', 'DC.rights'])
    if not 'autaff' in rec or not rec['autaff']:
        for meta in artpage.head.find_all('meta', attrs = {'name' : 'DC.creator'}):
            rec['autaff'] = [[ meta['content'] ]]
    rec['autaff'][-1].append(publisher)

    for tr in artpage.body.find_all('tr', attrs = {'class' : 'ds-table-row'}):
        tdt = ''
        for td in tr.find_all('td'):
            if td.has_attr('class') and 'label-cell' in td['class']:
                tdt = td.text.strip()
            else:
                if tdt == 'dc.contributor.advisor':
                    sv = td.text.strip()
                    if sv != 'en':
                        rec['supervisor'].append([sv])
                elif tdt == 'thesis.degree.discipline':
                    disc = td.text.strip()
                    if disc in boring:
                        keepit = False
                    else:
                        rec['note'].append(disc)
    if keepit:
        print('  ', list(rec.keys()))
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['hdl'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
