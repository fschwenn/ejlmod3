# -*- coding: utf-8 -*-
#harvest theses from Amsterdam
#FS: 2020-11-02
#FS: 2023-04-17

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


jnlfilename = 'THESES-AMSTERDAM-%s' % (ejlmod3.stampoftoday())
publisher = 'Amsterdamh U.'

pages = 10
skipalreadyharvested = True
boringinstitutes = ['InstituteforBiodiversityandEcosystemDynamicsIBED',
                    'InstituteforLogicLanguageandComputationILLC',
                    'KortewegdeVriesInstituteforMathematicsKdVI',
                    'SwammerdamInstituteforLifeSciencesSILSInstituteforBiodiversityandEcosystemDynamicsIBED',
                    'SwammerdamInstituteforLifeSciencesSILS',
                    'AmsterdamNeuroscience',
                    'InstituteforBiodiversityandEcosystemDynamicsIBEDSwammerdamInstituteforLifeSciencesSILS',
                    'VanderWaalsZeemanInstituteWZI', 'AmsterdamNeuroscience'
                    'VantHoffInstituteforMolecularSciencesHIMSSwammerdamInstituteforLifeSciencesSILS',
                    'VantHoffInstituteforMolecularSciencesHIMS']

options = uc.ChromeOptions()
options.binary_location='/opt/google/chrome/google-chrome'
#options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)
driver.implicitly_wait(30)
driver.get('https://dare.uva.nl')
driver.page_source              
time.sleep(2)

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

prerecs = []
for page in range(pages):
    tocurl = 'https://dare.uva.nl/search?sort=year;field1=meta;join=and;field2=meta;smode=advanced;sort-publicationDate-max=2100;typeClassification=PhD%20thesis;organisation=Faculty%20of%20Science%20(FNWI);startDoc='+str(10*page+1)
    ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
    driver.get(tocurl)
    tocpage = BeautifulSoup(driver.page_source, features='lxml')
    for i in tocpage.body.find_all('i', attrs = {'class' : 'fa-square-o'}):
        if i.has_attr('data-identifier'):
            rec = {'tc' : 'T',  'jnl' : 'BOOK', 'autaff' : [], 'note' : [], 'supervisor' : []}
            rec['artlink'] = 'https://dare.uva.nl/search?identifier=' + i['data-identifier']
            rec['hdl'] = '11245.1/' + i['data-identifier']
            if ejlmod3.checkinterestingDOI(rec['hdl']):
                if not skipalreadyharvested or not rec['hdl'] in alreadyharvested:
                    prerecs.append(rec)                    
    time.sleep(2)

recs = []
i = 0 
for rec in prerecs:
    i += 1
    keepit = True
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        driver.get(rec['artlink'])
        artpage = BeautifulSoup(driver.page_source, features='lxml')
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['artlink']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features='lxml')
        except:
            print("no access to %s" % (rec['artlink']))
            continue    
    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'citation_title', 'citation_isbn',
                                        'citation_publication_date', 'citation_pdf_url'])
    for dl in artpage.body.find_all('dl'):
        for child in dl.children:
            try:
                child.name
            except:
                continue
            if child.name == 'dt':
                dtt = child.text
            elif child.name == 'dd':
                #author
                if dtt == 'Author':
                    for a in child.find_all('a'):
                        if a.has_attr('href'):
                            if re.search('field1=dai', a['href']):
                                rec['autaff'] = [[ a.text.strip() ]]
                            elif re.search('orcid.org', a['href']):
                                rec['autaff'][-1].append(re.sub('.*orcid.org\/', 'ORCID:', a['href']))
                #supervisor
                if dtt == 'Supervisors':
                    for div in child.find_all('div'):
                        for a in div.find_all('a'):
                            if a.has_attr('href'):
                                if re.search('search', a['href']):
                                    rec['supervisor'].append([ a.text.strip() ])
                                elif re.search('orcid.org', a['href']):
                                    rec['supervisor'][-1].append(re.sub('.*orcid.org\/', 'ORCID:', a['href']))
                #apges
                if dtt == 'Number of pages':
                    rec['pages'] = re.sub('\D*(\d\d+).*', r'\1', child.text.strip())
                #Institute
                if dtt == 'Institute':
                    institute = re.sub('\W', '', child.text.strip())
                    if institute in boringinstitutes:
                        keepit = False
                        print('  skip "%s"' % (institute))
                    elif institute in ['InformaticsInstituteIVI']:
                        rec['fc'] = 'c'
                    elif institute in ['AntonPannekoekInstituteforAstronomyAPI']:
                        rec['fc'] = 'a'
                    else:
                        rec['note'].append(child.text.strip())
                #Abstract
                if dtt == 'Abstract':
                    rec['abs'] = child.text.strip()
                #HDL
                if dtt == 'Permalink':
                    for a in child.find_all('a'):
                        if a.has_attr('href'):
                            if re.search('handle.net', a['href']):
                                rec['hdl'] = re.sub('.*handle.net\/', '', a['href'])
    if keepit:
        recs.append(rec)
        ejlmod3.printrecsummary(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['hdl'])
        
ejlmod3.writenewXML(recs, publisher, jnlfilename)
