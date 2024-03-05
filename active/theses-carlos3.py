# -*- coding: utf-8 -*-
# harvest theses from Carlos III U., Madrid
# JH: 2019-02-23
# FS: 2024-03-04

from requests import Session
from bs4 import BeautifulSoup
import time
import undetected_chromedriver as uc
import ejlmod3
import re
import os

publisher = 'Carlos III U., Madrid'
jnlfilename = 'THESES-CARLOS-%s' % (ejlmod3.stampoftoday())
rpp = 100
years = 3
pages = 3
skipalreadyharvested = False

boring = ['UC3M. Departamento de Biblioteconomía y Documentación', 'UC3M. Departamento de Bioingeniería e Ingeniería Aeroespacial',
          'UC3M. Departamento de Bioingeniería', 'UC3M. Departamento de Ciencia e Ingeniería de Materiales e Ingeniería Química',
          'UC3M. Departamento de Ciencias Sociales', 'UC3M. Departamento de Ingeniería Térmica y de Fluidos',
          'UC3M. Departamento de Derecho Internacional, Eclesiástico y Filosofía del Derecho',
          'UC3M. Departamento de Derecho Penal, Procesal e Historia del Derecho', 'UC3M. Departamento de Derecho Privado',
          'UC3M. Departamento de Derecho Público del Estado', 'UC3M. Departamento de Economía de la Empresa',
          'UC3M. Departamento de Economía', 'UC3M. Departamento de Humanidades: Filosofía, Lenguaje y Literatura',
          'UC3M. Departamento de Humanidades: Historia, Geografía y Arte', 'UC3M. Departamento de Ingeniería Aeroespacial',
          'UC3M. Departamento de Ingeniería Mecánica', 'UC3M. Departamento de Ingeniería Telemática',          
          'UC3M. Departamento de Mecánica de Medios Continuos y Teoría de Estructuras',
          'UC3M. Instituto de Estudios Internacionales y Europeos Francisco de Vitoria',
          'Universidad Carlos III de Madrid. Departamento de Comunicación',
          'Universidad Carlos III de Madrid. Departamento de Humanidades: Filosofía, Lenguaje y Literatura',
          'Universidad Carlos III de Madrid. Departamento de Humanidades: Historia, Geografía y Arte',
          'UC3M. Departamento de Derecho Internacional Público, Eclesiástico y Filosofía del Derecho',
          'UC3M. Departamento de Derecho Social e Internacional Privado', 'UC3M. Departamento de Estadística',
          'UC3M. Departamento de Periodismo y Comunicación Audiovisual',
          'UC3M. Departamento de Teoría de la Señal y Comunicaciones',
          'UC3M. Instituto de Derechos Humanos Gregorio Peces-Barba']

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

baseurl = 'https://e-archivo.uc3m.es'


recs = []
for page in range(pages):
    tocurl = baseurl + '/collections/cc71bb4c-3d65-4232-b37c-92f67466fdd9?cp.page=' + str(page+1) + '&cp.rpp=' + str(rpp)
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    try:
        driver.get(tocurl)
        time.sleep(5)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    except:
        time.sleep(60)
        driver.get(tocurl)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")

    for rec in ejlmod3.ngrx(tocpage, baseurl, ['dc.contributor.advisor', 'dc.contributor.author', 'dc.contributor.departamento',  'dc.date.issued', 'dc.description.abstract', 'dc.description.degree', 'dc.identifier.uri', 'dc.language.iso', 'dc.rights.uri', 'dc.subject.eciencia', 'dc.subject.other', 'dc.title'],
                            boring=boring, alreadyharvested=alreadyharvested):
        if 'autaff' in rec and rec['autaff']:
            rec['autaff'][-1].append(publisher)
        else:
            rec['autaff'] = [['Doe, John', 'Unlisted']]
        #print(rec['thesis.metadata.keys'])
        if 'date' in rec and re.search('[12]\d\d\d', rec['date']) and int(re.sub('.*([12]\d\d\d).*', r'\1', rec['date'])) <= ejlmod3.year(backwards=years):
            print('    too old:', rec['date'])
        else:
            ejlmod3.printrecsummary(rec)
            recs.append(rec)
    print('  %i records so far' % (len(recs)))
    time.sleep(20)
ejlmod3.writenewXML(recs, publisher, jnlfilename)

