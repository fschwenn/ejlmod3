# -*- coding: utf-8 -*-
#harvest theses from Houston U.
#FS: 2019-12-09
#FS: 2023-04-18
#FS: 2023-11-30

import sys
import os
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import undetected_chromedriver as uc


publisher = 'Houston U.'
jnlfilename = 'THESES-HOUSTON-%s' % (ejlmod3.stampoftoday())
rpp = 60
pages = 8
skipalreadyharvested = True

boring = ['Atmospheric Sciences', 'Biochemistry', 'Biology', 'Biomedical Engineering', 'Business Administration',
          'Cell and Molecular Biology', 'Chemical Engineering', 'Chemistry', 'Civil Engineering',
          'Counseling Psychology', 'Curriculum and Instruction', 'Environmental Engineering', 'Geophysics',
          'History', 'Hospitality Administration', 'Hospitality Management', 'Industrial Engineering',
          'Materials Engineering', 'Mechanical Engineering', 'Music', 'Petroleum Engineering', 'Pharmacology',
          'Physiological Optics and Vision Science', 'Professional Leadership, Education', 'School Psychology',
          'Social Work', 'Spanish', 'Special Populations', 'Developmental, Behavioral, and Cognitive Neuroscience',
          'Economics', 'Educational Psychology', 'Electrical Engineering', 'English', 'Geology',
          'Geosensing Systems Engineering', 'Higher Education Leadership and Policy', 'Kinesiology',
          'Pharmaceutic Health Outcomes &a; Policy', 'Pharmaceutics', 'Political Science', 'Psychology, Clinical',
          'Psychology, Industrial and Organizational', 'Psychology, Social', 'Psychology', 'Creative Writing',
          'Educational Psychology and Individual Differences', 'Higher Education Leadership and Policy Studies',
          'Hispanic Studies, Spanish']

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []



options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

baseurl = 'https://uh-ir.tdl.org'
driver.get(baseurl)
time.sleep(10)    


recs = []
for page in range(pages):
    tocurl = 'https://uh-ir.tdl.org/collections/dee50d8d-4ac5-4a91-a16a-62217c150a4d?cp.page=' + str(page+1) + '&cp.rpp=' + str(rpp)
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    try:
        driver.get(tocurl)
        time.sleep(5)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    except:
        time.sleep(60)
        driver.get(tocurl)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    
    for rec in ejlmod3.ngrx(tocpage, baseurl, ['dc.contributor.advisor', 'dc.creator', 'dc.creator.orcid',
                                               'dc.date.issued', 'dc.description.abstract', 'dc.identifier.uri',
                                               'dc.rights', 'dc.subject', 'dc.title', 'thesis.degree.discipline',
                                               'thesis.degree.name'], boring=boring, alreadyharvested=alreadyharvested):
        rec['autaff'][-1].append(publisher)
        ejlmod3.printrecsummary(rec)
        #print(rec['thesis.metadata.keys'])
        recs.append(rec)
    print('  %i records so far' % (len(recs)))
    time.sleep(20)
ejlmod3.writenewXML(recs, publisher, jnlfilename)
