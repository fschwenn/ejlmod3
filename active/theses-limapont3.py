# -*- coding: utf-8 -*-
# harvest theses from Lima, Pont. U. Catolica
# JH: 2023-01-23

from bs4 import BeautifulSoup
from requests import Session
from time import sleep
from urllib.parse import parse_qs
import re
import ejlmod3

publisher = 'Lima, Pont. U. Catolica'
jnlfilename = 'THESES-LIMAPONT-%s' % (ejlmod3.stampoftoday())
rpp = 40
pages = 8
skipalreadyharvested = True
boring = ['Administrac%C3%ADon+Estrat%C3%A9gica+de+Empresas',
          'Administraci%C3%B3n+Estrat%C3%A9gica+de+Empresas',
          'Antropolog%C3%ADa',
          'Antropolog%C3%ADa+con+menci%C3%B3n+en+Estudios+Andinos',
          'Ciencia+Pol%C3%ADtica+y+Gobierno', 'Ciencias+de+la+Educaci%C3%B3n', 'Derecho',
          'Doctora+en+Ciencia+Pol%C3%ADtica+y+Gobierno',
          'Doctor+en+Administraci%C3%B3n+Estrat%C3%A9gica+de+Empresas',
          'Doctor+en+Antropolog%C3%ADa',
          'Doctor+en+Antropolog%C3%ADa+con+menci%C3%B3n+en+Estudios+Andinos',
          'Doctor+en+Ciencia+Pol%C3%ADtica+y+Gobierno',
          'Doctor+en+Ciencias+de+la+Educaci%C3%B3n', 'Doctor+en+Derecho',
          'Doctor+en+Econom%C3%ADa', 'Doctor+en+Filosof%C3%ADa',
          'Doctor+en+Gesti%C3%B3n+Estrat%C3%A9gica+con+menci%C3%B3n+en+Gesti%C3%B3n+Empresarial+y+Sostenibilidad',
          'Doctor+en+Gesti%C3%B3n+Estrat%C3%A9gica+con+menci%C3%B3n+en+Innovaci%C3%B3n+y+Gesti%C3%B3n+en+Educaci%C3%B3nr',
          'Doctor+en+Historia', 'Doctor+en+Historia+con+menci%C3%B3n+en+Estudios+Andinos',
          'Doctor+en+Humanidades',
          'Doctor+en+Ling%C3%BC%C3%ADstica+con+menci%C3%B3n+en+Estudios+Andinos',
          'Doctor+en+Literatura+Hispanoamericana', 'Doctor+en+Psicolog%C3%ADa',
          'Doctor+en+Sociolog%C3%ADa', 'Econom%C3%ADa', 'Filosof%C3%ADa',
          'Gesti%C3%B3n+Estrat%C3%A9gica+con+menci%C3%B3n+en+Gesti%C3%B3n+Empresarial+y+Sostenibilidad',
          'Gesti%C3%B3n+Estrat%C3%A9gica+con+menci%C3%B3n+en+Innovaci%C3%B3n+y+Gesti%C3%B3n+en+Educaci%C3%B3n+Superior',
          'Historia', 'Historia+con+menci%C3%B3n+en+Estudios+Andinos', 'Humanidades',
          'Ling%C3%BC%C3%ADstica+con+menci%C3%B3n+en+Estudios+Andinos',
          'Literatura+Hispanoamericana', 'Psicolog%C3%ADa', 'Sociolog%C3%ADa']

recs: list = []

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []
with Session() as session:
    prerecs = []
    for page in range(pages):
        to_curl = 'https://tesis.pucp.edu.pe/repositorio/handle/20.500.12404/1/browse?rpp=' + str(rpp) + '&sort_by=2&type=dateissued&offset=' + str(rpp*page) + '&etal=-1&order=DESC'
        print("#### OPEN PAGE %i/%i ####" % (page+1, pages))
        print(to_curl)

        try:
            index_resp = session.get(to_curl)
            if index_resp.status_code != 200:
                print("Error: Can't open page!")
                continue
        except:
            print('   try again in 60s')
            sleep(60)
            index_resp = session.get(to_curl)

        tocpage = BeautifulSoup(index_resp.content.decode('utf-8'), 'lxml')
        for rec in ejlmod3.getdspacerecs(tocpage, 'https://tesis.pucp.edu.pe', alreadyharvested=alreadyharvested):
            keepit = True
            for deg in rec['degrees']:
                if deg == 'Matem%C3%A1ticas':
                    rec['fc'] = 'm'
                if deg in boring:
                    keepit = False
            if keepit:
                prerecs.append(rec)
        #links = dspace_extract_links(index_resp.content.decode('utf-8'))
        print('  %4i records so far' % (len(prerecs)))
        sleep(4)


    for (i, rec) in enumerate(prerecs):
        jump = False
        ejlmod3.printprogress('-', [[i+1, len(prerecs)], [rec['link']], [len(recs)]])
        rec['supervisor'] = []

        try:
            data_resp = session.get(rec['link'])
            sleep(2)
            if data_resp.status_code != 200:
                print("[%s] --> Error: Can't open page! Skipping...." % rec['link'])
                continue
        except:
            print('   try again in 60s')
            sleep(60)
            data_resp = session.get(rec['link'])
        site_soup = BeautifulSoup(data_resp.content.decode('utf-8'), 'lxml')
        ejlmod3.metatagcheck(rec, site_soup, ['DC.creator', 'DCTERMS.issued', 'DC.identifier', 'DC.language', 'DC.subject', 'DC.title', 'DC.rights'])
        rec['autaff'][-1].append(publisher)

        for row in site_soup.find_all('tr', attrs={'class': 'ds-table-row'}):
            cols = row.find_all('td')

            title = cols[0].text
            data = cols[1].text

            # Get the supervisor
            if title == 'dc.contributor.advisor':
                rec['supervisor'].append([data])
            # Get the abstract
            if title == 'dc.description.abstract':
                if data.find('the') != -1 and data.find('it') != -1:
                    rec['abs'] = data
                else:
                    rec['abs'] = data
                    rec['language'] = 'Spanish'

            # Get the level
            if title == 'renati.level':
                if data != 'https://purl.org/pe-repo/renati/level#doctor':
                    jump = True
                    print('   skip %s' % (data))
                    
        # Get the pdf file
        pdf_section = site_soup.find_all('div', attrs={'class': 'file-link'})
        if len(pdf_section) != 0:
            pdf = pdf_section[0].find_all('a')

            if len(pdf) == 1:
                params = parse_qs('https://e-archivo.uc3m.es' + pdf[0].get('href'))
                if len(params.get('isAllowed')) == 1:
                    if params.get('isAllowed')[0] == 'y':
                        rec['FFT'] = 'https://e-archivo.uc3m.es' + pdf[0].get('href')
        if jump:
            ejlmod3.adduninterestingDOI(rec['hdl'])
        else:
            recs.append(rec)
            ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
