# -*- coding: utf-8 -*-
#harvest theses from Basque U., Bilbao
#FS: 2023-06-27

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import datetime
import time
import json

jnlfilename = 'THESES-BILBAO-%s' % (ejlmod3.stampoftoday())

publisher = 'Basque U., Bilbao'

hdr = {'User-Agent' : 'Magic Browser'}

rpp = 50
pages = 2
skipalreadyharvested = True
boring = ['Farmacia y ciencias de los alimentos', 'Química aplicada',
          'Biología vegetal y ecología', 'Farmacología', 'Física', 'Geología',
          'Ingeniería química y del medio ambiente', 'Química analítica',
          'Química física', 'Química Orgánica e Inorgánica', 'Química orgánica I',
          'Lengua Vasca y Comunicación', 'Lenguajes y sistemas informáticos',
          'Lingüística y estudios vascos', 'Máquinas y motores térmicos', 'Medicina',
          'Medicina preventiva y salud pública', 'Métodos Cuantitativos',
          'Métodos de investigación y diagnostico en educación',
          'Mineralogía y petrología', 'Neurociencias', 'Organización de empresas',
          'Pediatría', 'Periodismo', 'Periodismo II',
          'Personalidad, evaluación y tratamiento psicológico', 'Pintura',
          'Polímeros y Materiales Avanzados: Física, Química y Tecnología',
          'Políticas Públicas e Historia Económica',
          'Procesos psicológicos básicos y su desarrollo',
          'Psicología Clínica y de la Salud y Metodología de Investigación',
          'Psicología evolutiva y de la educación', 'Psicología Social',
          'Psicología Social y Metodología de las Ciencias del Comportamiento',
          'Química analítica', 'Química aplicada', 'Química física',
          'Química inorgánica', 'Química Orgánica e Inorgánica',
          'Química orgánica I', 'Química orgánica II', 'Sociología II',
          'Sociología y trabajo social', 'Tecnología electrónica',
          'Teoría e historia de la educación', 'Zoología y biología celular animal',
          'Análisis Económico', 'Arquitectura',
          'Arquitectura y Tecnología de Computadores', 'Arte y Tecnología',
          'Arte y tecnología', 'Biblioteca', 'Biología celular e histología',
          'Biología celular y ciencias morfológicas', 'Biología vegetal y ecología',
          'Bioquímica y biología molecular', 'Derecho publico',
          'Ciencia de la computación e inteligencia artificial',
          'Ciencia política y de la administración',
          'Ciencia y tecnología de polímeros', 'Ciencias de la Educación',
          'Ciencias y Técnicas de la Navegación, Máquinas y Construcciones Navales',
          'Cirugía, radiología y medicina física', 'Derecho civil',
          'Comunicación audiovisual y publicidad',
          'Derecho Administrativo, Constitucional y Filosofía del Derecho',
          'Derecho Constitucional e Historia del Pensamiento y de los Movimientos Sociales y Políticos',
          'Derecho de la empresa', 'Derecho de la Empresa y Derecho Civil',
          'Derecho eclesiástico del estado y derecho romano',
          'Derecho Internacional Público, Relaciones Internacionales e Historia del Derecho',  
          'Derecho Público y Ciencias Histórico-Jurídicas y del Pensamiento Político',
          'Dermatología, oftalmología y otorrinolaringología', 'Dibujo',
          'Didáctica de la Expresión Musical, Plástica y Corporal',
          'Didáctica de la Lengua y la Literatura',
          'Didáctica de la Matemática y de las Ciencias Experimentales',
          'Didáctica de las Ciencias Sociales',
          'Didáctica de las Matemáticas, Ciencias Experimentales y Sociales',
          'Didáctica y organización escolar', 'Economía aplicada I',
          'Economía aplicada II (Hacienda Pública y Derecho Fiscal)',
          'Economía aplicada III (Econometría y Estadística)', 'Economía aplicada IV',
          'Economía aplicada V', 'Economía financiera I', 'Economía financiera II',
          'Economía industrial', 'Educación física y deportiva', 'Enfermería',
          'Enfermería I', 'Enfermería II', 'Escultura',
          'Escultura y Arte y Tecnología', 'Especialidades médico-quirúrgicas',
          'Estomatologia I', 'Estomatología I', 'Estomatología II',
          'Estratigrafía y paleontología', 'Estudios clásicos',
          'Evaluación de la gestión e innovación empresarial',
          'Expresión grafica y proyectos de ingeniería',
          'Expresión gráfica y proyectos de ingeniería',
          'Farmacia y ciencias de los alimentos', 'Farmacología', 'Farmalogía',
          'Filología e Historia', 'Filología francesa',
          'Filología hispánica, románica y Teoría de la literatura',
          'Filología Inglesa y Alemana y Traducción e Interpretación', 'Filosofía',
          'Filosofía de los valores y antropología social', 'Fisiología',
          'Fundamentos del análisis económico I',
          'Fundamentos del análisis económico II',
          'Genética, antropología física y fisiología animal', 'Geodinámica',
          'Geografía, prehistoria y arqueología', 'Geología',
          'Grupo de investigación IMaCris / MaKrisI', 'HEGOA',
          'Historia contemporánea', 'Historia del arte y música',
          'Historia e instituciones económicas',
          'Historia medieval, moderna y de América', 'Ingenieria de Comunicaciones',
          'Ingeniería de comunicaciones', 'Ingeniería de sistemas y automática',
          'Ingeniería eléctrica', 'Ingeniería Energética', 'Ingeniería mecánica',
          'Ingeniería Minera y Metalúrgica y Ciencia de los Materiales',
          'Ingeniería nuclear y mecánica de fluidos', 'Ingeniería química',
          'Ingeniería química y del medio ambiente',
          'Inmunología, Microbiología y Parasitología',
          'Inmunología, microbiología y parasitología']

hdls = []
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

prerecs = []
for page in range(pages):
    tocurl = 'https://addi.ehu.es/handle/10810/12145/browse?sort_by=2&order=DESC&offset=' + str(page*rpp) + '&rpp=' + str(rpp)
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    prerecs += ejlmod3.getdspacerecs(tocpage, 'https://addi.ehu.es', alreadyharvested=alreadyharvested)
    print('   %4i records so far' % (len(prerecs)))
    time.sleep(4)

i = 0
recs = []
for rec in prerecs:
    keepit = True
    i += 1
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['link']], [len(recs)]]) 
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']+'?show=full'), features="lxml")
        time.sleep(4)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']+'?show=full'), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'citation_title', 'DCTERMS.issued', 'DCTERMS.abstract',
                                        'citation_pdf_url', 'DC.language', 'citation_doi', 'DC.rights',
                                        'DC.subject'])
    for tr in artpage.find_all('tr'):
        tdlabel = ''
        for td in tr.find_all('td', attrs = {'class' : 'label-cell'}):
            tdlabel = td.text.strip()
        for td in tr.find_all('td', attrs = {'class' : 'word-break'}):
            #supervisor
            if tdlabel == 'dc.contributor.advisor':
                rec['supervisor'].append([td.text.strip()])
                for a in td.find_all('a'):
                    if a.has_attr('href') and re.search('orcid.org', a['href']):
                        rec['supervisor'][-1].append(re.sub('.*orcid.org\/', 'ORCID:', a['href']))
            #author
            elif tdlabel == 'dc.contributor.author':
                rec['autaff'] == [[td.text.strip()]]
                for a in td.find_all('a'):
                    if a.has_attr('href') and re.search('orcid.org', a['href']):
                        rec['autaff'][-1].append(re.sub('.*orcid.org\/', 'ORCID:', a['href']))
            #pages
            elif tdlabel == 'dc.description':
                if re.search('\d\d+ *p\.', td.text):
                    rec['pages'] = re.sub('.*?(\d\d+) *p.*', r'\1', td.text.strip())
            #department
            elif tdlabel == 'dc.departamentoes':
                dep = td.text.strip()
                if dep in boring:
                    keepit = False
                elif dep == 'Física de la materia condensada':
                    rec['fc'] = 'f'
                elif dep in ['Matemática aplicada',
                             'Matemática Aplicada, Estadística e Investigación Operativa',
                             'Matemáticas']:
                    rec['fc'] = 'm'
                else:
                    rec['note'].append('DEP:::' + dep)
    #author's affiliation
    rec['autaff'][-1].append(publisher)    
    if keepit:
        recs.append(rec)
        ejlmod3.printrecsummary(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['hdl'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
