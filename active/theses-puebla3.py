# -*- coding: utf-8 -*-
#harvest theses from Puebla U.
#JH: 2022-06-07
#FS: 2022-09-04
#FS: 2024-01-09


import getopt
import sys
import os
import codecs
import re
import datetime
import ejlmod3
import undetected_chromedriver as uc
#from selenium import webdriver
from bs4 import BeautifulSoup
import time

# Initiate webdriver
#driver = webdriver.PhantomJS()
options = uc.ChromeOptions()
options.headless=True
options.binary_location='/usr/bin/google-chrome'
options.binary_location='/usr/bin/chromium'
options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)


publisher = 'Puebla U., Inst. Fis.'
jnlfilename = 'THESES-PUEBLA-%s' % (ejlmod3.stampoftoday())

recs = []

rpp = 50
pages = 3
skipalreadyharvested = True

boring = ['Facultad de Ciencias Químicas', 'Área de Ciencias Sociales y Humanidades',
          'Área Económico Administrativa', 'Área de Ciencias Sociales',
          'Área de Educación y Humanidades']
boring += ['Facultad de Economía', 'Facultad de Derecho y Ciencias Sociales',
           'Facultad de Arquitectura', 'Instituto de Fisiología',
           'nstituto de Ciencias de Gobierno y Desarrollo Estratégico<',
           'Facultad de Filosofía y Letras',
           'Área de Ciencias Sociales y Humanidades',
           'Área Económico Administrativa', 'BIOLOGÍA Y QUÍMICA']

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []


baseurl = 'https://repositorioinstitucional.buap.mx'

recs = []
for page in range(pages):
    tocurl = 'https://repositorioinstitucional.buap.mx/collections/93b25a1c-3323-4825-89ea-148db1250f42?cp.page=' + str(page+1) + '&cp.rpp=' + str(rpp)
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
                                               'dc.subject.classification', 'dc.language.iso',
                                               'dc.department', 'dc.description.abstract',
                                               'dc.identifier.uri',  'dc.thesis.degreediscipline',
                                               'dc.subject', 'dc.title',
                                               'dc.rights.uri', 'dc.subject.lcc']:
                            boring=boring, alreadyharvested=alreadyharvested):
        rec['autaff'][-1].append(publisher)
        ejlmod3.printrecsummary(rec)
        #print(rec['thesis.metadata.keys'])
        recs.append(rec)
    print('  %i records so far' % (len(recs)))
    time.sleep(20)
ejlmod3.writenewXML(recs, publisher, jnlfilename)








