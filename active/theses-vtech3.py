# -*- coding: utf-8 -*-
#harvest theses from Virginia Tech., Blacksburg
#FS: 2020-05-29
#FS: 2023-04-03
#FS: 2024-01-03

import sys
import os
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import json

publisher = 'Virginia Tech., Blacksburg'
jnlfilename = 'THESES-VTECH-%s' % (ejlmod3.stampoftoday())
skipalreadyharvested = True

rpp = 100
pages = 5
skipalreadyharvested = True

boring = ['Mechanical Engineering', 'Engineering Education', 'Biological Sciences',
          'Civil Engineering', 'Electrical Engineering',
          #'Computer Science and Applications',
          'Engineering Mechanics', 'Plant Pathology, Physiology and Weed Science',
          'Accounting and Information Systems', 'Aerospace Engineering',
          'Agricultural and Extension Education', 'Animal and Poultry Sciences',
          'Architecture and Design Research', 'Biomedical and Veterinary Sciences',
          'Biomedical Engineering', 'Chemical Engineering', 'Chemistry',
          #'Computer Engineering',
          'Counselor Education', 'Crop and Soil Environmental Sciences',
          'Curriculum and Instruction', 'Educational Leadership and Policy Studies',
          'Educational Research and Evaluation', 'Environmental Design and Planning',
          'Fisheries and Wildlife Science', 'Food Science and Technology',
          'Human Development', 'Industrial and Systems Engineering',
          'Materials Science and Engineering', 'Mining Engineering', 'Psychology',
          'Public Administration/Public Affairs', 'Biochemistry',
          'Social, Political, Ethical, and Cultural Thought',
          'Biological Systems Engineering', 'Business, Finance',
          'Economics, Agriculture and Life Sciences',
          'Business, Executive Business Research',
          'Genetics, Bioinformatics, and Computational Biology',
          'Geosciences', 'Geospatial and Environmental Analysis',
          'Horticulture', 'Human Nutrition, Foods, and Exercise',
          'Leadership and Social Change', 'Nuclear Engineering',
          'Planning, Governance, and Globalization', 'Rhetoric and Writing',
          'Science and Technology Studies', 'Translational Biology, Medicine and Health',
          'Agricultural, Leadership, and Community Education', 'Animal Sciences, Dairy',
          'Business, Business Information Technology', 'Business, Management',
          'Business, Marketing', 'Career and Technical Education',
          'Economics, Science', 'Economics', 'Entomology', 'Forest Products',
          'Forestry', 'Genetics, Bioinformatics and Computational Biology',
          'Higher Education','Hospitality and Tourism Management',
          'Macromolecular Science and Engineering',
          'Plant Pathology, Physiology, and Weed Science',
          'Public Administration and Public Affairs', 'Sociology']
boring += ['Aerospace Engineering', 'Agricultural and Extension Education',
           'Animal Sciences%2C Dairy', 'Architecture and Design Research',
           'Biochemistry', 'Biological Sciences', 'Biomedical and Veterinary Sciences',
           'Biomedical Engineering', 'Business%2C Business Information Technology',
           'Business%2C Executive Business Research', 'Chemical Engineering', 'Chemistry',
           'Civil Engineering', 'Counselor Education', 'Crop and Soil Environmental Sciences',
           'Curriculum and Instruction', 'Educational Leadership and Policy Studies',
           'Electrical Engineering', 'Engineering Education', 'Engineering Mechanics',
           'Entomology', 'Environmental Design and Planning', 'Neurotrauma',
           'Fisheries and Wildlife Science', 'Food Science and Technology', 'Forest Products',
           'Genetics%2C Bioinformatics%2C and Computational Biology', 'Geosciences',
           'Geospatial and Environmental Analysis', 'Higher Education', 'Horticulture',
           'Human Nutrition%2C Foods%2C and Exercise', 'Industrial and Systems Engineering',
           'Materials Science and Engineering', 'Mechanical Engineering',
           'Planning%2C Governance%2C and Globalization', 'Landscape Architecture',
           'Plant Pathology%2C Physiology and Weed Science', 'Psychology',
           'Public Administration%2FPublic Affairs', 'Sociology', 
           'Social%2C Political%2C Ethical%2C and Cultural Thought',
           'Translational Biology%2C Medicine and Health']
boring += ['Agricultural Economics', 'Civil and Environmental Engineering',
           'Counseling and Student Personnel', 'Educational Administration',
           'Environmental Sciences and Engineering', 'Family and Child Development',
           'Geology', 'Industrial Engineering and Operations Research',
           'Materials Engineering Science', 'Plant Pathology',
           'Vocational and Technical Education·', 'Zoology']

options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

baseurl = 'https://vtechworks.lib.vt.edu'
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

recs = []
for page in range(pages):
    tocurl = 'https://vtechworks.lib.vt.edu/collections/2aaadfa0-df04-421b-8779-c6944eb18db0?cp.page=' + str(page+1) + '&cp.rpp=' + str(rpp)
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
                                               'dc.date.issued', 'dc.rights.uri', 
                                               'dc.contributor.department', 'dc.rights', 
                                               'dc.description.abstract', 'dc.identifier.uri',
                                               'dc.subject', 'dc.title',  'thesis.degree.discipline',
                                               'thesis.degree.name'],
                            boring=boring, alreadyharvested=alreadyharvested):
        rec['autaff'][-1].append(publisher)
        ejlmod3.printrecsummary(rec)
        #print(rec['thesis.metadata.keys'])
        recs.append(rec)
    print('  %i records so far' % (len(recs)))
    time.sleep(20)
ejlmod3.writenewXML(recs, publisher, jnlfilename)
