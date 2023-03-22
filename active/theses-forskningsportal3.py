# -*- coding: UTF-8 -*-
#program to harvest theses from national repository forskningsportal.dk
# FS 2022.07.16
# FS 2023-03-17

import sys
import os
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import re
import ejlmod3
import time

publisher = 'Danish National Research Database'
jnlfilename = 'THESES-FORSKNINGSPORTAL-%s' % (ejlmod3.stampoftoday())
pages = 20
skipalreadyharvested = True
boring = ['Department of Biology', 'Department of Molecular Biology and Genetics',
          'Department of Food Science', 'Department of Agroecology',
          'Department of Chemistry and Bioscience', 'Department of Civil Engineering'
          'Department of Nutrition, Exercise and Sports',
          'Department of Environmental Engineering', 'Department of Health Technology',
          'Department of the Built Environment', 'National Institute of Aquatic Resources',
          'Center for Electric Power and Energy', 'Climate & Monitoring',
          'Database and Web Technologies', 'Database, Programming and Web Technologies',
          'Department of Animal Science', 'Department of Biological and Chemical Engineering',
          'Department of Chemistry', 'Department of Civil and Architectural Engineering',
          'Department of Ecoscience', 'Department of Electrical and Computer Engineering',
          'Department of Environmental Science', 'Department of Food and Resource Economics',
          'Department of Geosciences and Natural Resource Management',
          'Department of Geoscience', 'Department of Plant and Environmental Sciences',
          'Division for Structures, Materials and Geotechnics', 'Magnetic Resonance'
          'Division of Civil Engineering and Construction Management',
          'iCLIMATE Aarhus University Interdisciplinary Centre for Climate Change',
          'Department of Architecture, Design and Media Technology',
          'Department of Biotechnology and Biomedicine', 'Digital Design',
          'National Centre for Nano Fabrication and Characterization', 'National Food Institute',
          'Novo Nordisk Foundation Center for Biosustainability',
          'Aalborg Centre for Problem Based Learning in Engineering Science and Sustainability',
          'Department of Chemical and Biochemical Engineering', 'Department of Civil Engineering',
          'Department of Electrical Engineering', 'Department of Electronic Systems',
          'Department of Energy Conversion and Storage', 'Department of Materials and Production',
          'Department of Mechanical Engineering', 'Department of Planning',
          'Department of Science and Environment',  'Acoustic Technology', 'Advanced Biofuels',
          'Applied Power Electronic Systems', 'Automation and Control', 'Batteries',
          'Bio Conversions', 'Center for Communication, Media and Information Technologies',
          'Centre for Acoustic-Mechanical Microsystems', 'Cognitive Systems', 'Design and Processes',
          'Danish Centre for Health Informatics', 'Department of Mechanical and Production Engineering',
          'Department of Nutrition, Exercise and Sports', 'Department of Science Education', 
          'Department of Technology, Management and Economics', 'Department of Wind Energy', 
          'Design for Sustainability', 'Distributed, Embedded and Intelligent Systems',
          'DTU Microbes Initiative', 'Dynamical Systems', 'Electric Power Systems and Microgrids',
          'Electromagnetic Systems', 'Energy and Services', 'Engineering Design and Product Development',
          'Esbjerg Energy Section', 'Faculty of Agricultural Sciences', 'Microgrids', 
          'Fluid Mechanics, Coastal and Maritime Engineering', 'Fluid Power and Mechatronic Systems',
          'Genome Engineering', 'Geotechnics and Geology', 'Glass and Time', 'Human-Centered Computing',
          'Intelligent Energy Systems and Flexible Markets', 'Interdisciplinary Nanoscience Center',
          'Low Power Energy Harvesting and I-Solutions', 'Machine Learning in Photonic Systems',
          'Manufacturing Engineering', 'Materials and Durability', 'Media, Art and Design (MAD)',
          'Molecular and Medical Biology', 'Nanofabrication', 'Photovoltaic Systems',
          'Planning for Urban Sustainability', 'Power Electronic Control, Reliability and System Optimization',
          'Power Electronics System Integration and Materials', 'Power Electronic Systems', 'Production',
          'PROSYS - Process and Systems Engineering Centre', 'Reconstruction',  'Wind Power Systems',
          'Research Group for Food Allergy', 'Research Group for Genomic Epidemiology',
          'Research Group for Molecular and Reproductive Toxicology',  'Solid Mechanics',
          'Strain Design Teams', 'Structured Electromagnetic Materials', 'Structures and Safety',
          'Sustainability, Society and Economics', 'Sustainability', 'SUSTAINABLE DESIGN AND TRANSITION',
          'Sustainable Energy Planning Research Group', 'Techno-Anthropology and Participation',
          'The Danish Centre for Environmental Assessment', 'The Danish Polymer Centre',
          'The Hempel Foundation Coatings Science and Technology Centre (CoaST)', 'The Natural History Museum',
          'Thermal Engineering', 'Ultrafast Infrared and Terahertz Science', 'Visual Computing',
          'Section for Microbial and Chemical Ecology', 'Section for Protein Chemistry and Enzyme Technology',
          'Section for Protein Science and Biotherapeutics', 'Software and Process Engineering',
          'Section for Architecture and Urban Design', 'Section for Media Technology - Campus Aalborg']
boring += ['Business IT', 'Centre for Technology Entrepreneurship', 'Health',
           'Bioinformatics Research Centre (BiRC)', 'Center for Quantitative Genetics and Genomics',
           'Centre for Educational Development - CED', 'Department of Animal and Veterinary Sciences',
           'Department of Clinical Medicine', 'VISION – Center for Visualizing Catalytic Processes',
           'Water Technology & Processes', 'Wind Energy Systems Division',
           'Department of Environmental and Resource Engineering', 'Department of Wind and Energy Systems',
           'AI for the People', 'Astrophysics and Atmospheric Physics',
           'Centre of Excellence for Silicon Photonics for Optical Communications',
           'Cybersecurity Engineering', 'Embedded Systems Engineering', 'Geodesy and Earth Observation',
           'Geomagnetism', 'Nanomaterials and Devices', 'Networks Technology and Service Platforms',
           'Ultra-fast Optical Communication']

options = uc.ChromeOptions()
options.add_argument('--headless')
options.binary_location='/opt/google/chrome/google-chrome'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

def getdatafrommxdlink(rec):
    driver.get(rec['mxdlink'])
    mxdpage = BeautifulSoup(driver.page_source, features="lxml")
    #abstract
    for abs in mxdpage.find_all('mxd:abstract'):
        rec['abs'] = abs.text
    #author
    for person in mxdpage.find_all('mxd:person', attrs = {'pers_role' : 'pau'}):
        for ln in person.find_all('mxd:last'):
            author = ln.text
        for gn in person.find_all('mxd:first'):
            author += ', ' + gn.text
        rec['autaff'] = [[author]]
        for orcid in person.find_all('mxd:id', attrs = {'id_type' : 'orcid'}):
            rec['autaff'][-1].append('ORCID:' + orcid.text)
        for email in person.find_all('mxd:email'):
            rec['autaff'][-1].append('EMAIL:' + email.text)
    #affiliation
    for org in mxdpage.find_all('mxd:organisation', attrs = {'org_role' : 'oaf'}):
        for aff in org.find_all('mxd:name', attrs = {'xml:lang' : 'en'}):
            affiliation = []
            for level in ['mxd:level1', 'mxd:level2', 'mxd:level3']:
                for saff in aff.find_all(level):
                    safft = saff.text.strip()
                    affiliation.append(safft)
                    if safft in ['Algorithms, Logic and Graphs', 'Department of Mathematical Sciences',
                                 'Department of Mathematics']:
                        rec['fc'] = 'm'
                    elif safft in ['Computer Science', 'Department of Computer Science',
                                   'Scientific Computing', 'Software Systems Engineering']:
                        rec['fc'] = 'c'
                    elif safft in ['Statistics and Data Analysis']:
                        rec['fc'] = 's'
                    elif safft in ['Quantum Physics and Information Techology']:
                        rec['fc'] = 'k'
                    elif safft not in ['Faculty of Science', 'Aalborg University',
                                       'Aarhus University', 'Department of Physics and Astronomy']:
                        rec['note'].append('%s:%s' % (level.upper(), safft))
            rec['autaff'][-1].append(', '.join(affiliation))
            for saff in affiliation:
                if saff in boring:
                    rec['keepit'] = False
    #pubnote
    for pbn in mxdpage.find_all('mxd:book'):
        #pages
        for pages in pbn.find_all('mxd:pages'):
            rec['pages'] = pages.text
        #date
        for date in pbn.find_all('mxd:year'):
            rec['date'] = date.text
        #ISBN
        for isbn in pbn.find_all('mxd:isbn'):
            rec['isbn'] = isbn.text
        #DOI
        for doi in pbn.find_all('mxd:doi'):
            rec['doi'] = doi.text    
    #keywords
    for keyw in mxdpage.find_all('mxd:keyword'):
        rec['keyw'].append(keyw.text)
    #pdf_url
    for pdf in mxdpage.find_all('mxd:digital_object', attrs = {'role' : 'pub', 'access' : 'oa'}):
        for link in pdf.find_all('mxd:uri'):
            rec['FFT'] = link.text
    if not 'FFT' in rec:
        for pdf in mxdpage.find_all('mxd:digital_object', attrs = {'role' : 'pub'}):
            for link in pdf.find_all('mxd:uri'):
                rec['pdf_url'] = link.text
    return

def getdatafromartlink(rec):
    return

#collect all toc pages
prerecs = []
starturl = 'https://forskningsportal.dk/local/search/11894'
print(starturl)
driver.get(starturl)
time.sleep(.2)
WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, 'authors')))
time.sleep(.2)
tocpages = [ BeautifulSoup(driver.page_source, features="lxml") ]
for page in range(pages-1):
    xp = '//a[@onclick="paging_set(%i)"]' % (page+2)
    ejlmod3.printprogress('=', [[page+2, pages], [xp]])
    driver.find_element(by=By.XPATH, value=xp).click()
    time.sleep(.2)
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, 'authors')))
    time.sleep(.2)
    tocpages.append(BeautifulSoup(driver.page_source, features="lxml"))
    time.sleep(5)

#get links from toc pages
reclicksplit = re.compile('display_full..(.*).,(\d+),(\d+).')
for page in tocpages:
    for div in page.find_all('div', attrs = {'class' : 'title'}):
        if div.has_attr('onclick'):
            if reclicksplit.search(div['onclick']):
                rec = {'jnl' : 'BOOK', 'tc' : 'T', 'keepit' : True, 'note' : [], 'keyw' : []}
                rec['artlink'] = reclicksplit.sub(r'https://forskningsportal.dk/local/search/11894/\1#record-\2-\3', div['onclick'])
                rec['mxdlink'] = reclicksplit.sub(r'https://forskningsportal.dk/local/dki-cgi/ws/mxd/\1', div['onclick'])
                rec['link'] = reclicksplit.sub(r'https://forskningsportal.dk/local/dki-cgi/ws/cris-link?src=au&id=\1', div['onclick'])
                rec['tit'] = div.text
                if ejlmod3.checkinterestingDOI(rec['mxdlink']):                    
                    prerecs.append(rec)
    print('  %4i records so far' % (len(prerecs)))

#enrich records
i = 0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    getdatafrommxdlink(rec)
    if skipalreadyharvested and 'doi' in rec and rec['doi'] in alreadyharvested:
        print('   %s already in backup' % (rec['doi']))
    elif skipalreadyharvested and 'isbn' in rec and rec['isbn'] in alreadyharvested:
        print('   %s already in backup' % (rec['isbn']))
    elif rec['keepit']:
        if skipalreadyharvested and not 'doi' in rec and '20.2000/LINK/' + re.sub('\W', '', rec['link'][4:]) in alreadyharvested:
            print('   already in backup')
        else:
            ejlmod3.printrecsummary(rec)
            recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['mxdlink'])
    time.sleep(6)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
driver.quit()
