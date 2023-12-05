# -*- coding: utf-8 -*-
#harvest theses from Manitoba U.
#FS: 2020-08-25
#FS: 2023-02-08
#FS: 2023-12-02

import sys
import os
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import undetected_chromedriver as uc

jnlfilename = 'THESES-MANITOBA-%s' % (ejlmod3.stampoftoday())

publisher = 'Manitoba U.'

rpp = 40
pages = 2
skipalreadyharvested = True

boring = ['Pharmacology and Therapeutics', 'Disability Studies', 'History',
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

boring += ['Master of Science (M.Sc.)', 'Master of Arts (M.A.)',  'Master of Education (M.Ed.)',
           'Master of Fine Art (M.F.A.)',  'Master of Interior Design (M.I.D.)',
           'Master of Landscape Architecture (M.Land.Arch.)',  'Master of Dentistry (M. Dent.)',
           'Master of Natural Resources Management (M.N.R.M.)', 'Master of Nursing (M.N.)',
           'Master of Social Work (M.S.W.)', 'Master of City Planning (M.C.P.)',
           'Master of Mathematical, Computational and Statistical Sciences (M.M.C.S.S.)',
           'Master of Laws (LL.M.)', 'Bachelor of Science (B.Sc.)',
           'Maîtrise ès arts (Université de Saint-Boniface)', 'Master of Dentistry (M.Dent.)']


boring = []

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)


recs = []
for page in range(pages):
    tocurl = 'https://mspace.lib.umanitoba.ca/collections/b982474b-e27f-4861-af0d-2a6e75aa57bc?cp.page=' + str(page+1) + '&cp.rpp=' + str(rpp)
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    try:
        driver.get(tocurl)
        time.sleep(5)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    except:
        time.sleep(60)
        driver.get(tocurl)
        time.sleep(5)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    baseurl = 'https://mspace.lib.umanitoba.ca'
    
    for rec in ejlmod3.ngrx(tocpage, baseurl, [], boring=boring, alreadyharvested=alreadyharvested):
        rec['autaff'] = [[ rec['autaff'][0][0], publisher ]]
        ejlmod3.printrecsummary(rec)
        print(rec['thesis.metadata.keys'])
        recs.append(rec)
    print('  %i records so far' % (len(recs)))
    time.sleep(20)
ejlmod3.writenewXML(recs, publisher, jnlfilename)
