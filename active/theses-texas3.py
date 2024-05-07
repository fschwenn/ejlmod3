# -*- coding: utf-8 -*-
#harvest theses from Texas U.
#FS: 2019-12-09
#FS: 2022-09-10
#FS: 2023-11-28

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import codecs
import datetime
import time
import json
import undetected_chromedriver as uc

publisher = 'Texas U.'
jnlfilename = 'THESES-TEXAS_U-%s' % (ejlmod3.stampoftoday())

rpp = 100
pages = 10
skipalreadyharvested = True

boring = ['Cello performance', 'Chemistry', 'Civil Engineering', 'Clarinet performance',
          'Collaborative piano', 'Composition', 'Mechanical Engineering', 'Percussion performance',
          'Petroleum Engineering', 'Physics', 'Piano perfomance', 'Piano performance',
          'Psychology - Clinical Psychology', 'Psychology', 'Social work', 'Sociology',
          'Trombone performance', 'Trumpet performance', 'Vocal performance', 'Public Affairs',
          'Music', 'Economics', 'Advertising', 'Architecture', 'Biomedical Engineering',
          'Cell and Molecular Biology', 'Chemical Engineering', 'Communication Studies',
          'Educational Leadership and Policy', 'Geological Sciences', 'Government', 'History',
          'Linguistics', 'Public Policy (PhD)', 'Special Education', 'Music and Human Learning',
          'Speech, Language, and Hearing Sciences', 'Accounting', 'Aerospace Engineering',
          'Anthropology', 'Bassoon performance', 'Community and Regional Planning',
          'Comparative literature', 'Curriculum and Instruction', 'Ecology, Evolution, and Behavior',
          'Educational leadership and policy', 'Educational Psychology - School', 'Plant Biology', 
          'Educational Psychology', 'Engineering Mechanics', 'Microbiology', 'Philosophy',
          'Environmental and Water Resources Engineering', 'Finance', 'French', 'Germanic Studies',
          'Kinesiology', 'Management', 'Marketing', 'Materials Science and Engineering',
          'Nursing', 'Operations Research and Industrial Engineering', 'Pharmaceutical Sciences',
          'Radio-Television-Film',  'Social Work', 'Speech Language Pathology', 'Violin performance',
          'Science, Technology, Engineering, and Mathematics (STEM) Education', 'American Studies',
          'Biochemistry', 'Educational Psychology - Counseling', 'English', 'Geography',
          'Health Behavior and Health Education', 'Human Development and Family Sciences',
          'Latin American Studies', 'Marine science', 'Neuroscience', 'Nutritional Sciences',
          'Spanish', 'African and African Diaspora Studies', 'Architectural Engineering',
          'Information, Risk, and Operations Management', 'Information Studies']
boring += ['Doctor of Education', 'Doctor of Musical Arts', 'Artist diploma', 'Master of Music',
           'Master of Arts']


if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []
    
hdr = {'User-Agent' : 'Magic Browser'}
options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)
driver.get('https://utexas.edu')
time.sleep(10)
driver.get('https://repositories.lib.utexas.edu')
time.sleep(10)
recs = []
for page in range(pages):
    tocurl = 'https://repositories.lib.utexas.edu/browse/dateissued?scope=4d334651-b63a-4e48-851c-938cbe4833ba&bbm.page=' + str(page+1) + '&bbm.sd=DESC&bbm.rpp=' + str(rpp)
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    #req = urllib.request.Request(tocurl, headers=hdr)
    #tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    try:
        driver.get(tocurl)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    except:
        time.sleep(60)
        driver.get(tocurl)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    baseurl = 'https://repositories.lib.utexas.edu/'
    for rec in ejlmod3.ngrx(tocpage, baseurl, ['dc.contributor.advisor', 'dc.creator', 'dc.creator.orcid',
                                               'dc.date.issued', 'dc.description.abstract',
                                               'dc.identifier', 'dc.language.iso',
                                               'dc.rights', 'dc.title', 'dc.identifier.uri',
                                               'thesis.degree.discipline',
                                               'thesis.degree.level', 'thesis.degree.name'], boring=boring, alreadyharvested=alreadyharvested):
        rec['autaff'][-1].append(publisher)
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
        
    time.sleep(20)


ejlmod3.writenewXML(recs, publisher, jnlfilename)
