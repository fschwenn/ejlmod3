# -*- coding: utf-8 -*-
#harvest theses from Guelph U.
#FS: 2022-04-20
#FS: 2023-03-27
#FS: 2023-11-30

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import undetected_chromedriver as uc

jnlfilename = 'THESES-GUELPH-%s' % (ejlmod3.stampoftoday())
publisher = 'Guelph U.'

rpp = 40
pages = 10
skipalreadyharvested = True
years = 2
boring = ['Mechanical Engineering', 'Environmental Sciences', 'Animal and Poultry Science',
          'Chemistry', 'Department of Animal Biosciences', 'Department of Chemistry',
          'Department of Economics and Finance', 'Department of Family Relations and Applied Nutrition',
          'Department of Pathobiology', 'Department of Plant Agriculture', 'Economics', 'Engineering',
          'Family Relations and Applied Nutrition', 'Pathobiology', 'Plant Agriculture', 'Public Health',
          'School of Engineering', 'Department of Population Medicine', 'Bioinformatics', 'Geography', 
          'Biomedical Sciences', 'Clinical Studies', 'Creative Writing', 'Department of Clinical Studies', 
          'Criminology and Criminal Justice Policy', 'Department of Biomedical Sciences', 'English',
          'Department of Geography%2C Environment and Geomatics', 'Department of History', 'History', 
          'Department of Human Health and Nutritional Sciences', 'Department of Integrative Biology',
          'Department of Marketing and Consumer Studies', 'Department of Molecular and Cellular Biology',
          'Department of Psychology', 'Department of Sociology and Anthropology', 'Doctor of Veterinary Science',
          'Human Health and Nutritional Sciences', 'Integrative Biology', 'Landscape Architecture', 'Management', 
          'Latin American and Caribbean Studies', 'Literary Studies %2F Theatre Studies in English',
          'Molecular and Cellular Biology', 'Psychology', 'Rural Planning and Development', 'Sociology',
          'School of English and Theatre Studies', 'School of Environmental Design and Rural Development',
          'School of Languages and Literatures', 'Theatre Studies', 'Veterinary Science', 'Philosophy',
          'Biophysics', 'Collaborative International Development Studies', 'Department of Philosophy', 
          'Department of Food%2C Agricultural and Resource Economics', 'Department of Food Science',
          'Department of Political Science', 'Food%2C Agriculture and Resource Economics', 'Food Science',
          'Political Science', 'School of Environmental Sciences', 'Tourism and Hospitality', 'Toxicology',
          'School of Hospitality%2C Food and Tourism Management', 'Applied Statistics',
          'Department of Environmental Biology', 'Department of Land Resource Science',
          'Environmental Biology', 'Faculty of Environmental Sciences', 'Land Resource Science',
          'Population Medicine', 'Master of Applied Science', 'Master of Fine Arts',
          'Master of Landscape Architecture', 'Master of Science (Planning)', 'Master of Science',
          'Animal Biosciences', 'Artificial Intelligence', 'Bioinformatics', 'Biomedical Sciences',
          'Biophysics', 'Capacity Development and Extension', 'Chemistry', 'Clinical Studies',
          'Creative Writing', 'Economics', 'Engineering', 'Environmental Sciences',
          'Family Relations and Applied Nutrition', 'Food, Agriculture and Resource Economics',
          'Food Science', 'Geography', 'Human Health and Nutritional Sciences', 'Integrative Biology',
          'Landscape Architecture', 'Management', 'Marketing and Consumer Studies',
          'Molecular and Cellular Biology', 'Neuroscience', 'Pathobiology', 'Philosophy',
          'Plant Agriculture', 'Political Science', 'Population Medicine', 'Psychology',
          'Regenerative Medicine', 'Rural Planning and Development', 'Rural Studies', 'Sociology',
          'Tourism and Hospitality', 'Master of Science (Aquaculture)', 'Applied Nutrition',
          'Literary Studies / Theatre Studies in English']

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

baseurl = 'https://atrium.lib.uoguelph.ca'
driver.get(baseurl)
time.sleep(10)    


recs = []
for page in range(pages):
    tocurl = 'https://atrium.lib.uoguelph.ca/collections/50bed0cb-5490-4258-aec6-a4ec4a410bef?cp.page=' + str(page+1) + '&cp.rpp=' + str(rpp)
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    try:
        driver.get(tocurl)
        time.sleep(5)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    except:
        time.sleep(60)
        driver.get(tocurl)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    
    for rec in ejlmod3.ngrx(tocpage, baseurl, ['dc.contributor.advisor', 'dc.contributor.author', 'dc.degree.name', 'dc.date.created', 'dc.degree.programme', 'dc.description.abstract', 'dc.identifier.uri',  'dc.rights.license', 'dc.subject', 'dc.title'], boring=boring, alreadyharvested=alreadyharvested):
        rec['autaff'][-1].append(publisher)
        ejlmod3.printrecsummary(rec)
        #print(rec['thesis.metadata.keys'])
        recs.append(rec)
    print('  %i records so far' % (len(recs)))
    time.sleep(20)
ejlmod3.writenewXML(recs, publisher, jnlfilename)
