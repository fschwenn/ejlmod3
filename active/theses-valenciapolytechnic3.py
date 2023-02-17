# -*- coding: utf-8 -*-
# harvest thesis from Valencia, Polytechnic U.
#JH: 2023-02-14

from bs4 import BeautifulSoup
from requests import Session
from time import sleep
import ejlmod3
import re

jnlfilename = 'THESES-VALENCIA-POLYTECHNIC-%s' % (ejlmod3.stampoftoday())

publisher = 'Valencia, Polytechnic U.'
rpp = 100
pages = 3
skipalreadyharvested = True
boring = ["Departamento de Biotecnología - Departament de Biotecnologia",
          "Departamento de Dibujo - Departament de Dibuix",
          "Departamento de Ingeniería Hidráulica y Medio Ambiente - Departament d'Enginyeria Hidràulica i Medi Ambient",
          "Departamento de Ingeniería Mecánica y de Materiales - Departament d'Enginyeria Mecànica i de Materials",
          "Departamento de Máquinas y Motores Térmicos - Departament de Màquines i Motors Tèrmics",
          "Departamento de Producción Vegetal - Departament de Producció Vegetal",
          "Departamento de Proyectos de Ingeniería - Departament de Projectes d'Enginyeria",
          "Departamento de Química - Departament de Química",
          "Escuela Técnica Superior de Arquitectura - Escola Tècnica Superior d'Arquitectura",
          "Escuela Técnica Superior de Ingeniería del Diseño - Escola Tècnica Superior d'Enginyeria del Disseny",
          "Escuela Técnica Superior de Ingenieros de Caminos, Canales y Puertos - Escola Tècnica Superior d'Enginyers de Camins, Canals i Ports",
          "Facultad de Administración y Dirección de Empresas - Facultat d'Administració i Direcció d'Empreses",
          "Facultad de Bellas Artes - Facultat de Belles Arts",
          "Instituto Universitario de Ingeniería de Alimentos para el Desarrollo - Institut Universitari d'Enginyeria d'Aliments per al Desenvolupament",
          "Instituto Universitario Mixto de Tecnología Química - Institut Universitari Mixt de Tecnologia Química",
          "Departamento de Ciencia Animal - Departament de Ciència Animal",
          "Departamento de Composición Arquitectónica - Departament de Composició Arquitectònica",
          "Departamento de Comunicación Audiovisual, Documentación e Historia del Arte - Departament de Comunicació Audiovisual, Documentació i Història de l'Art",
          "Departamento de Conservación y Restauración de Bienes Culturales - Departament de Conservació i Restauració de Béns Culturals",
          "Departamento de Construcciones Arquitectónicas - Departament de Construccions Arquitectòniques",
          "Departamento de Economía y Ciencias Sociales - Departament d'Economia i Ciències Socials",
          "Departamento de Ecosistemas Agroforestales - Departament d'Ecosistemes Agroforestals",
          "Departamento de Escultura - Departament d'Escultura",
          "Departamento de Estadística e Investigación Operativa Aplicadas y Calidad - Departament d'Estadística i Investigació Operativa Aplicades i Qualitat",
          "Departamento de Expresión Gráfica Arquitectónica - Departament d'Expressió Gràfica Arquitectònica",
          "Departamento de Ingeniería Cartográfica Geodesia y Fotogrametría - Departament d'Enginyeria Cartogràfica, Geodèsia i Fotogrametria",
          "Departamento de Ingeniería de la Construcción y de Proyectos de Ingeniería Civil - Departament d'Enginyeria de la Construcció i de Projectes d'Enginyeria Civil",
          "Departamento de Ingeniería del Terreno - Departament d'Enginyeria del Terreny",
          "Departamento de Ingeniería de Sistemas y Automática - Departament d'Enginyeria de Sistemes i Automàtica",
          "Departamento de Ingeniería e Infraestructura de los Transportes - Departament d'Enginyeria i Infraestructura dels Transports",
          "Departamento de Ingeniería Eléctrica - Departament d'Enginyeria Elèctrica",
          "Departamento de Ingeniería Gráfica - Departament d'Enginyeria Gràfica",
          "Departamento de Ingeniería Química y Nuclear - Departament d'Enginyeria Química i Nuclear",
          "Departamento de Ingeniería Rural y Agroalimentaria - Departament d'Enginyeria Rural i Agroalimentària",
          "Departamento de Ingeniería Textil y Papelera - Departament d'Enginyeria Tèxtil i Paperera",
          "Departamento de Lingüística Aplicada - Departament de Lingüística Aplicada",
          "Departamento de Mecánica de los Medios Continuos y Teoría de Estructuras - Departament de Mecànica dels Medis Continus i Teoria d'Estructures",
          "Departamento de Organización de Empresas - Departament d'Organització d'Empreses",
          "Departamento de Pintura - Departament de Pintura",
          "Departamento de Proyectos Arquitectónicos - Departament de Projectes Arquitectònics",
          "Departamento de Proyectos de Ingeniería - Departament de Projectes d'Enginyeria",
          "Departamento de Tecnología de Alimentos - Departament de Tecnologia d'Aliments",
          "Departamento de Urbanismo - Departament d'Urbanisme",
          "Instituto de Agroquímica y Tecnologia de Alimentos - Institut d'Agroquímica i Tecnologia d'Aliments",
          "Instituto de Gestión de la Innovación y del Conocimiento - Institut de Gestió de la Innovació i del Coneixement",
          "Instituto Universitario de Ingeniería del Agua y del Medio Ambiente - Institut Universitari d'Enginyeria de l'Aigua i Medi Ambient"]
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

recs: list = []
prerecs: list = []
with Session() as session:
    for page in range(pages):
        to_curl = 'https://riunet.upv.es/handle/10251/321/browse?rpp=' + str(rpp) + '&sort_by=2&type=dateissued&offset=' + str(rpp * page) + '&etal=-1&order=DESC'
        ejlmod3.printprogress('=', [[page+1, pages], [to_curl]])
        inbackup = []
        index_response = session.get(to_curl)

        if index_response.status_code != 200:
            print("Error: Can't open the page! Skipping....")
            continue
        for rec in ejlmod3.getdspacerecs(BeautifulSoup(index_response.content.decode('utf-8').replace('<?xml version="1.0" encoding="UTF-8"?>', ''), 'lxml'), 'https://riunet.upv.es', divclass='item-metadata'):
            if skipalreadyharvested and rec['hdl'] in alreadyharvested:
                inbackup.append(rec['hdl'])
            else:
                prerecs.append(rec)
        print('  %4i records so far (%i already in backup)' % (len(prerecs), len(inbackup)))
        sleep(5)
    for i in range(len(prerecs)):
        keepit = True
        ejlmod3.printprogress('-', [[i+1, len(prerecs)], [prerecs[i].get('link')], [len(recs)]])
        #print("[{}] --> Harvesting data".format(prerecs[i].get('link') + '?show=full'))
        data_resp = session.get(prerecs[i].get('link') + '?show=full')

        if data_resp.status_code != 200:
            print("[{}] --> Error: Can't open the page! Skipping...".format(prerecs[i].get('link')) + '?show=full')

        prerecs[i]['supervisor'] = []
        prerecs[i]['autaff'] = []
        prerecs[i]['keyw'] = []
        prerecs[i]['note'] = []

        artpage = BeautifulSoup(data_resp.content.decode('utf-8').replace('<?xml version="1.0" encoding="UTF-8"?>', ''), 'lxml')
        ejlmod3.metatagcheck(prerecs[i], artpage, ['DCTERMS.extent', 'DC.language', 'citation_pdf_url'])
        # Get the table
        for row in artpage.find_all('tr', attrs={'class': 'ds-table-row'}):
            cols = row.find_all('td')
            title = cols[0].text
            data = cols[1].text

            # Get the supervisors
            if title == 'dc.contributor.advisor':
                prerecs[i]['supervisor'].append([data.replace('\n', '')])

            # Get the author
            if title == 'dc.contributor.author':
                prerecs[i]['autaff'].append([data.replace('\n', '')])

            # Get the issued date| issued date falsch genutzt (zumindest bei embargo theses)
            #if title == 'dc.date.issued':
            if title == 'dc.date.created':
                prerecs[i]['tit'] = data.replace('\n', '')

            # Get the handle
            if title == 'dc.identifier.uri':
                hdl = data.split('/')
                prerecs[i]['hdl'] = hdl[-2] + '/' + hdl[-1]

            # Get the abstract
            if title == 'dc.description.abstract':
                if data[0:len('[EN]')] == '[EN]':
                    prerecs[i]['abs'] = data[len('[EN]'):]

            # Get the keywords
            if title == 'dc.subject':
                prerecs[i]['keyw'].append(data.replace('\n', ''))

            # Get the title
            if title == 'dc.title':
                    prerecs[i]['tit'] = data.replace('\n', '')

            # Get the thesis type
            if title == 'dc.type':
                if data.replace('\n', '') != 'Tesis doctoral':
                    continue

            # Get the DOI
            if title == 'dc.identifier.doi':
                prerecs[i]['doi'] = data.replace('\n', '')

            # Get the affiliation
            if title == 'dc.contributor.affiliation':
                dep = re.sub('Universitat Politècnica de València. ', '', data)
                if dep in ["Departamento de Sistemas Informáticos y Computación - Departament de Sistemes Informàtics i Computació",
                           "Departamento de Informática de Sistemas y Computadores - Departament d'Informàtica de Sistemes i Computadors"]:
                    rec['fc'] = 'c'
                elif dep in ["Departamento de Matemática Aplicada - Departament de Matemàtica Aplicada"]:
                    rec['fc'] = 'm'
                elif dep in boring:
                    keepit = False
                else:
                    prerecs[i]['note'].append(dep)
        if keepit:
            print('  try to get ORCIDs')
            sleep(5)
            data_resp = session.get(prerecs[i].get('link'))
            if data_resp.status_code != 200:
                print("[{}] --> Error: Can't open the page! Skipping...".format(prerecs[i].get('link')))
            artpage = BeautifulSoup(data_resp.content.decode('utf-8').replace('<?xml version="1.0" encoding="UTF-8"?>', ''), 'lxml')
            for tr in artpage.find_all('tr'):
                spant = ''
                for span in tr.find_all('span', attrs = {'class' : 'bold'}):
                    spant = span.text.strip()
                    #ORCID of author
                    if spant in ['Author:', 'Autor:']:
                        for a in tr.find_all('a', attrs = {'class' : 'ds-authority-confidence'}):
                            if a.has_attr('href') and re.search('orcid.org', a['href']):
                                prerecs[i]['autaff'][-1].append(re.sub('.*org\/', 'ORCID:', a['href']))
                    #ORCIDs of supervisors
                    elif spant in ['Director(s):', 'Director(es):']:
                        prerecs[i]['supervisor'] = []
                        for sv in tr.find_all('span', attrs = {'class' : 'ds-dc_contributor_author-authority'}):
                            prerecs[i]['supervisor'].append([sv.text.strip()])
                            for a in sv.find_all('a', attrs = {'class' : 'ds-authority-confidence'}):
                                if a.has_attr('href') and re.search('orcid.org', a['href']):
                                    prerecs[i]['supervisor'][-1].append(re.sub('.*org\/', 'ORCID:', a['href']))
            #embargo
            for a in artpage.find_all('a', attrs = {'title' : 'Ítem embargado'}):
                del prerecs[i]['pdf_url']
                print('     PDF embargoed   :-(')
            prerecs[i]['autaff'][-1].append(publisher)
            ejlmod3.printrecsummary(prerecs[i])
            recs.append(prerecs[i])
        else:
            ejlmod3.adduninterestingDOI(prerecs[i]['hdl'])
        sleep(5)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
