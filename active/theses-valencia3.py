# -*- coding: utf-8 -*-
#harvest theses from Valencia U.
#FS: 2019-11-26
#FS: 2023-04-08

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'U. Valencia (main)'
jnlfilename = 'THESES-VALENCIA-%s' % (ejlmod3.stampoftoday())

numberofpages = 3
recordsperpage = 100
skipalreadyharvested = True

boring = ["Departament de Genètica", "Departament de Bioquímica i Biologia Molecular",
          "Departament de Teoria dels Llenguatges i Ciències de la Comunicació",
          "Departament d'Economia Aplicada",  "Departament d'Educació Física i Esportiva", 
          "Departament d'Educació Comparada i Història de l'Educació",
          "Departament de Biologia Cel.lular i Parasitologia",
          "Departament de Cirurgia", "Departament de Comptabilitat", 
          "Departament de Didàctica de les Ciències Experimentals i Socials",
          "Departament de Direcció d'Empreses. Juan Jose Renau Piqueras",
          "Departament de Dret Civil", "Departament de Microbiologia i Ecologia",
          "Departament de Dret Constitucional, Ciència Política i de l'Administració",
          "Departament de Dret del Treball i de la Seguretat Social",
          "Departament de Filologia Anglesa i Alemanya", "Departament de Filologia Espanyola",
          "Departament de Fisioteràpia", "Departament de Història de l'Art",
          "Departament de Lògica i Filosofia de la Ciència",          
          "Departament de Personalitat, Avaluació i Tract. Psicologics",
          "Departament de Psicobiologia", "Departament de Química Analítica",
          "Facultat de Dret", "﻿Institut de Ciència Molecular", "Institut de Drets Humans",
          "Departament d'Anàlisi Econòmica", "Departament d'Anatomia i Embriologia Humana",
          "Departament d'Estomatologia", "Departament de Biologia Vegetal",
          "Departament de Biologia Funcional i Antropologia Física",          
          "Departament de Comercialització i Investigació de Mercats",
          "Departament de Dret Administratiu i Processal",
          "Departament de Dret Financer i Història del Dret",
          "Departament de Filologia Catalana", "Departament de Filologia Francesa i Italiana",
          "Departament de Filosofia", "Departament de Medicina",
          "Departament de Medicina Preventiva i Salut Pública, Ciències de l'Alimentació, Toxicologia i Medicina Legal",          
          "Departament de Mètodes D'investigació i Diagnòstic en Educació",
          "Departament de Patologia", "Departament de Psicologia Bàsica",
          "Departament de Pediatria, Obstetrícia i Ginecologia",          
          "Departament de Psicologia Evolutiva i de l'Educació",
          "Departament de Química Física", "Departament de Quimica Orgànica",
          "Departament de Sociologia i Antropologia Social",
          "Departament de Teoria de l'Educació", "Departament de Història Moderna",
          "Departament de Treball Social i Serveis Socials",
          "Facultat d'Infermeria i Podologia", "Facultat de Ciències Biològiques",
          "Facultat de Filologia, Traducció i Comunicació",
          "Facultat de Medicina i Odontologia", "Departament d'Enginyeria Química",
          "Institut Interuniversitari de Desenvolupament Local",          
          "Departament de Didàctica de la Llengua i la Literatura",
          "Departament de Didàctica de l'Expressió Musical, Plàstica i Corporal",
          "Departament de Didàctica i Organització Escolar",
          'Departament de Dret Internacional "Adolfo Miaja de la Muela"',
          "Departament de Dret Romà i Eclesiàstic de l'Estat",
          "Departament de Farmàcia i Tecnologia Farmacèutica",
          "Departament de Farmacologia", "Departament de Filologia Clàssica",
          "Departament de Filosofia del Dret Moral i Politic",
          "Departament de Fisiologia", "Departament de Geologia",
          "Departament de Història de la Ciència i Documentació",          
          "Departament de Prehistòria i Arqueologia",
          "Departament de Psicologia Social", "Departament de Química Inorgànica",
          "Facultat de Ciències Socials", "Facultat de Filosofia i CC Educació",
          "Facultat de Química", "Institut de Trànsit i Seguretat Viària",
          "Institut Universitari d'Estudis de la Dona",
          "Centre de investigaciones sobre desertificación (CIDE) CSIC-UV-GV",
          "Departament d'Economia Financera i Actuarial",
          "Departament d'Estadística i Investigació Operativa",
          "Departament d'Infermeria", "Departament de Botànica",
          "Departament de Didàctica de les Matematiques",
          'Departament de Dret Internacional "Adolfo Miaja de la Muela"',
          'Departament de Dret Mercantil "Manuel Broseta Pont"',
          "Departament de Dret Penal", "Departament de Geografia",
          "Departament de Geometria i Topologia",
          "Departament de Història Contemporània",
          "Departament de Història de l'Antiguitat i la Cultura Escrita",
          "Departament de Història Medieval",
          "Departament de Metodologia de les Ciències del Comportament",
          "Departament de Zoología", "Facultat de Farmàcia",
          "Facultat de Fisioteràpia", "Facultat de Geografia i Història",
          "Facultat de Magisteri",
          "Facultat de Psicologia. Programes interdepartamentals",
          "Institut d’Investigació en Psicologia dels Recursos Humans",
          "Institut Interuniversitari d'Economia Internacional",
          "Institut Interuniversitari López Piñero",
          "Institut Universitari d'Economia Social i Cooperativa",
          "Màster en Història i Identitats Hispàniques en el Mediterrani Occidental (segles XV-XIX)",
          "Màster en Sociologia i Antropologia de les Polítiques Públiques"]

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

prerecs = []
recs = []
for pn in range(numberofpages):
    tocurl = 'https://roderic.uv.es/browse?order=DESC&rpp=' + str(recordsperpage) + '&sort_by=4&value=info%3Aeu-repo%2Fsemantics%2FdoctoralThesis&etal=-1&offset=' + str(pn * recordsperpage) + '&type=type'
    ejlmod3.printprogress("=", [[pn+1, numberofpages], [tocurl]])
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
    prerecs += ejlmod3.getdspacerecs(tocpage, 'http://roderic.uv.es', alreadyharvested=alreadyharvested)
    time.sleep(10)
    print('  %5i records so far' % (len(prerecs)))

i = 0
for rec in prerecs:
    keepit = True
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(5)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    for span in artpage.find_all('span', attrs = {'class' : 'bold'}):
        spant = span.text.strip()
        if re.search('document', spant):
            arttype = re.sub('.* is a *(.*)Date.*', r'\1', spant)
            arttype = re.sub('.* un.a *(.*),.*', r'\1', arttype)
            rec['arttype'] = arttype
    if not rec['arttype'] in ['tesis', 'tesi']:
        print('skip articletype:', str(unicodedata.normalize('NFKD',re.sub('ß', 'ss', arttype)).encode('ascii','ignore'),'utf-8'))
        continue
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'citation_title', 'DCTERMS.issued',
                                        'DC.language', 'citation_pdf_url', 'DCTERMS.abstract',
                                        'DC.description', 'DC.rights', 'DCTERMS.extent'])
    rec['autaff'][-1].append(publisher)
    #supervisor/department
    for meta in artpage.find_all('meta', attrs = {'name' :'DC.contributor'}):
        if meta.has_attr('xml:lang'):
            dep = meta['content']
            if dep in boring:
                keepit = False
            elif dep in ["Departament d'Anàlisi Matemàtica", "Departament d'Algebra", "Departament de Matemàtiques"]:
                rec['fc'] = 'm'
            elif dep in ["Departament d'Informàtica"]:
                rec['fc'] = 'c'
            else:
                rec['note'].append('DEP:::' + dep)
        else:
            rec['supervisor'].append([meta['content']])
    if keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['hdl'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
