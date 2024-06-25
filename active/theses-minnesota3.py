# -*- coding: utf-8 -*-
#harvest theses from Minnesota U.
#FS: 2020-05-05
#FS: 2022-09-10

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import json
import undetected_chromedriver as uc

publisher = 'Minnesota U.'

rpp = 100
pages = 2
skipalreadyharvested = True

hdr = {'User-Agent' : 'Magic Browser'}
jnlfilename = 'THESES-MINNESOTA-%s' % (ejlmod3.stampoftoday())

boring = ["Aerospace Engineering and Mechanics", "Animal Sciences", "Anthropology",
          "Applied Economics", "Applied Plant Sciences", "Biochemistry, Molecular Bio, and Biophysics",
          "Biological Science", "Biology", "Biomedical Engineering", "Business Administration",
          "Biomedical Informatics and Computational Biology", "Chemical Engineering", "Chemistry",
          "Bioproducts/Biosystems Science Engineering and Management", "Biostatistics",
          "Civil Engineering", "Comparative and Molecular Biosciences", "Comparative Literature",
          "Comparative Studies in Discourse and Society", "Conservation Biology",
          "Design, Housing and Apparel", "Earth Sciences", "Ecology, Evolution and Behavior",
          "Economics", "Educational Policy and Administration", "Educational Psychology",
          "Education, Curriculum and Instruction", "English", "Entomology", "Environmental Health",
          "Epidemiology", "Experimental & Clinical Pharmacology", "Family Social Science", "Geography",
          "Germanic Studies", "Health Services Research, Policy and Administration",
          "History of Science, Technology, and Medicine", "Industrial and Systems Engineering",
          "Industrial Engineering", "Integrative Biology and Physiology", "Kinesiology",
          "Land and Atmospheric Science", "Mass Communication", "Mechanical Engineering",
          "Medicinal Chemistry", "Microbiology, Immunology and Cancer Biology",
          "Molecular, Cellular, Developmental Biology and Genetics", "Music Education", "Music",
          "Natural Resources Science and Management", "Neuroscience", "Nutrition",
          "Organizational Leadership, Policy, and Development", "Pharmacology", "Political Science",
          "Psychology", "Rehabilitation Science", "Rhetoric and Scientific and Technical Communication",
          "Scientific Computation", "Social and Administrative Pharmacy", "Sociology",
          "Speech-Language-Hearing Sciences", "Theatre Arts", "Veterinary Medicine", "American Studies",
          "Biophysical Sciences and Medical Physics", "Biosystems and Agricultural Engineering",
          "Chemical Physics", "Child Psychology", "Communication Studies", "Dentistry", "Design",
          "Education, Work/Community/Family Educ", "Food Science", "French", 'Art History', 'Social Work',
          "Hispanic and Luso Literatures, Cultures & Linguistics", "History of Science and Technology",
          "History", "Linguistics", "Material Science and Engineering", "Nursing", "Pharmaceutics",
          "Philosophy", "Plant and Microbial Biology", "Plant Biological Sciences", "Plant Pathology",
          "Public Affairs", "Soil Science", "Water Resources Science", "Work and Human Resource Education"]

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

baseurl = 'https://conservancy.umn.edu'
collection = 'c8d50607-c28c-423e-92ec-d24ff2089e01'

recs = []
readvisor = re.compile('DC.DESCRIPTION=.*. Advisor: (.*?)\..*')
remajor = re.compile('DC.DESCRIPTION=.* Major: (.*?)\..*')
for page in range(pages):
    keepit = True
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
    for rec in ejlmod3.ngrx(tocpage, baseurl, ['dc.date.issued', 'dc.contributor.author',
                                               'dc.description.abstract', 'dc.subject',
                                               'dc.identifier.uri', 'dc.title',
                                               'dc.description'], boring=boring, alreadyharvested=alreadyharvested):
        if 'autaff' in rec and rec['autaff']:
            rec['autaff'][-1].append(publisher)
        else:
            rec['autaff'] = [[ 'Dee, John' ]]
        for nt in rec['note']:
            #supervisor
            if readvisor.search(nt):
                for advisor in re.split(', ', readvisor.sub(r'\1', nt)):
                    rec['supervisor'].append([[advisor]])
            #subject 
            if remajor.search(nt):
                major = remajor.sub(r'\1', nt)
                if major == 'Astrophysics':
                    rec['fc'] = 'a'
                elif major == 'Computer Science':
                    rec['fc'] = 'c'
                elif major == 'Mathematics':
                    rec['fc'] = 'm'
                elif major == 'Statistics':
                    rec['fc'] = 's'
                elif major in boring:
                    keepit = False
                    print('   skip "%s"' % (major))
                else:
                    rec['note'].append('MAJOR:::' + major)

        if keepit:
#            print(rec['thesis.metadata.keys'])
            ejlmod3.printrecsummary(rec)
            recs.append(rec)
        else:
            ejlmod3.adduninterestingDOI(rec['hdl'])
    print('  %i records so far' % (len(recs)))
    time.sleep(20)
ejlmod3.writenewXML(recs, publisher, jnlfilename)
