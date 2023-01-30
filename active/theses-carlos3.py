# -*- coding: utf-8 -*-
# harvest theses from Carlos III U., Madrid
# JH: 2019-02-23

from requests import Session
from bs4 import BeautifulSoup
from time import sleep
from urllib.parse import urlparse, parse_qs
import ejlmod3
import re

publisher = 'Carlos III U., Madrid'
jnlfilename = 'THESES-CARLOS-%s' % (ejlmod3.stampoftoday())
rpp = 100
pages = 2

boring = ['Filología', 'Biología y Biomedicina', 'Arte', 'Derecho',
          'Filosofía', 'Historia del Arte', 'Historia',
          'Ingeniería Industrial', 'Política', 'Sociología',
          'Biblioteconomía y Documentación', 'Economía', 'Empresa',
          'Aeronáutica', 'Educación', 'Energías Renovables',
          'Geografía', 'Materiales', 'Medicina', 'Medio Ambiente',
          'Literatura', 'Ingeniería Mecánica', 'Fusión',
          'Robótica e Informática Industrial']

def dspace_extract_links(content, prafix: str):
    soup = BeautifulSoup(index_resp.content.decode('utf-8').replace('<?xml version="1.0" encoding="UTF-8"?>', ''), 'lxml')
    article_links = soup.find_all('a', {'href': re.compile('/handle/\d{0,}/\d{0,}')})
    filtered = filter(lambda article: False if article.parent.get('class') is None
                        else True if 'artifact-title' in article.parent.get('class')
                        else False, article_links)

    return list(filtered)

recs = []

with Session() as session:
    for page in range(pages):
        tocurl = 'https://e-archivo.uc3m.es/handle/10016/2/browse?rpp=' + str(rpp) + '&sort_by=2&type=dateissued&offset=' + str(rpp*page) + '&etal=-1&order=DESC'
        ejlmod3.printprogress('=', [[page+1, pages], [tocurl], [len(recs)]])
        try:
            index_resp = session.get(tocurl)
            if index_resp.status_code != 200:
                sleep(30)
                index_resp = session.get(tocurl)
                if index_resp.status_code != 200:
                    print("[{}] --> Error: Can't reach this index page! Skipping this ".format(tocurl))
                    continue
        except:
            sleep(30)
            index_resp = session.get(tocurl)
            if index_resp.status_code != 200:
                print("[{}] --> Error: Can't reach this index page! Skipping this ".format(tocurl))
                continue

        v = 0
        for link in dspace_extract_links(index_resp, 'https://e-archivo.uc3m.es'):
            artlink = 'https://e-archivo.uc3m.es' + link.get('href')
            if not ejlmod3.checkinterestingDOI(artlink):
                print('[%s]     already identified as uninteresting' % (artlink + '?show=full'))
                continue
            else:
                print("[%s] --> Harvesting data" % (artlink + '?show=full'))
            rec: dict = {'tc': 'T', 'jnl': 'BOOK', 'autaff': [], 'supervisor': [], 'license': {},
                         'link': artlink, 'note' : []}
            try:
                site_resp = session.get(artlink + '?show=full')
                if site_resp.status_code != 200:
                    print("[%s] --> Error: Can't open!")
                    continue
            except:
                sleep(30)
                site_resp = session.get(artlink + '?show=full')
                if site_resp.status_code != 200:
                    print("[%s] --> Error: Can't open!")
                    continue

            jump = False
            soup = BeautifulSoup(site_resp.content.decode('utf-8').replace('<?xml version="1.0" encoding="UTF-8"?>', ''), 'lxml')
            ejlmod3.metatagcheck(rec, soup, ['DC.creator', 'DCTERMS.issued', 'DC.rights', 'DC.subject', 'DC.title',
                                             'DC.identifier', 'DCTERMS.extent', 'DC.type', 'DC.language',
                                             'citation_pdf_url'])
            for row in soup.find_all('tr', attrs={'class': 'ds-table-row'}):
                cols = row.find_all('td')

                title = cols[0].text
                data = cols[1].text

                # Get the supervisor
                if title == 'dc.contributor.advisor':
                    rec['supervisor'].append([data.replace('\n', '')])

                # Get the abstract
                if title == 'dc.description.abstract':
                    if data.find('the') != -1 or data.find('of') != -1 or data.find('if') != -1:
                        rec['abs'] = data

                # Get the DOI [is not the DOI of the thesis]                
                #if title == 'dc.relation.haspart':
                #    rec['doi'] = data.replace('https://doi.org/', '')

                # Get the license
                if title == 'dc.rights.uri':
                    payload = data.replace('http://creativecommons.org/licenses/', '').split('/')

                    rec['license']['url'] = data
                    if len(payload) == 4:
                        rec['license']['statement'] = payload[0].upper() + '-' + payload[1].upper()

                if title == 'dc.type':
                    if data != 'doctoralThesis':
                        print('    skip', data)
                        jump = True

                # Get the note
                if title == 'dc.subject.eciencia':
                    if data in boring:
#                        print('    skip', data)
                        jump = True
                    elif data in ['Informática']:
                        rec['fc'] = 'c'
                    elif data in ['Matemáticas']:
                        rec['fc'] = 'm'
                    elif data in ['Astronomía']:
                        rec['fc'] = 'a'
                    elif not data in ['Física']:
                        rec['note'].append('dc.subject.eciencia:::'+data)

            # Get the pdf file
            pdf_section = soup.find_all('div', attrs={'class': 'file-link'})
            if len(pdf_section) == 1:
                link = pdf_section[0].find_all('a')

                if len(link) == 1:
                    params = parse_qs('https://e-archivo.uc3m.es' + link[0].get('href'))

                    if len(params.get('isAllowed')) == 1:
                        if params.get('isAllowed')[0] == 'y':
                            rec['FFT'] = 'https://e-archivo.uc3m.es' + link[0].get('href')
            sleep(5)
            v += 1
            #document type
            if 'PeerReviewed' in rec['note']:
                jump = True
            if not jump:
                recs.append(rec)
            else:
                #print("[%s] --> Not a PhD theses! Skipping..." % ('https://e-archivo.uc3m.es' + link.get('href') + '?show=full'))
                ejlmod3.adduninterestingDOI(artlink)
                #continue
        sleep(5)
ejlmod3.writenewXML(recs, publisher, jnlfilename)
