# -*- coding: utf-8 -*-
#harvest theses from Saskatchewan U.
#FS: 2020-09-25
#FS: 2023-04-17
#FS: 2024-01-17

import getopt
import sys
import os
#import urllib.request, urllib.error, urllib.parse
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import re
import ejlmod3
import time


publisher = 'Saskatchewan U.'
jnlfilename = 'THESES-SASKATCHEWAN-%s' % (ejlmod3.stampoftoday())

rpp = 50
pages = 10
skipalreadyharvested = False
boring = ['Chemistry', 'Veterinary Biomedical Sciences', 'English', 'Educational Foundations',
          'History', 'School of Environment and Sustainability', 'Soil Science',
          'Agricultural and Resource Economics', 'Archaeology and Anthropology',
          'Biomedical Engineering', 'Chemical and Biological Engineering',
          'Educational Administration', 'Electrical and Computer Engineering',
          'Interdisciplinary Centre for Culture and Creativity', 'Interdisciplinary Studies',
          'Johnson-Shoyama Graduate School of Public Policy', 'Nursing', 'Pharmacology',
          'School of Public Health', 'Veterinary Pathology', 'Toxicology Centre',
          'Animal and Poultry Science', 'Biology', 'Civil and Geological Engineering',
          'Community Health and Epidemiology', 'Geography and Planning', 'Geography',
          'Large Animal Clinical Sciences', 'Law', 'Mechanical Engineering', 'Medicine',
          'Microbiology and Immunology', 'Psychology', 'Sociology', 'Veterinary Microbiology',
          'Anatomy and Cell Biology', 'Art and Art History', 'Biochemistry', 'Curriculum Studies',
          'Food and Bioproduct Sciences', 'Geological Sciences', 'Kinesiology',
          'Bioresource Policy, Business and Economics', 'Environmental Engineering',
          'Nutrition', 'Pathology and Laboratory Medicine', 'Western College of Veterinary Medicine',
          'Pharmacy and Nutrition', 'Physiology', 'Plant Sciences', 'School of Physical Therapy',
          'Anatomy, Physiology, and Pharmacology', 'Interdisciplinary Food Science Program',
          'Agricultural and Bioresource Engineering', 'Agricultural Economics',
          'Agricultural Engineering', 'Agriculture and Bioresource Engineering', 'Animal Husbandry',
          'Animal Science', 'Applied Microbiology and Food Science', 'Cancer Research',
          'Chemical Engineering', 'Chemistry and Chemical Engineering', 'Civil Engineering',
          'College of Agriculture', 'College of Arts and Science', 'College of Education',
          'College of Graduate Studies', 'College of Kinesiology', 'College of Pharmacy and Nutrition',
          'Crop Science and Plant Ecology', 'Crop Science', 'Dairy Science', 'Economics',
          'Educational Psychology and Special Education', 'Field Husbandry', 'Finance', 'Food Science',
          'Horticulture', 'Linguistics', 'Native Studies', 'Pharmacy', 'Physiology and Pharmacology',
          'Plant Ecology', 'Plant Science', 'Political Science', 'Political Studies',
          'Poultry Science', 'Psychiatry', 'Toxicology']
boring += ['Master of Science (M.Sc.)', 'Master of Education (M.Ed.)', 'Master of Arts (M.A.)',
           'Master of Nursing (M.N.)', 'Master of Public Policy (M.P.P.)',
           'Master of Laws (LL.M.)', 'Master of Fine Arts (M.F.A.)']

options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

hdr = {'User-Agent' : 'Magic Browser'}


recs = []
allhdls = []
baseurl = 'https://harvest.usask.ca'

recs = []
for page in range(pages):
    tocurl = baseurl + '/collections/c58530ca-7de1-416a-81bc-4b715d1ddf2e?cp.page=' + str(page+1) + '&cp.rpp=' + str(rpp)
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
                                               'dc.date.issued', 'thesis.degree.department',
                                               'dc.degree.discipline', 'dc.language.iso', 
                                               'dc.rights', 'thesis.degree.level', 'thesis.degree.name', 
                                               'dc.description.abstract', 'dc.identifier.uri',
                                               'dc.subject', 'dc.title'],
                            boring=boring, alreadyharvested=alreadyharvested):
        rec['autaff'][-1].append(publisher)
        ejlmod3.printrecsummary(rec)
        #print(rec['thesis.metadata.keys'])
        recs.append(rec)
    print('  %i records so far' % (len(recs)))
    time.sleep(20)
ejlmod3.writenewXML(recs, publisher, jnlfilename)


