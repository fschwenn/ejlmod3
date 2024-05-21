# -*- coding: utf-8 -*-
#harvest theses from Santa Maria U., Valparaiso
#FS: 2020-03-24
#FS: 2023-03-15
#FS: 2024-05-11

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import undetected_chromedriver as uc
import time
import mechanize
import unicodedata

publisher = 'Santa Maria U., Valparaiso'
jnlfilename = 'THESES-SANTAMARIA-%s' % (ejlmod3.stampoftoday())

pages = 5
rpp = 60
skipalreadyharvested = True
boring = ['Universidad Técnica Federico Santa María. Departamento de Arquitectura',
          'Universidad Técnica Federico Santa María. Departamento de Electrónica',
          'Universidad Técnica Federico Santa María. Departamento de Industrias',
          'Universidad Técnica Federico Santa María. Departamento de Ingeniería Comercial',
          'Universidad Técnica Federico Santa María. Departamento de Ingeniería Química y Ambiental',
          'Universidad Técnica Federico Santa María. Departamento de Química',
          'Universidad Técnica Federico Santa María. Departamento de Química y Medio Ambiente']
boring += ['INGENIERO CIVIL MECÁNICO', 'INGENIERO DE EJECUCIÓN EN GESTIÓN INDUSTRIAL',
           'INGENIERO EN CONSTRUCCIÓN CON LICENCIATURA EN INGENIERÍA',
           'INGENIERO EN PREVENCIÓN DE RIESGOS LABORALES Y AMBIENTALES',
           'DEPARTAMENTO DE INGENIERÍA MECÁNICA. INGENIERÍA CIVIL MECÁNICA',
           'INGENIERÍA DE EJECUCIÓN EN GESTIÓN INDUSTRIAL',
           'INGENIERÍA EN CONSTRUCCIÓN CON LICENCIATURA EN INGENIERÍA',
           'INGENIERÍA EN PREVENCIÓN DE RIESGOS LABORALES Y AMBIENTALES',
           'INGENIERÍA EN DISEÑO DE PRODUCTOS',
           'INGENIERÍA EN PREVENCIÓN DE RIESGOS LABORALES Y AMBIENTALES',
           'INGENIERÍA MECÁNICA',
           'MAGÍSTER EN CIENCIAS DE LA INGENIERÍA ELÉCTRICA',
           'MAGÍSTER EN CIENCIAS, MENCIÓN FÍSICA',
           'DEPARTAMENTO DE INGENIERÍA MECÁNICA. INGENIERÍA CIVIL MECÁNICA – MENCIÓN PRODUCCIÓN',
           'DEPARTAMENTO DE INGENIERÍA MECÁNICA. INGENIERÍA CIVIL MECÁNICA',
           'DEPARTAMENTO DE INGENIERÍA MECÁNICA. MAGÍSTER EN CIENCIAS DE INGENIERÍA MECÁNICA',
           'DEPARTAMENTO DE INGENIERÍA METALÚRGICA Y DE MATERIALES. INGENIERÍA CIVIL DE MINAS',
           'DEPARTAMENTO DE INGENIERÍA METALÚRGICA Y DE MATERIALES. INGENIERÍA CIVIL METALÚRGICA',
           'DEPARTAMENTO DE OBRAS CIVILES. CONSTRUCCIÓN CIVIL',
           'DEPARTAMENTO DE OBRAS CIVILES. INGENIERÍA CIVIL',
           'MAGISTER EN CIENCIAS DE INGENIERIA MECANICA',
           'MAGISTER EN CIENCIAS DE LA INGENIERIA ELECTRICA',
           'MAGISTER EN CIENCIAS DE LA INGENIERIA INFORMATICA',
           'MAGISTER EN CIENCIAS MENCION FISICA', 'CONSTRUCTOR CIVIL',
           'DEPARTAMENTO DE INGENIERÍA MECÁNICA. INGENIERO(A) CIVIL MECÁNICO(A) – MENCIÓN PRODUCCIÓN',
           'DOCTOR EN INGENIERIA MECANICA', 'INGENIERO(A)A EN MANTENIMIENTO INDUSTRIAL',
           'INGENIERO(A) MECÁNICO(A)', 'INGENIERO CIVIL DE MINAS',
           'INGENIERO CIVIL ELECTRICISTA', 'INGENIERO CIVIL INFORMÁTICO',
           'INGENIERO CIVIL MECÁNICO', 'INGENIERO DE EJECUCIÓN EN GESTIÓN INDUSTRIAL',
           'INGENIERO DE EJECUCIÓN EN MECÁNICA DE PROCESOS Y MANTENIMIENTO INDUSTRIAL',
           'INGENIERO EN CONSTRUCCIÓN CON LICENCIATURA EN INGENIERÍA',
           'INGENIERO EN DISEñO DE PRODUCTOS',
           'INGENIERO EN PREVENCIÓN DE RIESGOS LABORALES Y AMBIENTALES',
           'INGENIERO MECÁNICO	INDUSTRIAL', 'LICENCIADO EN CIENCIAS , MENCIÓN FÍSICA.',
           'MAGISTER EN CIENCIAS DE INGENIERIA MECANICA',
           'MAGISTER EN CIENCIAS DE LA INGENIERIA ELECTRICA',
           'MAGISTER EN CIENCIAS DE LA INGENIERIA INFORMATICA',
           'DEPARTAMENTO DE INFORMÁTICA. MAGÍSTER EN CIENCIAS DE LA INGENIERÍA INFORMÁTICA',
           'DEPARTAMENTO DE INGENIERÍA COMERCIAL. INGENIERÍA COMERCIAL',
           'DEPARTAMENTO DE INGENIERÍA MECÁNICA. DOCTORADO EN INGENIERÍA MECÁNICA',
           'DEPARTAMENTO DE INGENIERÍA MECÁNICA. INGENIERÍA CIVIL MECÁNICA – MENCIÓN PRODUCCIÓN',
           'DEPARTAMENTO DE INGENIERÍA MECÁNICA. INGENIERÍA CIVIL MECÁNICA',
           'DEPARTAMENTO DE INGENIERÍA MECÁNICA. MAGÍSTER EN CIENCIAS DE INGENIERÍA MECÁNICA',
           'DEPARTAMENTO DE INGENIERÍA METALÚRGICA Y DE MATERIALES. INGENIERÍA CIVIL DE MINAS',
           'DEPARTAMENTO DE INGENIERÍA METALÚRGICA Y DE MATERIALES. INGENIERÍA CIVIL METALÚRGICA',
           'DEPARTAMENTO DE OBRAS CIVILES. CONSTRUCCIÓN CIVIL',
           'DEPARTAMENTO DE OBRAS CIVILES. INGENIERÍA CIVIL',
           'INGENIERÍA DE EJECUCIÓN EN GESTIÓN INDUSTRIAL',
           'INGENIERÍA DE EJECUCIÓN MECÁNICA DE PROCESOS Y MANTENIMIENTO INDUSTRIAL',
           'INGENIERÍA EN CONSTRUCCIÓN CON LICENCIATURA EN INGENIERÍA',
           'INGENIERÍA EN DISEÑO DE PRODUCTOS', 'INGENIERÍA EN MANTENIMIENTO INDUSTRIAL',
           'INGENIERÍA EN PREVENCIÓN DE RIESGOS LABORALES Y AMBIENTALES', 'INGENIERÍA MECÁNICA',
           'MAGÍSTER EN CIENCIAS DE LA INGENIERÍA ELÉCTRICA',
           'MAGÍSTER EN CIENCIAS, MENCIÓN FÍSICA',
           'Universidad Técnica Federico Santa María. Departamento de ConstrucciÑn y PrevenciÑn',
           'Universidad Técnica Federico Santa María. Departamento de Departamento de Mecánica',
           'Universidad Técnica Federico Santa María. Departamento de Diseño y Manufactura',
           'Universidad Técnica Federico Santa María. Departamento de Ingeniería Diseño y Manufactura',
           'Universidad Técnica Federico Santa María. Departamento de Ingeniería Mecánica',
           'Universidad Técnica Federico Santa María. Departamento de Ingeniería Metalúrgica y de Materiales',
           'Universidad Técnica Federico Santa María. Departamento de Mecánica',
           'Universidad Técnica Federico Santa María. Departamento de Obras Civiles']
boring += ['Ingeniería de Ejecución en Gestión de la Calidad',
           'Ingeniería en Construcción con Licenciatura en Ingeniería',
           'Ingeniería en Prevención de Riesgos Laborales y Ambientales',
           'INGENIERO EN FABRICACIÓN Y DISEñO INDUSTRIAL',
           'Técnico Universitario Dibujante Proyectista',
           'Técnico Universitario en Prevención de Riesgos',
           'TÉCNICO UNIVERSITARIO EN PROYECTO Y DISEñO MECÁNICO',
           'INGENIERÍA EN FABRICACIÓN Y DISEÑO INDUSTRIAL',
           'TÉCNICO UNIVERSITARIO EN PROYECTO Y DISEÑO MECÁNICO']

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []


recs = []

options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)


baseurl = 'https://repositorio.usm.cl'
collection = '0bfa339f-4083-42b9-b1e6-00116b895d1a'



for page in range(pages):
    tocurl = baseurl + '/collections/' + collection + '?cp.page=' + str(page+1) + '&cp.rpp=' + str(rpp)
    tocurl = baseurl + '/search?query=&spc.page=' + str(page+1) + '&spc.sf=dc.date.issued&spc.sd=DESC&spc.rpp=' + str(rpp)
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
    for rec in ejlmod3.ngrx(tocpage, baseurl, ['dc.contributor.advisor', 'dc.contributor.department',
                                               'dc.creator', 'dc.date.issued', 'dc.description.abstract',
                                               'dc.description.degree', 'dc.description.program',
                                               'dc.format.extent', 'dc.identifier.uri', 'dc.rights',
                                               'dc.subject', 'dc.title', 'dspace.entity.type'],
                            boring=boring, alreadyharvested=alreadyharvested):
        if 'autaff' in rec and rec['autaff']:
            rec['autaff'][-1].append(publisher)
        else:
            rec['autaff'] = [[ 'Dee, John' ]] 
        ejlmod3.printrecsummary(rec)
        #print(rec['thesis.metadata.keys'])
        recs.append(rec)
    print('  %i records so far' % (len(recs)))
    time.sleep(20)
ejlmod3.writenewXML(recs, publisher, jnlfilename)


