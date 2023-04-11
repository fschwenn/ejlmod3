# -*- coding: utf-8 -*-
#harvest theses from Oviedo U.
#FS: 2021-09-14
#FS: 2023-04-07

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

rpp = 60
pages = 3
skipalreadyharvested = True

publisher = 'Oviedo U.'
jnlfilename = 'THESES-OVIEDO-%s' % (ejlmod3.stampoftoday())

boring = ['Biología Molecular y Celular, Departamento de',
          'Universidad de León, Departamento de Tecnología Minera, Topografía y Estructuras',
          'Ciencias de la Salud, Departamento de',
          'Administración de Empresas, Departamento de',
          'Biología de Organismos y Sistemas, Departamento de',
          'Biología Funcional, Departamento de',
          'Bioquímica y Biología Molecular, Departamento de',
          'Ciencia de los Materiales e Ingeniería Metalúrgica, Departamento de',
          'Ciencias de la Educación, Departamento de',
          'Ciencias Jurídicas Básicas, Departamento de',
          'Ciencia y Tecnología Náutica, Departamento de',
          'Cirugía y Especialidades Médico Quirúrgicas, Departamento de',
          'Construcción e Ingeniería de Fabricación, Departamento de',
          'Derecho Privado y de la Empresa, Departamento de',
          'Derecho Público, Departamento de',
          'Economía Aplicada, Departamento de',
          'Economía, Departamento de',
          'Economía y Empresa, Facultad de',
          'Energía, Departamento de',
          'Estadística e Investigación Operativa y Didáctica de la Matemática, Departamento de',
          'Explotación y Prospección de Minas, Departamento de',
          'Filología Anglogermánica y Francesa, Departamento de',
          'Filología Clásica y Románica, Departamento de',
          'Filología Española, Departamento de',
          'Filosofía, Departamento de',
          'Geografía, Departamento de',
          'Geología, Departamento de',
          'Historia del Arte y Musicología, Departamento de',
          'Historia, Departamento de',
          'Informática, Departamento de',
          'Ingeniería eléctrica, electrónica, de computadores y sistemas, Departamento de',
          'Ingeniería Eléctrica, Electrónica, de Computadores y Sistemas, Departamento de',
          'Ingeniería Química y Técnica del medio Ambiente, Departamento de',
          'Ingeniería Química y Tecnología del Medio Ambiente, Departamento de',
          'Medicina, Departamento de',
          'Morfología y Biología Celular, Departamento de',
          'Química Orgánica e Inorgánica, Departamento de',
          'Universidad de Oviedo. Facultad de Filosofía y Letras',
          'Psicología, Departamento de',
          'Contabilidad, Departamento de',
          'Economía Cuantitativa, Departamento de',
          'Instituto Universitario de Neurociencias del Principado de Asturias (INEUROPA)',
          'Instituto Universitario de Oncología, IUOPA',
          'Sociología, Departamento de']

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

prerecs = []
for page in range(pages):
    tocurl = 'https://digibuo.uniovi.es/dspace/handle/10651/5573/discover?rpp=' + str(rpp) + '&page=' + str(page+1) + '&sort_by=dc.date.issued_dt&order=desc'
    ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
    try:
        tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
        time.sleep(3)
    except:
        print("retry %s in 180 seconds" % (tocurl))
        time.sleep(180)
        tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
    prerecs += ejlmod3.getdspacerecs(tocpage, 'https://digibuo.uniovi.es', alreadyharvested=alreadyharvested)
    print('    %3i records so far' % (len(prerecs)))
        
i = 0
recs = []
for rec in prerecs:
    keepit = True
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(3)
    except:
        print("retry %s in 180 seconds" % (rec['link']))
        time.sleep(180)
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'DCTERMS.issued', 'DCTERMS.abstract',
                                        'DC.subject', 'citation_pdf_url','citation_date',
                                        'DCTERMS.extent', 'DC.rights', 'citation_language'])
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'DC.contributor'}):
        if meta.has_attr('xml:lang') or re.search(',.*,', meta['content']) or re.search('(Departamento|Instituto)', meta['content']):
            department = meta['content']
            if department in boring:
                keepit = False
            else:
                rec['note'].append(department)
        else:
            rec['supervisor'].append([meta['content']])
    if keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['hdl'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
