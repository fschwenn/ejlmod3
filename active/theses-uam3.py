# -*- coding: utf-8 -*-
#harvest theses from University of U. Autonoma, Madrid (main)
#FS: 2019-09-26
#FS: 2023-02-01

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

skipalreadyharvested = True
rpp = 50
pages = 5
boring = ['UAM. Departamento de Medicina', 'Hospital Universitario de La Princesa',
          'UAM. Departamento de Biología', 'Centro de Biología Molecular Severo Ochoa (CBM)',
          'Centro Nacional de Investigaciones Cardiovasculares Carlos III (CNIC)',
          'Centro Nacional de Investigaciones Oncológicas (CNIO)',
          'CSIC. Instituto de Catálisis y Petroleoquímica (ICP)',
          'Hospital General Universitario Gregorio Marañon',
          'Instituto de Investigación en Ciencias de la Alimentación (CIAL)',
          'Instituto de Investigaciones Biomédicas &quot;Alberto Sols&quot; (IIBM)',
          'UAM. Departamento de Biología Molecular', 'UAM. Departamento de Bioquímica',
          'UAM. Departamento de Ciencia Política y Relaciones Internacionales',
          'UAM. Departamento de Cirugía', 'UAM. Departamento de Estructura Económica y Economía del Desarrollo',
          'UAM. Departamento de Estudios Árabes e Islámicos y Estudios Orientales',
          'UAM. Departamento de Filología Española', 'UAM. Departamento de Filosofía',
          'UAM. Departamento de Geografía', 'UAM. Departamento de Historia Contemporánea',
          'UAM. Departamento de Música', 'UAM. Departamento de Pedagogía',
          'UAM. Departamento de Psicología Social y Metodología', 'UAM. Departamento de Psiquiatría',
          'UAM. Departamento de Química Física Aplicada', 'UAM. Departamento de Química Inorgánica',
          'UAM. Departamento de Química Orgánica', 'Centro de Investigación Biomédica en Red en Enfermedades Raras (CIBERER)'
          'Centro de Investigaciones Energéticas Medioambientales y Tecnológicas (CIEMAT)',
          'Instituto de Investigación del Hospital de La Princesa (IP)', 'UAM. Departamento de Filologías y su Didáctica',
          'Instituto de Investigaciones Biomédicas &quot;Alberto Sols&quot; (IIBM)',
          'Instituto de Investigación Hospital Universitario LA PAZ (IdiPAZ)',
          'Instituto de Investigación Sanitaria Fundación Jiménez Díaz (IIS-FJD)',
          'Instituto Fundación Teófilo Hernando para la I+D del medicamento',
          'UAM. Departamento de Antropología Social y Pensamiento Filosófico',
          'UAM. Departamento de Educación Física, Deporte y Motricidad Humana',
          'UAM. Departamento de Farmacología', 'UAM. Departamento de Fisiología',
          'UAM. Departamento de Historia Antigua, Historia Medieval, Paleografía y Diplomática',
          'UAM. Departamento de Obstetricia y Ginecología', 'UAM. Departamento de Pediatría',
          'UAM. Departamento de Química Analítica y Análisis Instrumental',
          'Hospital Universitario 12 de Octubre', 'UAM. Departamento de Anatomía, Histología y Neurociencia',
          'Instituto Madrileño de Estudios Avanzados en Materiales (IMDEA-Materiales)',
          'Instituto Madrileño de Investigación y Desarrollo Rural, Agrario y Alimentario (IMIDRA)',
          'UAM. Departamento de Derecho Privado, Social y Económico', 'UAM. Departamento de Derecho Público y Filosofía Jurídica',
          'UAM. Departamento de Didácticas Específicas', 'UAM. Departamento de Ecología', 'UAM. Departamento de Economía Aplicada',
          'UAM. Departamento de Filología Francesa', 'UAM. Departamento de Filología Inglesa',
          'UAM. Departamento de Lingüística, Lenguas Modernas, Lógica y Fª de la Ciencia y Tª de la Literatura y Literatura Comparada',
          'UAM. Departamento de Medicina Preventiva y Salud Pública y Microbiología',
          'UAM. Departamento de Prehistoria y Arqueología', 'UAM. Departamento de Psicología Básica',
          'UAM. Departamento de Psicología Biológica y de la Salud', 'UAM. Departamento de Psicología Evolutiva y de la Educación',
          'UAM. Departamento de Química', 'UAM. Departamento de Tecnología Electrónica y de las Comunicaciones',
          'Hospital Universitario Marqués de Valdecilla-IDIVAL (Santander)', 'Hospital Virgen de la Salud (Toledo)',
          'Instituto de Ciencias Ambientales de la Orinoquia Colombiana (ICAOC, Colombia)',
          'Instituto Madrileño de Estudios Avanzados en Alimentación (IMDEA-Alimentación)',
          'Instituto Madrileño de Estudios Avanzados en Nanociencia (IMDEA-Nanociencia)',
          'Instituto Nacional de Técnica Aeroespacial (INTA)', 'UAM. Centro de Microanálisis de Materiales (CMAM)',
          'UAM. Departamento de Análisis Económico: Economía Cuantitativa',
          'UAM. Departamento de Análisis Económico, Teoría Económica e Historia Económica',
          'UAM. Departamento de Anatomía Patológica', 'UAM. Departamento de Contabilidad',
          'UAM. Departamento de Didáctica y Teoría de la Educación',
          'UAM. Departamento de Economía y Hacienda Pública', 'UAM. Departamento de Educación Artística, Plástica y Visual',
          'UAM. Departamento de Enfermería', 'UAM. Departamento de Filología Clásica',
          'UAM. Departamento de Filologías y su Didáctica', 'UAM. Departamento de Financiación e Investigación Comercial',
          'UAM. Departamento de Geología y Geoquímica', 'UAM. Departamento de Historia Moderna',
          'UAM. Departamento de Historia y Teoría del Arte', 'UAM. Departamento de Ingeniería Informática',
          'UAM. Departamento de Ingeniería Química', 'UAM. Departamento de Organización de Empresas',
          'UAM. Departamento de Química Agrícola', 'UAM. Instituto Universitario de Estudios de la M',
          'UAM. Departamento de Antropología Social y Pensamiento Filosófico Español',
          'UAM. Departamento de Sociología', 'CSIC. Centro de Astrobiología (CAB)',
          'CSIC. Centro Nacional de Biotecnología (CNB)']

deptofc = {'UAM. Departamento de Física de la Materia Condensada' : 'f',
           'UAM. Departamento de Física Teórica de la Materia Condensada' : 'f',
           'Instituto de Ciencias Matemáticas (ICMAT)' : 'm',
           'UAM. Departamento de Matemáticas' : 'm'}
publisher = 'U. Autonoma, Madrid (main)'

jnlfilename = 'THESES-UAM-%s' % (ejlmod3.stampoftoday())

hdr = {'User-Agent' : 'Magic Browser'}

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
prerecs = []
for page in range(pages):
    tocurl = 'https://repositorio.uam.es/handle/10486/700636/discover?rpp=' + str(rpp) + '&etal=0&group_by=none&page=' + str(page+1) + '&sort_by=dc.date.issued_dt&order=desc&filtertype_0=type&filter_relational_operator_0=equals&filter_0=doctoralThesis'
    ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    for rec in ejlmod3.getdspacerecs(tocpage, 'https://repositorio.uam.es'):
        if skipalreadyharvested and rec['hdl'] in alreadyharvested:
            pass
        else:
            prerecs.append(rec)
    print('  %4i records so far' % (len(prerecs)))

recs = []
for (i, rec) in enumerate(prerecs):
    keepit = True
    ejlmod3.printprogress("-", [[i+1, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']+'?show=full'), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']+'?show=full'), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'DC.title', 'DCTERMS.issued',
                                        'DCTERMS.abstract', 'citation_pdf_url',
                                        'DCTERMS.extent', 'DC.language'])
    for tr in artpage.find_all('tr'):
        tdlabel = ''
        for td in tr.find_all('td', attrs = {'class' : 'label-cell'}):
            tdlabel = td.text.strip()
        for td in tr.find_all('td', attrs = {'class' : 'word-break'}):
            #supervisor
            if tdlabel == 'dc.contributor.advisor':
                rec['supervisor'].append([td.text.strip()])
            #department
            elif tdlabel == 'dc.contributor.other':
                dep = td.text.strip()
                if dep in boring:
                    keepit = False
                else:
                    if dep in list(deptofc.keys()):
                        rec['fc'] = deptofc[dep]
                    else:
                        rec['note'].append(dep)
            #keywords
            elif tdlabel == 'dc.subject.other':
                rec['keyw'].append(td.text.strip())        
    rec['autaff'][-1].append('U. Autonoma, Madrid (main)')
    ejlmod3.globallicensesearch(rec, artpage)
    if keepit:
        recs.append(rec)
        ejlmod3.printrecsummary(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['hdl'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
