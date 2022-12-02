# -*- coding: utf-8 -*-
#harvest theses from Minho U.
#JH: 2022-11-15

from bs4 import BeautifulSoup
from requests import Session
from time import sleep
import ejlmod3
import urllib3
import re

urllib3.disable_warnings()

publisher = 'Minho U.'
rpp = 50
pages = 4

reboring = re.compile('(Administração|Ambiental|Arqueologia|Arquitectura|Biologia|Biológica|Biological|Biológicas|Biology|Biomédica|Biomédicas|Celular|Células|Chemical|Civil|Clínica|Criança|Cultura|Curricular|Design|Educação|Educativa|Empresariais|Ensino|Escolar|Especial|Especialidade|Estratégica|Filosofia|Geografia|Geologia|Gestão|História|Humana|Infância|Infantil|Jurídicas|Lazer|Líderes|Linguagem|Linguística|Literatura|Marketing|Medicina|Molecular|Planeamento|Polímeros|Política|Políticas|Psicologia|Públicas|Química|Recreação|Regenerativa|Regional|Saúde|Social|Sociedade|Sociologia|Têxtil)')
refcc = re.compile('(Computer Science|Informática|Informatics)')
refcm = re.compile('(Matemática|Mathematics)')
refcq = re.compile('Física')

recs = []

def get_sub_site(url, session_var):
    if ejlmod3.ckeckinterestingDOI(url):
        print('[%s] --> Harvesting data' % url)
    else:
        return
    rec = {'tc': 'T', 'autaff': [], 'license': {}, 'keyw': [], 'link': url, 'jnl': 'BOOK', 'supervisor' : []}

    site_resp = session_var.get(url, verify=False)

    if site_resp.status_code != 200:
        print('[%s] --> Error: Can\'t open page')
        return

    artpage = BeautifulSoup(site_resp.content.decode('utf-8'), 'lxml')
    ejlmod3.metatagcheck(rec, artpage, ['DC.date', 'DCTERMS.abstract', 'DC.subject', 'DC.title', 'citation_date',
                                        'DC.language', 'DC.rights', 'DC.title', #'DC.creator', 'DC.contributor',
                                        'citation_pdf_url', 'DC.identifier', 'citation_keywords', 'DCTERMS.issued'])
    sleep(5)

    for td in artpage.find_all('td', attrs={'class': 'metadataFieldValue dc_description'}):
        description = td.text.strip()
        if refcq.search(description):
            pass
        elif refcc.search(description):
            rec['fc'] = 'c'
        elif refcm.search(description):
            rec['fc'] = 'm'            
        elif reboring.search(description):
            ejlmod3.adduninterestingDOI(url)
            return
        else:
            rec['note'] = [description]
    #ORCIDS are only in body
    for tr in artpage.body.find_all('tr'):
        for td in tr.find_all('td', attrs = {'class' : 'dc_contributor_advisor'}):
            if 'metadataFieldValue' in td['class']:
                for a in td.find_all('a'):
                    if a.has_attr('href') and re.search('orcid.org', a['href']):
                        orcid = re.sub('.*org\/', 'ORCID:', a['href'])
                        a.replace_with(';'+orcid)
                for br in td.find_all('br'):
                    br.replace_with('ZZZ')
                for advisor in re.split('ZZZ', td.text.strip()):
                    parts = re.split(' *;', advisor)
                    rec['supervisor'].append(parts)
        for td in tr.find_all('td', attrs = {'class' : 'dc_contributor_author'}):
            if 'metadataFieldValue' in td['class']:
                for a in td.find_all('a'):
                    if a.has_attr('href') and re.search('orcid.org', a['href']):
                        orcid = re.sub('.*org\/', 'ORCID:', a['href'])
                        a.replace_with(';'+orcid)
                rec['autaff'] = [re.split(' *;', td.text.strip()) ]
                rec['autaff'][0].append(publisher)
    # Get the pdf link if not in metatags
    if 'hidden' in rec.keys() or 'FFT' in rec.keys():
        links = artpage.find_all('a')

        for link in links:
            if link.get('href').find('/bitstream/') != -1:
                rec['FFT'] = 'https://repositorium.sdum.uminho.pt' + link.get('href')
    ejlmod3.printrecsummary(rec)
    recs.append(rec)
    return

for page in range(pages):
    print('==== OPEN PAGE %i/%i ====' % (page+1, pages))
    to_curl = 'https://repositorium.sdum.uminho.pt/handle/1822/3/browse?type=dateissued&sort_by=2&order=DESC&rpp=%s' \
              '&etal=3&null=&offset=%s' % (rpp, rpp*page)
    with Session() as session:
        resp = session.get(to_curl, verify=False)

        if resp.status_code != 200:
            print("[%s] --> Error: Can't open page!" % to_curl)
            continue

    sleep(10)
    for link in BeautifulSoup(resp.content.decode('utf-8'), 'lxml').find_all('a'):
        if link.get('href') is not None:
            if link.get('href').find('handle') != -1 and len(link.get('href')) <= 20:
                get_sub_site('https://repositorium.sdum.uminho.pt{}'.format(link.get('href')), session)

jnlfilename = 'THESES-MINHO-%s' % (ejlmod3.stampoftoday())

ejlmod3.writenewXML(recs, publisher, jnlfilename)
