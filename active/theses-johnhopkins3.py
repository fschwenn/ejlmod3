# -*- coding: utf-8 -*-
#harvest theses from Johns Hopkins U. (main) 
#FS: 2019-12-11
#FS: 2023-01-20
#FS: 2023-11-30

import sys
import os
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import undetected_chromedriver as uc

publisher = 'Johns Hopkins U. (main)'
jnlfilename = 'THESES-JOHN_HOPKINS-%s' % (ejlmod3.stampoftoday())


rpp = 100
pages = 5
skipalreadyharvested = True

boring = ['School of Medicine', 'Neuroscience', 'Biomedical Engineering', 'Mechanical Engineering', 'Biology',
          'Chemistry', 'Anthropology', 'Clinical Investigation', 'Environmental Health &a; Engineering',
          'Materials Science &a; Engineering', 'Materials Science and Engineering', 'Mental Health',
          'Physiology', 'Population%2C Family and Reproductive Health', 'Pharmacology and Molecular Sciences',
          'Electrical Engineering', 'Graduate Training Program in Clinical Investigation',
          'Molecular Microbiology and Immunology', 'Sociology', 'Biochemistry', 'Civil Engineering', 'Economics',
          'Entrepreneurial Leadership in Education', 'History', 'Human Genetics and Molecular Biology', 'Nursing',
          'Public Health Studies', 'Biostatistics', 'Cellular and Molecular Medicine', 'Environmental Health and Engineering',
          'Chemical &a; Biomolecular Engineering', 'Chemical and Biomolecular Engineering',
          'Electrical and Computer Engineering', 'Biochemistry%2C Cellular and Molecular Biology',
          'Cell Biology', 'Cellular &a; Molecular Medicine', 'Health Policy and Management', 'Immunology',
          'Biophysics', 'Education', 'Epidemiology', 'International Health', 'Chemistry', 'Robotics',
          'School of Medicine', 'Bloomberg School of Public Health', 'English', 'Anatomy',
          'School of Advanced International Studies', 'China Studies', 'History of Medicine',
          'Comparative Literature', 'East Asian Studies', 'Egyptian Art and Archaeology',
          'German', 'Global Security Studies', 'History of Science &a; Technology',
          'History of Science and Technology', 'Italian',  'Spanish', 
          'Psychological and Brain Sciences', 'Psychology', 'School of Education',
          'Cognitive Science', 'History of Art', 'Humanities', 'Near Eastern Studies',
          'Philosophy', 'Political Science', 'International Affairs',
          'German and Romance Languages and Literatures', 'School of Nursing',
          'Biochemistry, Cellular and Molecular Biology', 'Classics', 'Earth and Planetary Sciences',
          'Health, Behavior and Society', 'McKusick-Nathans Institute of Genetic Medicine',
          'Molecular Biology and Genetics', 'Pathobiology', 'Population, Family and Reproductive Health',
          'WH/Latin American Studies', 'Classics', 'Earth &a; Planetary Sciences',
          'Energy Policy &a; Climate', 'Health Equity and Social Justice', 'International Studies',
          'Latin American Studies', 'Microbiology', 'Social &a; Behavioral Sciences']

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []


options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

baseurl = 'https://jscholarship.library.jhu.edu'
driver.get(baseurl)
time.sleep(10)    


recs = []
for page in range(pages):
    tocurl = 'https://jscholarship.library.jhu.edu/collections/9d8f870e-647d-4e06-a870-8977f530a24c?cp.page=' + str(page+1) + '&cp.rpp=' + str(rpp)
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    try:
        driver.get(tocurl)
        time.sleep(5)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    except:
        time.sleep(60)
        driver.get(tocurl)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    
    for rec in ejlmod3.ngrx(tocpage, baseurl, ['dc.contributor.advisor', 'dc.creator',
                                               'dc.creator.orcid', 'dc.date.issued',
                                               'dc.description.abstract', 'dc.identifier.uri',
                                               'dc.subject', 'dc.title',  'thesis.degree.discipline',
                                               'thesis.degree.name'], fakehdl=True, boring=boring, alreadyharvested=alreadyharvested):
        rec['autaff'][-1].append(publisher)
        ejlmod3.printrecsummary(rec)
        #print(rec['thesis.metadata.keys'])
        recs.append(rec)
    print('  %i records so far' % (len(recs)))
    time.sleep(20)
ejlmod3.writenewXML(recs, publisher, jnlfilename)
