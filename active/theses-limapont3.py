# -*- coding: utf-8 -*-
# harvest theses from Lima, Pont. U. Catolica
# JH: 2019-01-23

from bs4 import BeautifulSoup
from requests import Session
from time import sleep
from urllib.parse import parse_qs
import re
import ejlmod3



def dspace_extract_links(content: str):
    soup = BeautifulSoup(content, 'lxml')
    artifacts: list = soup.find_all('h4', attrs={'class': 'artifact-title'})
    out: list = []

    for artifact in artifacts:
        out.append('https://tesis.pucp.edu.pe' + artifact.find_all('a')[0].get('href') + '?show=full')

    return out

publisher = 'Lima, Pont. U. Catolica'
jnlfilename = 'THESES-LIMAPONT-%s' % (ejlmod3.stampoftoday())
rpp = 20
pages = 2
recs: list = []

with Session() as session:
    for page in range(pages):
        to_curl = 'https://tesis.pucp.edu.pe/repositorio/browse?rpp=' + str(rpp) + '&sort_by=2&type=dateissued&offset=' + str(rpp*page) + '&etal=-1&order=DESC'
        print("#### OPEN PAGE %i/%i ####" % (page+1, pages))
        print(to_curl)

        index_resp = session.get(to_curl)

        if index_resp.status_code != 200:
            print("Error: Can't open page!")
            continue

        #index_soup = BeautifulSoup(index_resp.content.decode('utf-8'), 'lxml')
        #recs += ejlmod3.getdspacerecs(tocpage, 'https://tesis.pucp.edu.pe/repositorio')
        links = dspace_extract_links(index_resp.content.decode('utf-8'))


        jump = False
        for link in links:
            print('[%s] --> Harvesting data' % link)
            rec: dict = {'tc': 'T', 'jnl': 'BOOK', 'autaff': [], 'supervisor': [], 'license': {}}

            data_resp = session.get(link)

            if data_resp.status_code != 200:
                print("[%s] --> Error: Can't open page! Skipping...." % link)
                continue

            site_soup = BeautifulSoup(data_resp.content.decode('utf-8'), 'lxml')
            ejlmod3.metatagcheck(rec, site_soup, ['DC.creator', 'DCTERMS.issued', 'DC.identifier', 'DC.language', 'DC.subject', 'DC.title'])

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

                # Get the license
                if title == 'dc.rights.uri':
                    payload = data.replace('http://creativecommons.org/licenses/', '').split('/')

                    rec['license']['url'] = data
                    if len(payload) == 4:
                        rec['license']['statement'] = payload[0].upper() + '-' + payload[1].upper()

                # Get the level
                if title == 'renati.level':
                    if data != 'https://purl.org/pe-repo/renati/level#doctor':
                        jump = True

            # Get the pdf file
            pdf_section = site_soup.find_all('div', attrs={'class': 'file-link'})
            if len(pdf_section) != 0:
                pdf = pdf_section[0].find_all('a')

                if len(pdf) == 1:
                    params = parse_qs('https://e-archivo.uc3m.es' + pdf[0].get('href'))

                    if len(params.get('isAllowed')) == 1:
                        if params.get('isAllowed')[0] == 'y':
                            rec['FFT'] = 'https://e-archivo.uc3m.es' + pdf[0].get('href')
            print(rec)
            sleep(10)
            if not jump:
                recs.append(rec)
                break
            else:
                print("[%s] --> Not a PhD theses! Skipping..." % link)
                continue

        break
        sleep(10)

ejlmod3.writenewXML(recs, publisher, jnlfilename, xmldir='dev/', retfilename='dev/')
