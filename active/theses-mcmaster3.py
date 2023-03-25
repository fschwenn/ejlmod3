# -*- coding: utf-8 -*-
#harvest theses McMaster U.
#FS: 2021-01-08
#FS: 2023-03-25

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import json
import ssl

publisher = 'McMaster U.'
jnlfilename = 'THESES-MCMASTER-%s' % (ejlmod3.stampoftoday())

rpp = 100
pages = 2
skipalreadyharvested = True

boringdeps = ['Global Health', 'Religion', 'Biology', 'Electrical and Computer Engineering', 'Medical Sciences',
              'Biomedical Engineering', 'Chemical Engineering', 'Chemistry and Chemical Biology', 'Chemistry',
              'Classics', 'Earth and Environmental Sciences', 'Geography', 'Health Research Methodology',
              'Christian Studies', 'Christian Theology', 'Education', 'Geochemistry', 'Geography and Geology',
              'Geology', 'Health Care Research Methods',
              'Health Sciences', 'Kinesiology', 'Labour Studies', 'Mechanical Engineering', 'Religious Studies',
              'Anthropology', 'Biochemistry and Biomedical Sciences', 'Biochemistry', 'Civil Engineering',
              'Clinical Epidemiology/Clinical Epidemiology & Biostatistics', 'eHealth', 'Health Policy',
              'Cognitive Science of Language', 'Statistics',
              #'Computational Engineering and Science', 'Computing and Software',
              'Engineering Physics', 'French', 'Geography and Earth Sciences', 'Health and Aging',
              'Materials Science and Engineering', 'Materials Science', 'Neuroscience', 'Philosophy',
              'Biomechanics', 'Classical Studies', 'Communications Management', 'Environmental Science',
              'Political Science - International Relations', 'Political Science', 'Social Work', 'Sociology',
              'Medical Sciences (Blood and Cardiovascular)', 'Medical Sciences (Cell Biology and Metabolism)',
              'Medical Sciences (Division of Physiology/Pharmacology)', 'Rehabilitation Science',
              'Medical Sciences (Molecular Virology and Immunology Program)', 'Nursing', 'Psychology',
              'Business', 'Chemical Biology', 'Clinical Epidemiology/Clinical Epidemiology & Biostatistics',
              'Clinical Health Sciences (Health Research Methodology)',
              #'Computer Science',
              'Electrical Engineering', 'English and Cultural Studies', 'Health Science Education', 'History',
              'Radiation Sciences (Medical Physics/Radiation Biology)', 'Software Engineering',
              'Adapted Human Biodynamics', 'Astrophysics', 'Behavioural Endocrinology',
              'Biblical Studies, Religion', 'Church History/Christian Interpretation', 'Church History',
              'Clinical Health Sciences (Nursing)', 'Divinity College', 'Health Geography', 'Health',
              'Literature', 'Management Science/Information Systems', 'Management Science/Systems',
              'Medical Sciences, Division of Physiology/Pharmacology', 'Physiology and Pharmacology',
              'Medical Sciences (Neuroscience and Behavioral Science)', 'Political Economy',
              'Romance Languages', 'Roman Studies', 'School of the Arts',
              'Molecular Immunology, Virology and Inflammation', 'Music Criticism', 'Music', 'Neurosciences',
              'Business Administration', 'Earth Sciences', 'Economics', 'Engineering', 'English',
              'Health and Radiation Physics', 'Materials Engineering', 'Medical Physics', 'Religious Sciences',
              'Medical Sciences (Growth and Development)', 'Medical Sciences (Neurosciences)', 'Medicine',
              'Engineering Physics and Nuclear Engineering', 'Finance', 'Metallurgy and Materials Science',
              'Mechanical and Manufacturing Engineering', 'School of Geography and Geology', 'Work and Society',
              'Medical Sciences (Clinical Epidemiology and Health Care Research)',
              'Medical Sciences (Thrombosis & Haemostasis & Atherosclerosis)', 'Humanities']

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

#bad certificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
hdr = {'User-Agent' : 'Magic Browser'}

prerecs = []
for page in range(pages):
    tocurl = 'https://macsphere.mcmaster.ca/handle/11375/272/browse?rpp=' + str(rpp) + '&sort_by=2&type=dateissued&offset=' + str(page*rpp) + '&etal=-1&order=DESC'
    ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
    try:
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
    except:
        print(' try again in 20s...')
        time.sleep(20)
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
    divs = tocpage.body.find_all('td', attrs = {'headers' : 't2'})
    for div in divs:
        rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'note' : [], 'supervisor' : []}
        for a in div.find_all('a'):
            rec['artlink'] = 'https://macsphere.mcmaster.ca' + a['href']
            rec['hdl'] = re.sub('.*handle\/', '', a['href'])
            if ejlmod3.checkinterestingDOI(rec['hdl']):
                if not skipalreadyharvested or not rec['hdl'] in alreadyharvested:
                    prerecs.append(rec)
    time.sleep(5)

i = 0
recs = []
for rec in prerecs:
    keepit = True
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        req = urllib.request.Request(rec['artlink'], headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        time.sleep(2)
    except:
        try:
            print("   retry %s in 15 seconds" % (rec['artlink']))
            time.sleep(15)
            req = urllib.request.Request(rec['artlink'], headers=hdr)
            artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        except:
            print("   no access to %s" % (rec['artlink']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'DC.title', 'citation_date',
                                        'DC.subject', 'citation_pdf_url'])
    if not 'date' in list(rec.keys()):
        for meta in artpage.head.find_all('meta', attrs = {'name' : 'DCTERMS.dateAccepted'}):
            rec['date'] = meta['content']
            rec['note'].append('date from DCTERMS.dateAccepted')
    if not 'autaff' in rec:
        rec['autaff'] = [[ 'Doe, John' ]]
    rec['autaff'][-1].append(publisher)
    for tr in artpage.find_all('tr'):
        for td in tr.find_all('td', attrs = {'class' : 'metadataFieldLabel'}):
            tdfl = td.text.strip()
        for td in tr.find_all('td', attrs = {'class' : 'metadataFieldValue'}):
            #supervisor
            if re.search('Advisor', tdfl):
                for a in td.find_all('a'):
                    rec['supervisor'].append([a.text.strip()])
            elif re.search('Department', tdfl):
                dep = td.text.strip()
                if dep in boringdeps:
                    keepit = False
                else:
                    rec['note'].append(dep)
    #license
    ejlmod3.globallicensesearch(rec, artpage)
    if keepit:
        recs.append(rec)
        ejlmod3.printrecsummary(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['hdl'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
