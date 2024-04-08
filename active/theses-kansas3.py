# -*- coding: utf-8 -*-
#harvest theses from Kansas State U.
#FS: 2020-02-10
#FS: 2023-02-20
#FS: 2024-04-08

import getopt
import sys
import os
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Kansas State U.'
pages = 5
rpp = 100 
skipalreadyharvested = True
boring = ['Biochemistry and Molecular Biophysics Interdepartmental Program', 'Curriculum and Instruction Programs',
          'Department of Agricultural Economics', 'Department of Agronomy',
          'Department of Animal Sciences and Industry', 'Department of Architectural Engineering and Construction Science',
          'Department of Architectural Engineering', 'Department of Architecture',
          'Department of Biological &a; Agricultural Engineering', 'Department of Biology', 'Department of Chemical Engineering',
          'Department of Chemistry', 'Department of Clinical Sciences', 'Department of Diagnostic Medicine/Pathobiology',
          'Department of Economics', 'Department of Educational Leadership', 'Department of Electrical and Computer Engineering',
          'Department of Entomology', 'Department of Food, Nutrition, Dietetics and Health', 'Department of Geography',
          'Department of Geology', 'Department of Grain Science and Industry', 'Department of History',
          'Department of Horticulture and Natural Resources', 'Department of Human Ecology-Personal Financial Planning',
          'Department of Journalism and Mass Communications', 'Department of Kinesiology',
          'Department of Landscape Architecture/Regional and Community Planning',
          'Department of Mechanical and Nuclear Engineering', 'Department of Psychological Sciences',
          'Department of Sociology, Anthropology, and Social Work', 'Food Science Institute',
          'Genetics Interdepartmental Program',
          'Public Health Interdepartmental Program', 'Department of Anatomy and Physiology',
          'Department of Civil Engineering', 'Division of Biology']

jnlfilename = 'THESES-KANSASSTATE-%s' % (ejlmod3.stampoftoday())

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)


baseurl = 'https://krex.k-state.edu'
collection = '6d684812-6d29-4564-8b51-f5670957936b'

recs = []
for page in range(pages):
    tocurl = baseurl + '/collections/' + collection + '?cp.page=' + str(page+1) + '&cp.rpp=' + str(rpp)
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    try:
        driver.get(tocurl)
        time.sleep(10)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    except:
        time.sleep(60)
        driver.get(tocurl)
        time.sleep(10)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    for rec in ejlmod3.ngrx(tocpage, baseurl, ['dc.contributor.author',  'dc.date.published',
                                               'dc.description.abstract', 'dc.description.advisor',
                                               'dc.description.level',  'dc.identifier.uri',
                                               'dc.description.department', 'dc.subject', 'dc.title'],
                            boring=boring, alreadyharvested=alreadyharvested):        
        rec['autaff'][-1].append(publisher)
        #print(rec['thesis.metadata.keys'])
        recs.append(rec)
    print('  %i records so far' % (len(recs)))
    time.sleep(20)
ejlmod3.writenewXML(recs, publisher, jnlfilename)









