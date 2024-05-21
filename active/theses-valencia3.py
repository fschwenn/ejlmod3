# -*- coding: utf-8 -*-
#harvest theses from Valencia U.
#FS: 2019-11-26
#FS: 2023-04-08
#FS: 2024-01-02

import sys
import os
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import undetected_chromedriver as uc

publisher = 'U. Valencia (main)'
jnlfilename = 'THESES-VALENCIA-%s' % (ejlmod3.stampoftoday())

numberofpages = 666
years= 2
rpp = 60
skipalreadyharvested = True
boring = ['Departament d&s;Anatomia i Embriologia Humana', 'Departament d&s;Estomatologia',
          'Departament de Bioquímica i Biologia Molecular', 'Departament de Cirurgia',
          'Departament de Direcció d&s;Empreses. Juan Jose Renau Piqueras',
          'Departament de Dret Internacional &quot;Adolfo Miaja de la Muela&quot;',
          'Departament de Dret Penal', 'Departament de Farmacologia', 'Departament de Filologia Catalana',
          'Departament de Fisiologia', 'Departament de Fisioteràpia', 'Departament de Genètica',
          'Departament de Patologia', 'Departament de Pediatria, Obstetrícia i Ginecologia',
          'Departament de Prehistòria i Arqueologia', 'Departament de Química Inorgànica',
          'Facultat de Ciències Socials', 'Facultat de Geografia i Història',
          'Facultat de Medicina i Odontologia', 'Institut d’Investigació en Psicologia dels Recursos Humans',
          'Institut Interuniversitari López Piñero', 'Departament de Dret Civil',
          'Centre de investigaciones sobre desertificación (CIDE) CSIC-UV-GV',
          'Departament d&s;Anàlisi Econòmica', 'Departament d&s;Economia Aplicada',
          'Departament d&s;Economia Financera i Actuarial',
          'Departament d&s;Educació Comparada i Història de l&s;Educació',
          'Departament d&s;Educació Física i Esportiva', 'Departament d&s;Enginyeria Química',
          'Departament d&s;Estadística i Investigació Operativa', 'Departament d&s;Infermeria',
          'Departament de Biologia Cel.lular i Parasitologia',
          'Departament de Comercialització i Investigació de Mercats', 'Departament de Comptabilitat',
          'Departament de Didàctica de la Llengua i la Literatura',
          'Departament de Didàctica de l&s;Expressió Musical, Plàstica i Corporal',
          'Departament de Didàctica i Organització Escolar', 'Departament de Dret Administratiu i Processal',          
          'Departament de Dret Constitucional, Ciència Política i de l&s;Administració',
          'Departament de Dret del Treball i de la Seguretat Social',
          'Departament de Dret Financer i Història del Dret',
          'Departament de Dret Internacional &quot;Adolfo Miaja de la Muela&quot;',
          'Departament de Dret Mercantil &quot;Manuel Broseta Pont&quot;',
          'Departament de Dret Mercantil "Manuel Broseta Pont"',
          'Departament de Dret Romà i Eclesiàstic de l&s;Estat',
          'Departament de Farmàcia i Tecnologia Farmacèutica', 'Departament de Filologia Anglesa i Alemanya',
          'Departament de Filologia Espanyola', 'Departament de Filologia Francesa i Italiana',
          'Departament de Filosofia', 'Departament de Geografia', 'Departament de Història Contemporània',
          'Departament de Història de la Ciència i Documentació',
          'Departament de Història de l&s;Antiguitat i la Cultura Escrita',
          'Departament de Història de l&s;Art', 'Departament de Història Medieval',
          'Departament de Medicina Preventiva i Salut Pública, Ciències de l&s;Alimentació, Toxicologia i Medicina Legal',
          'Departament de Medicina', 'Departament de Mètodes D&s;investigació i Diagnòstic en Educació',
          'Departament de Metodologia de les Ciències del Comportament',
          'Departament de Microbiologia i Ecologia', 'Departament de Teoria de l&s;Educació',
          'Departament de Personalitat, Avaluació i Tract. Psicologics', 'Departament de Psicobiologia',
          'Departament de Psicologia Bàsica', 'Departament de Psicologia Evolutiva i de l&s;Educació',
          'Departament de Psicologia Social', 'Departament de Química Analítica',
          'Departament de Quimica Orgànica', 'Departament de Sociologia i Antropologia Social',         
          'Departament de Teoria dels Llenguatges i Ciències de la Comunicació', 'Departament de Zoología',
          'Facultat d&s;Infermeria i Podologia', 'Facultat de Ciències Biològiques', 'Facultat de Dret',
          'Facultat de Farmàcia', 'Facultat de Filosofia i CC Educació', 'Facultat de Fisioteràpia',
          'Facultat de Magisteri', 'Facultat de Psicologia. Programes interdepartamentals',
          'Facultat de Química', 'Institut de Drets Humans', 'Institut Interuniversitari d&s;Economia Internacional',
          'Institut Interuniversitari de Desenvolupament Local',
          'Institut Universitari d&s;Economia Social i Cooperativa',
          'Institut Universitari d&s;Estudis de la Dona',
          'Institut Universitari d&s;Investigació de Polítiques de Benestar Social (Polibenestar)',
          'Màster en Investigació en Didàctiques Específiques',
          'Màster en Investigació i ús Racional del Medicament']

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

baseurl = 'https://roderic.uv.es'
recs = []
#for (dep, fc) in deps:
for page in range(numberofpages):
    tocurl = 'https://roderic.uv.es/search?f.itemtype=doctoral%20thesis,equals&spc.page=' + str(page+1) + '&f.dateIssued.min=' + str(ejlmod3.year(backwards=years)+1) + '&spc.rpp=' + str(rpp) + '&spc.sd=DESC'
    ejlmod3.printprogress("=", [[page+1, numberofpages], [tocurl]])
    try:
        driver.get(tocurl)
        time.sleep(5)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
        prerecs = ejlmod3.ngrx(tocpage, baseurl, ['dc.contributor.author', 'dc.date.issued',
                                                  'dc.description.abstract', 'dc.identifier.doi',
                                                  'dc.identifier.uri', 'dc.language.iso',
                                                  'dc.rights.accessRights', 'dc.subject',
                                                  'dc.title', 'dc.type','dc.contributor.advisor',
                                                  'dc.contributor.other', 
                                                  'dc.format.extent'], boring=boring, alreadyharvested=alreadyharvested)
        prerecs[0]
    except:
        time.sleep(60)
        driver.get(tocurl)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
        prerecs = ejlmod3.ngrx(tocpage, baseurl, ['dc.contributor.author', 'dc.date.issued',
                                                  'dc.description.abstract', 'dc.identifier.doi',
                                                  'dc.identifier.uri', 'dc.language.iso',
                                                  'dc.rights.accessRights', 'dc.subject',
                                                  'dc.title', 'dc.type', 'dc.contributor.advisor',
                                                  'dc.contributor.other', 
                                                  'dc.format.extent'], boring=boring, alreadyharvested=alreadyharvested)
    for div in tocpage.find_all('div', attrs = {'class' : 'pagination-info'}):
        for span in div.find_all('span', attrs = {'class' : 'align-middle'}):
            spant = span.text.strip()
            if re.search(' of \d', spant):
                numoftheses = int(re.sub('.* of (\d+).*', r'\1', spant))
                numberofpages = (numoftheses - 1) // rpp + 1
    for rec in prerecs:
        rec['autaff'][-1].append(publisher)
        ejlmod3.printrecsummary(rec)
        #print(rec['thesis.metadata.keys'])
        recs.append(rec)
    print('  %i records so far' % (len(recs)))
    time.sleep(20)
    if page >= numberofpages:
        break
ejlmod3.writenewXML(recs, publisher, jnlfilename)
