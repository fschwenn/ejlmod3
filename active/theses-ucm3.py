# -*- coding: utf-8 -*-
#harvest theses from UCM, Somosaguas
#FS: 2021-11-30
#FS: 2023-04-28
#FS: 2024-01-21

import sys
import os
#import urllib.request, urllib.error, urllib.parse
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import ssl


publisher = 'UCM, Somosaguas'
jnlfilename = 'THESES-UniversidadComplutenseDeMadrid-%s' % (ejlmod3.stampoftoday())

hdr = {'User-Agent' : 'Magic Browser'}
years = 3
rpp = 60
pages = 15
skipalreadyharvested = True


boring = ['Fac. de Bellas Artes', 'Fac. de Ciencias Biológicas',
          'Fac. de Ciencias Económicas y Empresariales', 'Fac. de Ciencias Químicas',
          'Fac. de Derecho', 'Fac. de Educación', 'Fac. de Enfermería, Fisioterapia y Podología',
          'Fac. de Filosofía', 'Fac. de Geografía e Historia', 'Fac. de Medicina',
          'Fac. de Veterinaria', 'Facultad de Medicina', 'Facultad de Filosofía y Letras',
          'Universidad Complutense de Madrid. Facultad de Medicina',
          'Fac. de Ciencias Políticas y Sociología', 'Fac. de Farmacia', 'Fac. de Filología',
          'Fac. de Psicología', 'Fac. de Trabajo Social', 'Fac. de Psicología', 
          'Fac. de Trabajo Social']

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

baseurl = 'https://docta.ucm.es'



recs = []
for page in range(pages):
    tocurl = baseurl + '/collections/1ec1a8a8-1138-4284-99a5-8907e46de1f3?cp.page=' + str(page+1) + '&cp.rpp=' + str(rpp)
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
                                               'dc.description.faculty', 
                                               'dc.rights', 'dc.language.iso', 
                                               'dc.description.abstract', 'dc.identifier.uri',
                                               'dc.title'],
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
