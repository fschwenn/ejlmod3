# -*- coding: utf-8 -*-
#harvest theses from Middle East Tech. U., Ankara
#works only on FS' notebook
#FS: 2021-01-02
#FS: 2023-01-02

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import undetected_chromedriver as uc
from selenium.webdriver.remote.webdriver import By

pages = 20
skipalreadyharvested = True

publisher = 'Middle East Tech. U., Ankara'
jnlfilename = 'THESES-MiddleEastTechUAnkara-%s' % (ejlmod3.stampoftoday())

tocurl = 'https://open.metu.edu.tr/handle/11511/158'

boringdegrees = ['M.S. - Master of Science', 'M.A. - Master of Arts', 'M.Arch. - Master of Architecture',
                 'Thesis (M.Arch.) -- Graduate School of Natural and Applied Sciences. Architecture.',
                 'Thesis (M.Arch.) -- Graduate School of Natural and Applied Sciences. Conservation of Cultural Heritage in Architecture.',
                 'Thesis (M.S.) -- Graduate School of Applied Mathematics. Mathematics.',
                 'Thesis (M.S.) -- Graduate School of Informatics. Operational Research.',
                 'Thesis (M.S.) -- Graduate School of Natural and Applied Sciences. Aerospace Engineering.',
                 'Thesis (M.S.) -- Graduate School of Natural and Applied Sciences. Archaeometry.',
                 'Thesis (M.S.) -- Graduate School of Natural and Applied Sciences. Biochemistry.',
                 'Thesis (M.S.) -- Graduate School of Natural and Applied Sciences. Biology.',
                 'Thesis (M.S.) -- Graduate School of Natural and Applied Sciences. Biomedical Engineering.',
                 'Thesis (M.S.) -- Graduate School of Natural and Applied Sciences. Biotechnology.',
                 'Thesis (M.S.) -- Graduate School of Natural and Applied Sciences. Building Science in Architecture.',
                 'Thesis (M.S.) -- Graduate School of Natural and Applied Sciences. Chemical Engineering.',
                 'Thesis (M.S.) -- Graduate School of Natural and Applied Sciences. Chemistry.',
                 'Thesis (M.S.) -- Graduate School of Natural and Applied Sciences. City and Regional Planning.',
                 'Thesis (M.S.) -- Graduate School of Natural and Applied Sciences. Civil Engineering.',
                 'Thesis (M.S.) -- Graduate School of Natural and Applied Sciences. Computer Education and Instructional Technology.',
                 'Thesis (M.S.) -- Graduate School of Natural and Applied Sciences. Computer Engineering.',
                 'Thesis (M.S.) -- Graduate School of Natural and Applied Sciences . Earthquake Studies.',
                 'Thesis (M.S.) -- Graduate School of Natural and Applied Sciences. Earth System Science.',
                 'Thesis (M.S.) -- Graduate School of Natural and Applied Sciences. Electrical and Electronics Engineering.',
                 'Thesis (M.S.) -- Graduate School of Natural and Applied Sciences. Engineering Sciences.',
                 'Thesis (M.S.) -- Graduate School of Natural and Applied Sciences. Environmental Engineering.',
                 'Thesis (M.S.) -- Graduate School of Natural and Applied Sciences. Food Engineering.',
                 'Thesis (M.S.) -- Graduate School of Natural and Applied Sciences. Geodetic and Geographical Information Technologies.',
                 'Thesis (M.S.) -- Graduate School of Natural and Applied Sciences. Geological Engineering.',
                 'Thesis (M.S.) -- Graduate School of Natural and Applied Sciences. Industrial Design.',
                 'Thesis (M.S.) -- Graduate School of Natural and Applied Sciences. Industrial Engineering.',
                 'Thesis (M.S.) -- Graduate School of Natural and Applied Sciences. Mathematics and Science Education.',
                 'Thesis (M.S.) -- Graduate School of Natural and Applied Sciences. Mechanical Engineering.',
                 'Thesis (M.S.) -- Graduate School of Natural and Applied Sciences. Metallurgical and Materials Engineering.',
                 'Thesis (M.S.) -- Graduate School of Natural and Applied Sciences. Micro and Nanotechnology.',
                 'Thesis (M.S.) -- Graduate School of Natural and Applied Sciences. Mining Engineering.',
                 'Thesis (M.S.) -- Graduate School of Natural and Applied Sciences. Molecular Biology and Genetics',
                 'Thesis (M.S.) -- Graduate School of Natural and Applied Sciences. Occupational Health and Safety.',
                 'Thesis (M.S.) -- Graduate School of Natural and Applied Sciences. Operational Research.',
                 'Thesis (M.S.) -- Graduate School of Natural and Applied Sciences. Petroleum and Natural Gas Engineering.',
                 'Thesis (M.S.) -- Graduate School of Natural and Applied Sciences. Physics.',
                 'Thesis (M.S.) -- Graduate School of Natural and Applied Sciences. Polymer Science and Technology.',
                 'Thesis (M.S.) -- Graduate School of Natural and Applied Sciences. Statistics.',
                 'Thesis (M.S.) -- Graduate School of Natural and Applied Sciences. Urban Design in City and Regional Planning Department.',
                 'Thesis (M.S.) -- Graduate School of Social Sciences. Elementary Science and Mathematics Education.', 
                 'Thesis (M.S.) -- Graduate School of Social Sciences. Secondary Science and Mathematics Education.',
                 'Thesis (M.S.) -- Graduate School of Social Sciences. Elementary Science and Mathematics Education.',
                 'Thesis (Ph.D.) -- Graduate School of Informatics. Geodetic and Geographical Information Technologies',
                 'Thesis (Ph.D.) -- Graduate School of Natural and Applied Sciences. Aerospace Engineering.',
                 'Thesis (Ph.D.) -- Graduate School of Natural and Applied Sciences. Archaeometry.',
                 'Thesis (Ph.D.) -- Graduate School of Natural and Applied Sciences. Architecture.',
                 'Thesis (Ph.D.) -- Graduate School of Natural and Applied Sciences. Biology.',
                 'Thesis (Ph.D.) -- Graduate School of Natural and Applied Sciences. Biomedical Engineering.',
                 'Thesis (Ph.D.) -- Graduate School of Natural and Applied Sciences. Biotechnology.',
                 'Thesis (Ph.D.) -- Graduate School of Natural and Applied Sciences. Chemical Engineering.',
                 'Thesis (Ph.D.) -- Graduate School of Natural and Applied Sciences. Chemistry.',
                 'Thesis (Ph.D.) -- Graduate School of Natural and Applied Sciences. City and Regional Planning.',
                 'Thesis (Ph.D.) -- Graduate School of Natural and Applied Sciences. Civil Engineering.',
                 'Thesis (Ph.D.) -- Graduate School of Natural and Applied Sciences. Computer Education and Instructional Technology.',
                 'Thesis (Ph.D.) -- Graduate School of Natural and Applied Sciences. Conservation of Cultural Heritage in Architecture.',
                 'Thesis (Ph.D.) -- Graduate School of Natural and Applied Sciences. Earth System Science.',
                 'Thesis (Ph.D.) -- Graduate School of Natural and Applied Sciences. Electrical and Electronics Engineering.',
                 'Thesis (Ph.D.) -- Graduate School of Natural and Applied Sciences. Food Engineering.',
                 'Thesis (Ph.D.) -- Graduate School of Natural and Applied Sciences. Geological Engineering.',
                 'Thesis (Ph.D.) -- Graduate School of Natural and Applied Sciences. Industrial Design.',
                 'Thesis (Ph.D.) -- Graduate School of Natural and Applied Sciences. Industrial Engineering.',
                 'Thesis (Ph.D.) -- Graduate School of Natural and Applied Sciences. Mechanical Engineering.',
                 'Thesis (Ph.D.) -- Graduate School of Natural and Applied Sciences. Metallurgical and Materials Engineering.',
                 'Thesis (Ph.D.) -- Graduate School of Natural and Applied Sciences. Micro and Nanotechnology.',
                 'Thesis (Ph.D.) -- Graduate School of Natural and Applied Sciences. Mining Engineering.',
                 'Thesis (Ph.D.) -- Graduate School of Natural and Applied Sciences. Petroleum and Natural Gas Engineering.',
                 'Thesis (Ph.D.) -- Graduate School of Natural and Applied Sciences. Polymer Science and Technology.',
                 'The Center for Solar Energy Research and Applications (ODTÜ-GÜNAM) at Middle East Technical University partially funds the research presented here.',
                 'Thesis (Ph.D.) -- Graduate School of Social Sciences. Mathematics and Science Education.',
                 'M.C.P. - Master of City Planning']
#driver
options = uc.ChromeOptions()
options.add_argument('--headless')
options.binary_location='/opt/google/chrome/google-chrome'
options.binary_location='/usr/bin/chromium'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

prerecs = []
driver.get(tocurl)
for page in range(pages):
    ejlmod3.printprogress('=', [[page+1, pages]])
    tocpage = BeautifulSoup(driver.page_source, 'lxml')
    for a in tocpage.body.find_all('a', attrs = {'class' : 'ui-link'}):
        if a.has_attr('href') and re.search('handle', a['href']):
            rec = {'tc' : 'T', 'jnl' : 'BOOK', 'keyw' : [], 'note' : []}
            rec['hdl'] = re.sub('.*handle\/', '', a['href'])
            if ejlmod3.checkinterestingDOI(rec['hdl']):
                rec['link'] = 'https://open.metu.edu.tr' + a['href']
                rec['tit'] = a.text.strip()
                if not skipalreadyharvested or not rec['hdl'] in alreadyharvested:
                    prerecs.append(rec)
    #next page
    for el in driver.find_elements(By.CLASS_NAME, "ui-paginator-next"):
        el.click()
    print('  %4i records so far' % (len(prerecs)))
    time.sleep(10)

i = 0
recs = []
for rec in prerecs:
    keepit = True
    i += 1
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        driver.get(rec['link'])
        artpage = BeautifulSoup(driver.page_source, features="lxml")
    except:
        print(' ... try again in 5 minutes')
        time.sleep(300)
        driver.get(rec['link'])
        artpage = BeautifulSoup(driver.page_source, 'lxml')       
    time.sleep(5)
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'DCTERMS.extent', 'DC.subject', 'citation_date'])    
    rec['autaff'][-1].append(publisher)                                    
    for meta in artpage.find_all('meta'):
        if meta.has_attr('name') and meta.has_attr('content'):
            #abstract
            if meta['name'] == 'DCTERMS.abstract':
                if re.search(' the ', meta['content']):
                    rec['abs'] = meta['content']
            #license
            elif meta['name'] == 'DC.rights,DCTERMS.URI':
                rec['license'] = {'url' : meta['content']}
            #fulltext
            elif meta['name'] == 'citation_pdf_url':
                if not re.search('[öşüçğıÇŞ]', meta['content']):
                    rec['FFT'] = meta['content']
            #type
            elif meta['name'] == 'DC.description':
                if meta['content'] in boringdegrees:
                    print(' skip "%s"' % (meta['content']))
                    keepit = False
                elif not meta['content'] in ['Ph.D. - Doctoral Program']:
                    rec['note'].append(meta['content'])
    if keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['hdl'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
