# -*- coding: utf-8 -*-
#harvest theses from U. Zaragoza
#JH: 2022-05-01
#FS: 2023-03-16

from time import sleep
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from base64 import b16encode
import ejlmod3
import os
import re

publisher = 'U. Zaragoza (main)'
rpp = 50
pages = 2
skipalreadyharvested = True
boring = ['Medicina y especialidades médicas', 'Programa de Doctorado en Producción Animal',
          'Programa de Doctorado en Historia del Arte',
          'Programa de Doctorado en Bioquímica y Biología Molecular',
          'Programa de Doctorado en Ciencia Analítica en Química',
          'Programa de Doctorado en Ciencias Agrarias y del Medio Natural',
          'Programa de Doctorado en Ciencias Biomédicas y Biotecnológicas',
          'Programa de Doctorado en Ciencias de la Antigüedad',
          'Programa de Doctorado en Ciencias de la Salud y del Deporte',
          'Lingüística aplicada a la traducción e interpretación',
          'Programa de Doctorado en Contabilidad y Finanzas',
          'Programa de Doctorado en Derechos Humanos y Libertades Fundamentales',
          'Programa de Doctorado en Derecho', 'Programa de Doctorado en Economía',
          'Programa de Doctorado en Economía y Gestión de las Organizaciones',
          'Programa de Doctorado en Educación', 'Programa de Doctorado en Geología',
          'Programa de Doctorado en Energías Renovables y Eficiencia Energética',          
          'Programa de Doctorado en Historia, Sociedad y Cultura: Épocas Medieval y Moderna',
          'Programa de Doctorado en Ingeniería Biomédica',
          'Teoría de la literatura y literatura comparada',
          'Programa de Doctorado en Ingeniería de Sistemas e Informática',
          'Programa de Doctorado en Ingeniería Electrónica', 'Programa de Doctorado en Ingeniería Mecánica',
          'Programa de Doctorado en Ingeniería Química y del Medio Ambiente',
          'Programa de Doctorado en Lingüística Hispánica',
          'Programa de Doctorado en Logística y Gestión de la Cadena de Suministro',
          'Programa de Doctorado en Mecánica de Fluidos', 'Programa de Doctorado en Medicina',
          'Programa de Doctorado en Medicina y Sanidad Animal',
          'Programa de Doctorado en Nuevos Territorios en la Arquitectura',
          'Programa de Doctorado en Ordenación del Territorio y Medio Ambiente',
          'Programa de Doctorado en Patrimonio, Sociedades y Espacios de Frontera',
          'Programa de Doctorado en Química Inorgánica', 'Programa de Doctorado en Química Orgánica',
          'Programa de Doctorado en Sociología de las Políticas Públicas y Sociales',
          'Programa de Doctorado en Calidad, Seguridad y Tecnología de los Alimentos',
          'Programa de Doctorado en Energías renovables y Eficiencia energética',
          'Programa de Doctorado en Estudios Ingleses', 'Programa de Doctorado en Filosofía',
          'Programa de Doctorado en Historia Contemporánea',
          'Programa de Doctorado en Ingeniería de Diseño y Fabricación',
          'Programa de Doctorado en Ingeniería Química y del Medio ambiente',
          'Programa de Doctorado en Literaturas Hispánicas',
          'Programa de Doctorado en Nuevos territorios en Arquitectura',
          'Programa de Doctorado en Relaciones de Género y Estudios Feministas',
          'Programa de Doctorado en Tecnologías de la Información y Comunicaciones en Redes Móviles',
          'Ciencias de la Documentación e Historia de la Ciencia',
          'Filología Inglesa y Alemana', 'Filosofía', 'Fisiatría y Enfermería',
          'Historia', 'Ingeniería de Diseño y Fabricación',
          'Ingeniería Electrónica y Comunicaciones', 'Ingeniería Mecánica',
          'Ingeniería Química y Tecnologías del Medio Ambiente',
          'Producción Animal y Ciencia de los Alimentos',
          'Unidad Predepartamental de Arquitectura', 'Historia contemporánea',
          'Bioquímica y Biología Molecular y Celular', 'Anatomía patológica',
          'Cirugía, Ginecología y Obstetricia', 'Anatomía',
          'Filología Española', 'Cirugía', 'Derecho constitucional',
          'Historia Medieval, Ciencias y Técnicas Historiográficas y Estudios Árabes e Islámicos',
          'Historia Moderna y Contemporánea', 'Economía financiera y contabilidad',
          'Instituto de Ciencia de Materiales de Aragón (ICMA)', 'Farmacología',
          'Medicina, Psiquiatría y Dermatología', 'Obstetricia y ginecología',
          'Psicología y Sociología', 'Análisis geográfico regional', 'Arqueología',
          'Arquitectura y tecn. Computadoras', 'Bioquímica y biología molecular', 'Cerámicas',
          'Comercialización e Invest. Mercados', 'Derecho internacional público',
          'Didáctica de la expresión corporal', 'Didáctica de las ciencias experimentales',
          'Didáctica de las ciencias sociales', 'Economía aplicada',
          'Epidemiología y Salud Pública', 'Estratigrafía', 'Filología latina', 'Filosofía del derecho',
          'Geodinámica externa', 'Geografía humana', 'Geometría y topología',
          'Historia e instituciones económicas',
          'Historia moderna', 'Ingeniería de sistemas y automática',
          'Lenguajes y sistemas informáticos', 'Métodos de invest. Y diagnóstico en educación',
          'Microbiología', 'Microbiología y parasitología',
          'Organización de empresas', 'Paleontología', 'Pediatría', 'Petrología y Geoquímica',
          'Pintura', 'Prehistoria', 'Prospectiva e investigación minera',
          'Química analítica', 'Química Analítica', 'Química orgánica', 'Radiología y medicina física',
          'Servicios de Salud', 'Sociología', 'Tecnología electrónica', 'Zoología',
          'Ciencias de la Antigüedad', 'Ciencias de la Educación',
          'Derecho Penal, Filosofía del Derecho e Historia del Derecho',
          'Didáctica de las Ciencias Experimentales',
          'Didáctica de las Lenguas y de las Ciencias Humanas y Sociales',
          'Dirección de Márketing e Investigación de Mercados', 'Dirección y Organización de Empresas',
          'Estructura e Historia Económica y Economía Pública', 'Expresión Musical, Plástica y Corporal',
          'Geografía y Ordenación del Territorio', 'Historia del Arte',
          'Microbiología, Medicina Preventiva y Salud Pública', 'Patología Animal',
          'Pediatría, Radiología y Medicina Física', 'Química Analítica', 'Química Orgánica',
          'Derecho administrativo', 'Derecho civil', 'Derecho mercantil',
          'Economía, sociología y política agraria', 'Estadística e investigación operativa',
          'Fisiología', 'Fundamentos del análisis económico', 'Geodinámica interna',
          'Historia antigua', 'Ingeniería agroforestal', 'Ingeniería mecánica', 'Ingeniería metalúrgica',
          'Ing. Procesos de fabricación', 'Producción animal', 'Producción vegetal',
          'Química inorgánica', 'Tecnología del medio ambiente', 'Agricultura y Economia Agraria',
          'Análisis Económico', 'Ciencias Agrarias y del Medio Natural', 'Derecho de la Empresa',
          'Derecho Privado', 'Derecho Público', 'Farmacología y Fisiología',
          'Informática e Ingeniería de Sistemas',
          'Instituto de Investigación en Ingeniería de Aragón (I3A)', 'Literatura Española',
          'Métodos Estadísticos', 'Química Inorgánica', 'Zaragoza Logistics Center (ZLC)']

recs = []

jnlfilename = 'THESES-ZARAGOZA-%s' % (ejlmod3.stampoftoday())
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

# Initialize Webdriver
options = uc.ChromeOptions()
options.binary_location='/opt/google/chrome/google-chrome'
options.binary_location='/usr/bin/chromium'
options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)


def get_sub_site(url):
    keepit = True
    print(("  [%s] --> Harversting data" % url))

    rec = {'tc': 'T', 'jnl': 'BOOK', 'note' : []}
    rec['link'] = re.sub('\/export.*', '', url)

    can_be_downloaded = False

    driver.get(url)
    my_record = BeautifulSoup(driver.page_source, 'lxml').find_all('record')

    if len(my_record) != 1:
        return

    for datafield in my_record[0].find_all('datafield'):
        tag = datafield.get('tag')
        data = datafield.find_all('subfield')

        # Get the language
        if tag == '041':
            language = data[0].text.upper()
            if language == 'SPA':
                rec['language'] = 'spanish'
            elif language != 'ITA':
                rec['language'] = 'italian'
            elif language != 'ENG':
                rec['language'] = language

        # Get the author
        elif tag == '100':
            rec['autaff'] = []
            for author in data:
                rec['autaff'].append([author.text, publisher])

        # Get the title
        elif tag == '245':
            for sf in datafield.find_all('subfield', attrs = {'code' : 'a'}):
                rec['tit'] = sf.text
            for sf in datafield.find_all('subfield', attrs = {'code' : 'b'}):
                rec['tit'] += ': ' + sf.text

        # Get the date
        elif tag == '260':
            date = datafield.find_all('subfield', attrs={'code': 'c'})
            rec['date'] = date[0].text

        # Get the pages
        elif tag == '300':
            rec['pages'] = data[0].text

        # Get the abstract
        elif tag == '520':
            if len(data[0].text) > 10:
                rec['abs'] = data[0].text

        # Get the license
        elif tag == '506':
            if len(data) != 1:
                can_be_downloaded = True
                rec['license'] = {}
                for sf in data:
                    if sf['code'] == 'u':
                        rec['license']['url'] = sf.text

        # Get the keywords
        elif tag == '653':
            rec['keyw'] = []
            for keyword in data:
                rec['keyw'].append(keyword.text)

        # Get the supervisors
        elif tag == '700':
            rec['supervisor'] = []
            for supervisor in datafield.find_all('subfield', attrs={'code': 'a'}):
                rec['supervisor'].append([re.sub('^Dra?\. ', '', supervisor.text)])

        # Get the pdf link
        elif tag == '856':
            pdf_link = datafield.find_all('subfield', attrs={'code': 'u'})
            if len(pdf_link) != 0:
                if can_be_downloaded:
                    rec['FFT'] = pdf_link[0].text
                else:
                    rec['hidden'] = pdf_link[0].text

        #department
        elif tag == '910':
            for sf in data:
                if sf['code'] == 'a':
                    dep = sf.text.strip()
                    if dep in boring:
                        keepit = False
                    else:
                        rec['note'].append('dep=%s' % (dep))
                elif sf['code'] == 'b':
                    subdep = sf.text.strip()
                    if subdep in boring:
                        keepit = False
                    else:
                        rec['note'].append('subdep=%s' % (subdep))
        #program
        elif tag == '521':
            for sf in data:
                if sf['code'] == 'a':
                    prg = sf.text.strip()
                    if prg in boring:
                        keepit = False
                    else:
                        rec['note'].append('prg=%s' % (prg))
    
            

        # Write the fake DOI
        rec['doi'] = '20.2000/Zargoza/' + b16encode(url.encode('utf-8')).decode('utf-8')
    if keepit:
        if skipalreadyharvested and rec['doi'] in alreadyharvested:
            print('    already in backup')
        else:
            recs.append(rec)
            ejlmod3.printrecsummary(rec)
    else:
        ejlmod3.adduninterestingDOI(url)
    return


for page in range(pages):
    to_curl = 'https://zaguan.unizar.es/search?cc=tesis&ln=en&rg=' + str(rpp) + '&jrec=' + str(page * rpp + 1)
    driver.get(to_curl)
    ejlmod3.printprogress("=", [[page+1, pages], [to_curl]])
    # Get the index links
    for article in BeautifulSoup(driver.page_source, 'lxml').find_all('a', attrs={'class': 'tituloenlazable'}):
        nothing, record, number_and_params = article.get('href').split('/')
        final = '/%s/%s' % (record, number_and_params.split('?')[0])
        finalurl = 'https://zaguan.unizar.es%s/export/xm?ln=en' % final
        if ejlmod3.checkinterestingDOI(finalurl):
            get_sub_site(finalurl)
            sleep(4)
    sleep(10)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
