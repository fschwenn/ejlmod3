# -*- coding: utf-8 -*-
#harvest theses from Georgia Tech
#FS: 2022-04-18
#FS: 2023-03-27
#FS: 2023-11-30

import sys
import os
from bs4 import BeautifulSoup
import re
import ejlmod3
import undetected_chromedriver as uc
import time

publisher = 'Georgia Tech'
jnlfilename = 'THESES-GEORGIATECH-%s' % (ejlmod3.stampoftoday())

rpp = 40
pages = 5
skipalreadyharvested = True

boring = ['Electrical and Computer Engineering', 'Civil and Environmental Engineering',
          'Aerospace Engineering', 'Biology', 'Chemical and Biomolecular Engineering',
          'City and Regional Planning', 'Computational Science and Engineering',
          'Industrial and Systems Engineering', 'Interactive Computing', 'Music',
          'Mechanical Engineering', 'Psychology', 'Public Policy', 'Architecture',
          'Biomedical Engineering (Joint GT/Emory Department)', 'Chemistry and Biochemistry',
          'Economics', 'History, Technology and Society', 'International Affairs',
          'Building Construction', 'Business', 'Earth and Atmospheric Sciences',
          'Literature, Media, and Communication', 'Materials Science and Engineering',
          'Applied Physiology', 'Industrial Design', 'Biomedical Engineering',
          'Polymer, Textile and Fiber Engineering', 'Bioengineering',
          'Center for Music Technology', 'Chemical Engineering', 'City Planning',
          'Digital Media', 'Literature, Communication, and Culture', 'Management',
          'Materials Science & Engineering', 'Medical Physics', 'Robotics',
          'Strategic Management', 'Aerospace Engineering', 'Applied Physiology',
          'Architecture', 'Biology', 'Biomedical Engineering (Joint GT/Emory Department)',
          'Building Construction', 'Business', 'Chemical and Biomolecular Engineering',
          'Chemistry and Biochemistry', 'City and Regional Planning',
          'Civil and Environmental Engineering', 'Earth and Atmospheric Sciences',
          'Economics', 'History, Technology and Society',
          'Industrial and Systems Engineering', 'Industrial Design',
          'Literature, Media, and Communication', 'Materials Science and Engineering',
          'Mechanical Engineering', 'Psychology', 'Public Policy']


if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

baseurl = 'https://repository.gatech.edu'
driver.get(baseurl)
time.sleep(10)    

recs = []
for page in range(pages):
    tocurl = 'https://repository.gatech.edu/collections/3b203ae7-3ac9-4107-aae7-d4320ca8e1e0?cp.page=' + str(page+1) + '&cp.rpp=' + str(rpp)
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    try:
        driver.get(tocurl)
        time.sleep(5)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    except:
        time.sleep(60)
        driver.get(tocurl)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    
    for rec in ejlmod3.ngrx(tocpage, baseurl, ['dc.contributor.advisor', 'dc.contributor.author',
                                               'dc.contributor.department', 'dc.date.issued',
                                               'dc.description.abstract', 'dc.identifier.uri',
                                               'dc.subject', 'dc.title', 'dc.type.genre',
                                               'local.contributor.advisor',
                                               'thesis.degree.level'], boring=boring, alreadyharvested=alreadyharvested):
        rec['autaff'][-1].append(publisher)
        ejlmod3.printrecsummary(rec)
        #print(rec['thesis.metadata.keys'])
        recs.append(rec)
    print('  %i records so far' % (len(recs)))
    time.sleep(20)
ejlmod3.writenewXML(recs, publisher, jnlfilename)
