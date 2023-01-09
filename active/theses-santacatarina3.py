# -*- coding: utf-8 -*-
#harvest theses of university santacatrina
#JH: 2023-01-01

import re
from requests import Session
from time import sleep
from bs4 import BeautifulSoup
from typing import Union
import ejlmod3

publisher = 'Santa Catarina U.'
jnlfilename = 'THESES-SANTACATARINA-%s' % ejlmod3.stampoftoday()

rpp = 10
boring = ['Dissertação (Mestrado)', 'Dissertação (Mestrado profissional)',
          'Master Thesis']

def dspace_extract_links(content: str, prafix: str):
    soup = BeautifulSoup(content, 'lxml')
    article_links = soup.find_all('a', {'href': re.compile('/handle/\d{0,}/\d{0,}')})
    filtered = filter(lambda article: False if article.parent.get('class') is None
                        else True if 'artifact-title' in article.parent.get('class')
                        else False, article_links)

    return list(filtered)


def dspace_table_extract_information(titles: list, link: str, mapping: dict) -> Union[dict, int]:
    extracted_data: dict = {}

    with Session() as session:
        resp = session.get(link)

        if resp.status_code != 200:
            return -1


        resp_data = resp.content.decode('utf-8').replace('<?xml version="1.0" encoding="UTF-8"?>', '')
        soup = BeautifulSoup(resp_data, 'lxml')

        for title in titles:
            patter: str = '^%s$' % title.replace('.', '\\.')
            mapped_name: Union[str, dict] = mapping[title]

            if mapped_name is None:
                return -2

            fields = soup.find_all('td', text=re.compile(patter, re.MULTILINE))

            if len(fields) == 0:
                print("Can't find:", mapped_name)
                continue

            for field in fields:
                data_field: str = field.parent.find_all('td')[1].text

                datatype: int = mapping[title].get('datatype')

                if datatype == 1:
                    extracted_data[mapped_name.get('name')] = data_field
                elif datatype == 2:
                    if mapped_name.get('name') in extracted_data.keys():
                        extracted_data[mapped_name.get('name')].append(data_field)
                    else:
                        extracted_data[mapped_name.get('name')] = [data_field]
                elif datatype == 3:
                    if mapped_name.get('name') in extracted_data.keys():
                        extracted_data[mapped_name.get('name')].append([data_field])
                    else:
                        extracted_data[mapped_name.get('name')] = [[data_field]]

    # Get the pdf link
    pdf_section = soup.find_all('a', attrs={'href': re.compile('bitstream')})
    if len(pdf_section) == 2:
        rec['hidden'] = 'https://repositorio.ufsc.br%s' % pdf_section[0].get('href')

    return extracted_data


recs = []
alllinks = []
with Session() as session:

    for (dep, fc, pages) in [('76362', 'c', 2), ('75302', '', 2), ('77533', '', 2), ('123199', 'm', 1),
                             ('80823', 'mc', 1), ('103512', 'm', 2), ('74675', '', 0)]:
        for page in range(pages):
            to_curl = 'https://repositorio.ufsc.br/handle/123456789/' + dep + '/browse?rpp=' + str(
                rpp) + '&sort_by=2&type=dateissued&offset=' + str(rpp * page) + '&etal=-1&order=DESC'
            ejlmod3.printprogress('=', [[dep], [page+1, pages], [to_curl]])

            print('#### OPENING INDEX PAGE (%i/%i) OF %s:%s ####' % (page + 1, pages, dep, fc))
            index_resp = session.get(to_curl)

            if index_resp.status_code != 200:
                print('Error: Can\'t open the page\nSkipping this index page.')
                continue

            index_resp_data = index_resp.content.decode('utf-8').replace('<?xml version="1.0" encoding="UTF-8"?>', '')

            soup = BeautifulSoup(index_resp_data, 'lxml')
            article_links = dspace_extract_links(index_resp_data, 'https://repositorio.ufsc.br')
            rec = {}

            # Open the sub site
            for article in article_links:
                if ejlmod3.checkinterestingDOI(article.get('href')) and not article.get('href') in alllinks:
                    print('[%s] --> Harvesting data' % 'https://repositorio.ufsc.br%s?show=full' % article.get('href'))
                    alllinks.append(article.get('href'))
                else:
                    print('[%s]' % 'https://repositorio.ufsc.br%s?show=full' % article.get('href'))
                    continue
                try:
                    data_resp = session.get('https://repositorio.ufsc.br%s?show=full' % article.get('href'))
                except Exception:
                    print('[%s] --> Is not a real record. Skipping...' % 'https://repositorio.ufsc.br%s?show=full' %
                          article.get('href'))
                    continue

                if data_resp.status_code != 200:
                    print('[%s] Error: Can\'t open page!')
                    continue

                data_resp_data = data_resp.content.decode('utf-8').replace('<?xml version="1.0" encoding="UTF-8"?>', '')
                data_soup = BeautifulSoup(data_resp_data, 'lxml')

                mapping = {
                    'dc.contributor.advisor': {
                        'name': 'supervisor',
                        'datatype': 3
                    },
                    'dc.type': {
                        'name': 'note',
                        'datatype': 2
                    },
                    'dc.contributor.author': {
                        'name': 'autaff',
                        'datatype': 3
                    },
                    'dc.date.issued': {
                        'name': 'date',
                        'datatype': 1
                    },
                    'dc.identifier.uri': {
                        'name': 'link',
                        'datatype': 1
                    },
                    'dc.description.abstract': {
                        'name': 'abs',
                        'datatype': 1
                    },
                    'dc.subject.classification': {
                        'name': 'keyw',
                        'datatype': 2
                    },
                    'dc.title': {
                        'name': 'tit',
                        'datatype': 1
                    }
                }

                keepit = True
                rec = dspace_table_extract_information(mapping.keys(), 'https://repositorio.ufsc.br%s?show=full' % article.get('href'), mapping)
                rec['tc'] = 'T'
                rec['jnl'] = 'BOOK'
                if len(fc) != 0:
                    rec['fc'] = fc
                ejlmod3.metatagcheck(rec, data_soup, ['DCTERMS.extent', 'DC.language', 'DCTERMS.abstract', 'DC.type'])
                rec['autaff'][-1].append(publisher)
                if 'note' in rec:
                    for note in rec['note']:
                        if note in boring:
                            keepit = False
                            ejlmod3.adduninterestingDOI(article.get('href'))
                if keepit:
                    recs.append(rec)
                sleep(5)
            sleep(10)
        sleep(5)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
