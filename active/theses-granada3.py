# -*- coding: utf-8 -*-
#harvest theses from Granada U.
#FS: 2019-11-26
#FS: 2023-04-29

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import unicodedata

publisher = 'U. Granada (main)'
jnlfilename = 'THESES-GRANADA-%s' % (ejlmod3.stampoftoday())

numberofpages = 5
recordsperpage = 100
skipalreadyharvested = True

boringdivisions = ['Psicologia', 'Ingenieria', 'Biologia', 'Educacion', 'Quimica', 'Medicina',
                   'Administrativo', 'Anatomia', 'Andalucia', 'Antigua', 'Arquitectonicas',
                   'Biotecnologia', 'Botanica', 'Bromatologia', 'Celular',
                   'clinica', 'Comercializacion', 'Comercio', 'Comportamiento', 'Construccion',
                   'Construcciones', 'Contabilidad', 'Criminologia', 'Democracia', 'Deportes',
                   'Deportiva', 'Dermatologia', 'Dibujo', 'Ecologia', 'Economica', 'Eduacion',
                   'Electronica', 'Embriologia', 'Empresa', 'Empresas', 'Enfermeria',
                   'Escolar]', 'Escolares', 'Escultura', 'Esenanza-Aprendizaje', 'Especialidades',
                   'Estadistica', 'Estomatologia', 'Estratigrafia', 'Estructuras', 'Evolutiva',
                   'Farmacologia', 'Filologias', 'Financiera', 'financiero', 'Fisioterapia',
                   'Genetica', 'Genomica', 'Geodinamica', 'Geografico', 'Ginecologia',
                   'Hidraulica', 'Histologia', 'Historiograficas', 'Humanidades', 'Inglesa',
                   'Inmunologia', 'Inteligencia', 'Internacionales', 'Interpretacion',
                   'Interuniversitario', 'Juridica', 'Legal', 'Linguistica', 'Mecanica',
                   'Medicna', 'Medieval', 'Mente', 'Mercados', 'Microbiologia', 'Migraciones',
                   'Mineralogia', 'Obstetricia', 'Oncologica', 'Operativa', 'Optica',
                   'Organizaciones', 'Otorrinolaringologia', 'Paleontologia', 'Parasitologia',
                   'Pedagogia', 'Pediatria', 'Penal', 'Petrologia', 'Pfizer', 'Pintura',
                   'Poeticas', 'Prehistoria', 'Preventiva', 'Proyectos', 'Publico',
                   'Radiologia', 'Recursos', 'Regional', 'Relaciones', 'Seguridad',
                   'Semiticos', 'Sistema', 'Sociologia', 'Tecnicas', 'Toxicologia', 'Trabajo',
                   'Traduccion', 'tributario', 'Vegetal', 'Zoologia', 'Historia', 'Agua',
                   'America', 'Antropologia', 'Aplicaciones', 
                   'Arqueologia', 'Arquitectonica', 'artes', 'Avances', 'Biogeoquimicos',
                   'Comunicacion', 'Educativa', 'Ensenanza-Aprendizaje', 'Eslava',
                   'Espanola', 'Evaluacion', 'Farmaceutica', 'Fisiologia', 'Flujos', 'Geografia',
                   'Grafica', 'Inorganica', 'Internacional', 'Lenguajes', 'Metodos', 'Musica',
                   'Ordenacion', 'Organica', 'Personalidad', 'Psicologico', 'Tratamiento',
                   'Urbanistica', 'Arquitectura', 'Conflictos', 'contextos', 'Corporal',
                   'Curriculum', 'Diagnostico', 'Economia', 'Espacio', 'Griega', 'Humana',
                   'Literatura', 'Musical', 'Organizacion', 'Plastica', 'Profesorado', 'Social',
                   'Territorio', 'Alimentos', 'Arte', 'Desarrollo', 'Lengua', 'Modelos',
                   'Bioquimica', 'Discursos', 'Expresion', 'Filologia', 'Filosofia', 'Genero',
                   'Migratorios', 'Practicas', 'Sociales', 'Contextos', 'Economicas',
                   'Educativas', 'Empresariales', 'Instituciones', 'Molecular', 'Mujeres',
                   'Nutricion', 'Textos', 'Tierra', 'Biomedicina', 'Derecho', 'Didactica',
                   'Juridicas', 'Sistemas', 'Artes', 'Civil', 'Clinica', 'Farmacia', 'Lenguas']

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []


###remove accents from a string
def akzenteabstreifen(string):
    if not type(string) == type('unicode'):
        string = str(string,'utf-8', errors='ignore')
        if not type(string) == type('unicode'):
            return string
        else:
            return str(unicodedata.normalize('NFKD',re.sub('ß', 'ss', string)).encode('ascii','ignore'),'utf-8')
    else:
        return str(unicodedata.normalize('NFKD',re.sub('ß', 'ss', string)).encode('ascii','ignore'),'utf-8')


prerecs = []
recs = []
for pn in range(numberofpages):
    tocurl = 'https://digibug.ugr.es/handle/10481/191/browse?rpp=' + str(recordsperpage) + '&sort_by=2&type=dateissued&offset=' + str(pn * recordsperpage) + '&etal=-1&order=DESC'
    ejlmod3.printprogress("=", [[pn+1, numberofpages], [tocurl]])
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
    prerecs += ejlmod3.getdspacerecs(tocpage,'https://digibug.ugr.es',  alreadyharvested=alreadyharvested)
    print('  %4i records so far' % (len(prerecs)))
    time.sleep(10)


i = 0
for rec in prerecs:
    i += 1
    keepit = True
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
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'citation_title', 'DC.identifier',
                                        'DCTERMS.issued', 'DC.subject', 'DCTERMS.abstract',
                                        'DC.language', 'citation_pdf_url', 'DC.rights'])
    rec['autaff'][-1].append(publisher)
    for meta in artpage.find_all('meta', attrs = {'name' : 'DC.contributor'}):
        if meta.has_attr('xml:lang'):
            rec['division'] = akzenteabstreifen(meta['content'])
            for bd in boringdivisions:
                if bd in rec['division']:
                    print('  skip "%s" because of "%s"' % (rec['division'], bd))
                    keepit = False
                    break
            rec['note'].append(rec['division'])
        else:
            rec['supervisor'].append([meta['content']])
    if keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['hdl'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
