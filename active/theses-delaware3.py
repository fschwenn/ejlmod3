# -*- coding: utf-8 -*-
#harvest theses from Delaware
#JH: 2019-09-11
#FS: 2024-01-22

import undetected_chromedriver as uc
import time
from bs4 import BeautifulSoup
import ejlmod3
import re
import os

publisher = 'U. Delaware, Newark'
jnlfilename = 'THESES-DELAWARE-%s' % (ejlmod3.stampoftoday())
rpp = 100
pages = 4
years = 2
skipalreadyharvested = True
boring = []
for b in ["School of Education", "Department of Plant and Soil Sciences",
          "Department of Political Science and International Relations",
          "Universith of Delaware, Department of Kinesiology and Applied Physiology",
          "Biomechanics and Movement Science Program",
          "Biomechanics and Movement Science", "Biomedical Engineering Department",
          "Program in Biomechanics and Movement Science",
          "Center for Bioinformatics and Computational Biology",
          "Department of Animal and Food Sciences", "Department of History",
          "Department of Applied Physiology", "Department of Art Conservation",
          "Department of Art History", "Department of Behavioral Health and Nutrition",
          "Department of Biological Sciences", "Department of Biomedical Engineering",
          "Department of Chemical &amp; Biomolecular Engineering",
          "Department of Chemical and Biomolecular Engineering",
          "Department of Chemistry and Biochemistry",
          "Department of Civil and Environmental Engineering",
          "University of Delaware. Department of Civil and Environmental Engineering",
          "Department of Earth Sciences", "Department of Economics",
          "Department of English", "Department of Entomology and Wildlife Ecology",
          "Department of Entomology and Wildlife Ecology.",
          "Department of Geography and Spatial Sciences",
          "Department of Geography", "Department of Geological Sciences",          
          "Department of Human Development and Family Sciences",
          "Department of Kinesiology and Applied Physiology",
          "Department of Kinesiology and Applied Physiology.",
          "Department of Linguistics and Cognitive Science",
          "Department of Medical and Molecular Sciences",
          "Department of Medical Laboratory Sciences",
          "Department of Psychological and Brain Sciences",
          "Department of Sociology and Criminal Justice",
          "Department Sociology and Criminal Justice",
          "Disaster Science and Management Program",
          "Energy and Environmental Policy Program",
          "Institute for Financial Services Analytics",
          "School of Marine Science and Policy",
          "School of Nursing", "School of Public Policy and Administration",
          "Water Science and Policy Program",
          "Center for Bioinformatics and Computational BiologyDepartment of Animal and Food Sciences",
          "Center for Energy & Environmental Policy",
          "Center for Energy and Environmental Policy",
          "Department of Chemical & Biomolecular Engineering",
          "Department of Chemical and Biochemical Engineering",
          "University of Delaware,Department of Chemical and Biomolecular Engineering",
          "Department of Chemical Engineering", "Department of Department",
          "Department of Civil & Environmental Engineering",
          "Department of Dept. of Political Science and International Relations",
          "Department of Entomology & Wildlife Ecology",
          "Department of Geology", "Department of History",
          "Department of Human Development & Family Studies",
          "Department of Human Development and Family",
          "Department of Human Development and Family Studies",
          "Department of Human Development and Family Studies.",
          "Department of Kinesiology & Applied Physiology",
          "Department of Kinesiology and Applied Physiology",
          "Department of Linguistics & Cognitive Sciences",
          "Department of Linguistics & Cognitive Science",
          "Department of Linguistics & Cognitive Science.",
          "Department of Linguistics and Cognitive Sciences",
          "Department of Physical Therapy.", "Department of Sociology",
          "Department of Plant & Soil Sciences",
          "Department of Political Science & International Relations",
          "Department of Psychological & Brain Sciences",
          "Department of Psychology", 'Department of Physical Therapy',
          "Department of School of Marine Science and Policy",
          "Department of Sociology & Criminal Justice",
          "Department of Sociology and Criminal Justice.",
          'Department of Health Behavior and Nutrition Sciences',
          "Materials Science and Engineering",
          "School of Marine Science & Policy",
          "School of Marine Sciences & Policy",
          "School of Public Policy & Administration"]:
    boring.append(b,)
    boring.append('University of Delaware, '+b)
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium'
options.binary_location='/usr/bin/google-chrome'
options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

baseurl = 'https://udspace.udel.edu'

recs = []
for page in range(pages):
    tocurl = baseurl + '/collections/1de73a61-b4e3-4551-8a96-434f1373cfe6?cp.page=' + str(page+1) + '&cp.rpp=' + str(rpp)
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
                                               'dc.date.issued', 'dc.subject.keyword',
                                               'dc.description.faculty', 'dc.description.department',
                                               'dc.description.abstract', 'dc.identifier.uri',
                                               'dc.rights', 'dc.subject', 'dc.title'],
                            boring=boring, alreadyharvested=alreadyharvested):
        rec['autaff'][-1].append(publisher)
        ejlmod3.printrecsummary(rec)
        #print(rec['thesis.metadata.keys'])
        if 'date' in rec and re.search('[12]\d\d\d', rec['date']) and int(re.sub('.*([12]\d\d\d).*', r'\1', rec['date'])) <= ejlmod3.year(backwards=years):
            print('    too old:', rec['date'])
        else:
            recs.append(rec)
    print('  %i records so far' % (len(recs)))
    time.sleep(20)
ejlmod3.writenewXML(recs, publisher, jnlfilename)
