# -*- coding: utf-8 -*-
#harvest theses from North Carolina State U.
#FS: 2021-09-07
#FS: 2023-04-18
#FS: 2024-01-09

import sys
import os
#import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
import re
import ejlmod3
import time

publisher = 'North Carolina State U.'

rpp = 100
pages = 6
skipalreadyharvested = True

#hdr = {'User-Agent' : 'Firefox'}
jnlfilename = 'THESES-NCSU-%s' % (ejlmod3.stampoftoday())

boring = ['Mechanical Engineering', 'Electrical Engineering', 'Biology', 'Biomedical Engineering',
          'Chemical Engineering', 'Civil Engineering', 'Educational Adm & Supervision',
          'Fish, Wildlife, and Con Bio', 'Forestry and Environmental Res', 'Horticultural Science',
          'Psychology', 'Aerospace Engineering', 'Chemistry', 'Comm, Rhetoric & Digital Media',
          'Computer Engineering', 'Economics', 'Ed Leadership Policy Human Dev',
          'Fiber & Polymer Science', 'Food Science', 'Forest Biomaterials', 'Genetics',
          'Learning and Teaching in STEM', 'Material Science & Engineering', 'Public History',
          'Sociology', 'Soil Science', 'Statistics', 'Teacher Educ and Learning Sci',
          'Materials Science & Engineering', 'Plant Biology', 'Plant Pathology',
          'Animal Sci & Poultry Sci', 'Bioinformatics', 'Biological & Agri Engineering',
          'Applied Mathematics', 'Counseling & Counselor Educ', 'Crop Science',
          'Ed Research & Policy Analysis', 'Mathematics Education', 'Microbiology',
          'Adult and Community College Education', 'Adult and Higher Education',
          'Agricultural and Extension Education', 'Agricultural Education', 'Animal and Poultry Science',
          'Animal SciencePoultry ScienceFunctional Genomics', 'Animal SciencePoultry Science',
          'Animal Science', 'Biochemistry', 'BioinformaticsStatistics', 'Botany', 'ChemistryStatistics',
          'Comm Rhetoric & Digital Media', 'Communication, Rhetoric, and Digital Media',
          'Comparative Biomedical Sciences',
          'Counseling and Counselor Education', 'Counselor Education', 'Curriculum and Instruction',
          'Curriculum Studies', 'EconomicsStatistics', 'EdD', 'Educational Administration and Supervision',
          'Educational Psychology', 'Educational Research and Policy Analysis', 'Engineering',
          'Extension Education', 'Fiber and Polymer ScienceBiomedical Engineering',
          'Fiber and Polymer ScienceElectrical Engineering', 'ForestryNatural Resources', 'Forestry',
          'Functional Genomics', 'Geospatial Analytics', 'Higher Education Administration', 'Immunology',
          'Industrial EngineeringIndustrial Engineering', 'Marine, Earth and Atmospheric Sciences',
          'Materials Science and Engineering', 'Math, Science and Technology Education',
          'NutritionAnimal Science', 'Occupational Education', 'Operations ResearchComputer Science',
          'Operations ResearchElectrical Engineering', 'Parks, Recreation and Tourism Management',
          'Physiology', 'Plant PathologyCrop Science', 'Poultry Science', 'School Counseling',
          'Technology Education', 'Textiles', 'Training and Development', 'Wood and Paper Science',
          'Fiber and Polymer ScienceWood and Paper Science', 'Fisheries and Wildlife Sciences',
          'Fisheries, Wildlife, and Conservation Biology', 'Forestry and Environmental Resources', 
          'Fiber and Polymer ScienceMaterials Science and Engineering', 'Fiber and Polymer Science', 
          'Curriculum and Instruction, English Education', 'Curriculum and Instruction, Reading', 
          'Biological and Agricultural Engineering', 'Biomedical EngineeringFiber and Polymer Science', 
          'Science Education', 'Biomathematics', 'Comm, Rhetoric & Digital Media',
          'Comparative Biomedical Sci', 'Nutrition', 'Parks, Rec and Tourism Mgmt',
          'Curriculum & Instruction', 'Design', 'Entomology', 'Fiber & Polymer Science',
          'Industrial Engineering', 'Marine, Earth & Atmos Sciences', 'Zoology',
          'Material Science & Engineering', 'Materials Science & Engineering',
          'Operations Research', 'Public Administration', 'Toxicology', 'Textile Technology Management']
boring += ['Animal Sci &a; Poultry Sci', 'Biological &a; Agri Engineering',
           'Comm, Rhetoric &a; Digital Media', 'Counseling &a; Counselor Educ',
           'Curriculum &a; Instruction', 'Ed Research &a; Policy Analysis',
           'Fiber &a; Polymer Science', 'Marine, Earth &a; Atmos Sciences', 'Agricultural Economics',
           'Educational Leadership, Policy and Human Development']

options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

baseurl = 'https://repository.lib.ncsu.edu'

recs = []
for page in range(pages):
    tocurl = 'https://repository.lib.ncsu.edu/collections/a6d35d83-348f-46b8-a93a-ef66db6c4c1c?cp.page=' + str(page+1) + '&cp.rpp=' + str(rpp)
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
                                               'dc.date.issued',
                                               'dc.degree.discipline', 
                                               'dc.department', 'dc.rights', 
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





