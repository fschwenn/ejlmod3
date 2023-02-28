# -*- coding: UTF-8 -*-
# program to harvest Sao Carlos Federal U.
# FS 2023-02-26

from requests import Session
from bs4 import BeautifulSoup
#from spacy.language import Language
#from spacy_language_detection import LanguageDetector
#import spacy
import re
import ejlmod3
from time import sleep

publisher = 'Sao Carlos Federal U.'
jnlfilename = 'THESES-SAO-CARLOS-FEDERAL-%s' % (ejlmod3.stampoftoday())
rpp = 20
pages = 1
skipalreadyharvested = True

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
    alreadyharvested += ['20.2000/SAO-CARLOS-FEDERAL/7468',
                         '20.2000/SAO-CARLOS-FEDERAL/7412']

def dspace_table_data(rec: dict, content: str, interesting_data: list, link: str):
    soup = BeautifulSoup(content, 'lxml')

    for row in soup.find_all('tr', attrs={'class': 'ds-table-row'}):
        cols = row.find_all('td')

        title = cols[0].text
        data = cols[1].text

        for i in interesting_data:
            if i.get('title') == title:
                if i.get('custom_handler') is not None:
                    rec[i.get('name')] = i.get('custom_handler')(data)
                    break

                if i.get('type') == 1:
                    rec[i.get('name')] = data
                if i.get('type') == 2:
                    if i.get('name') in rec.keys():
                        rec[i.get('name')].append(data)
                    else:
                        rec[i.get('name')] = [data]
                if i.get('type') == 3:
                    if i.get('name') in rec.keys():
                        rec[i.get('name')].append([data])
                    else:
                        rec[i.get('name')] = [[data]]

                break

    # Trying to get the pdf link
    pdf_link = soup.find_all('a')
    for i in pdf_link:
        if i.get('href') is None:
            continue
        if i.get('href').find('/bitstream/handle/') != -1 and i.get('href').find('.pdf') != -1:
            if 'license' in rec.keys():
                rec['FFT'] = link + i.get('href')
            else:
                rec['hidden'] = link + i.get('href')
            break
    # Check if language is english
    """if rec['abs'] is not None:
        nlp_model = spacy.load('en_core_web_trf')
        def get_lang_detector(nlp, name):
            return LanguageDetector(seed=42)
        Language.factory('language_detector', func=get_lang_detector)
        nlp_model.add_pipe('language_detector', last=True)
        doc = nlp_model(rec['abs'])
        detect_language = doc._.language
        if detect_language.get('language') != 'en' and detect_language.get('score') > 0.90:
            rec['lang'] = detect_language.get('language')"""

def compute_license(data):
    splitted_link: list = data.split('/')
    if len(splitted_link) >= 4 and re.search('creativecommons', data):
        
        license_code = '{}-{}-{}'.format(splitted_link[-4], splitted_link[-3], splitted_link[-2]).upper()

        return {'statement': license_code, 'link': data}
    else:
        return {}


recs = []

with Session() as session:
    for (dep, fc) in [('5627', 'm'), ('4893', '')]:
        for page in range(pages):
            tocurl = 'https://repositorio.ufscar.br/handle/ufscar/' + dep + '/browse?rpp=' + str(rpp) + '&sort_by=2&type=dateissued&offset=' + str(rpp*page) + '&etal=-1&order=DESC'
            ejlmod3.printprogress('=', [[dep], [page+1, pages], [tocurl]])

            index_resp = session.get(tocurl)

            if index_resp.status_code != 200:
                print("Error: Can't open this index page! Skipping...")
                continue

            tocpage = BeautifulSoup(index_resp.content.decode('utf-8'), 'lxml')
            v = 0
            for rec in ejlmod3.getdspacerecs(tocpage, 'https://repositorio.ufscar.br', fakehdl=True):
                rec['doi'] = '20.2000/SAO-CARLOS-FEDERAL/' + re.sub('\D', '', rec['link'])
                if skipalreadyharvested and rec['doi'] in alreadyharvested:
                    print('   %s already in backup' % (rec['doi']))
                    continue
                else:
                    print("[{}] --> Harvesting data".format(rec.get('link') + '?show=full'))
                # Open the record page
                record_resp = session.get(rec.get('link') + '?show=full')

                if record_resp.status_code != 200:
                    print("[{}] --> ERROR: CAN'T OPEN PAGE! SKIPPING...".format(rec.get('link') + '?show=full'))
                    continue

                interesting_data = [
                    {'title': 'dc.contributor.author', 'type': 3, 'name': 'autaff'},
                    {'title': 'dc.date.issued', 'type': 1, 'name': 'date'},
                    {'title': 'dc.description.abstract', 'type': 1, 'name': 'abs'},
                    {'title': 'dc.subject', 'type': 2, 'name': 'keyw'},
                    {'title': 'dc.title', 'type': 1, 'name': 'tit'},
                    {'title': 'dc.title.alternative', 'type': 1, 'name': 'transtit'},
                    {'title': 'dc.contributor.advisor1', 'type': 3, 'name': 'supervisor'},
                    {'title': 'dc.language.iso', 'type' : 1, 'name' : 'language'},
                    {'title': 'dc.rights.uri', 'name': 'license', 'custom_handler': compute_license}
                ]

                dspace_table_data(rec, record_resp.content.decode('utf-8'), interesting_data, 'https://repositorio.ufscar.br')
                

                keepit = True
                for deg in rec['degrees']:
                    if re.search('Disserta%C3%A7%C3%A3o+%28Mestrado', deg):
                        keepit = False
                if keepit:
                    if fc: rec['fc'] = fc
                    rec['autaff'][-1].append(publisher)
                    recs.append(rec)
                sleep(5)
            #sleep(5)
            ejlmod3.writenewXML(recs, publisher, jnlfilename)

        sleep(5)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
