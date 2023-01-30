# -*- coding: utf-8 -*-
#harvest theses from Debrecen
#JH: 2023-01-01

from requests import Session
from time import sleep
from bs4 import BeautifulSoup
import ejlmod3

publisher = 'Debrecen U.'
pages = 1
rpp = 10

jnlfilename = 'THESES-DEBRECEN-%s' % ejlmod3.stampoftoday()
recs = []

def get_sub_site(url, site_session):
    print("[%s] --> Harvesting data" % url)
    try:
        site_rep = site_session.get(url)
    except:
        sleep(30)
        site_rep = site_session.get(url)

        if site_rep.status_code != 200:
            print("[%s] --> Error: Can't reach the site. Skipping..." % url)
            return
        

    rec: dict = {'tc': 'T', 'jnl': 'BOOK', 'autaff': [], 'supervisor': [], 'keyw': []}
    artpage = BeautifulSoup(site_rep.content.decode('utf-8'), 'lxml')
    ejlmod3.metatagcheck(rec, artpage, ['citation_language', 'citation_publication_date'])
    for row in artpage.find_all('tr'):
        cols = row.find_all('td')
        label = cols[0].text.strip()
        data = cols[1].text.strip()

        # Get the author
        if 'dc.contributor.author' == label:
            rec['autaff'].append([data])

        # Get the issued date
        if 'dc.date.issued' == label:
            if data.find('T') != -1:
                rec['date'] = data.split('T')[0]
            else:
                rec['date'] = data

        # Get the handle
        if 'dc.identifier.uri' == label:
            rec['hdl'] = data

        # Get the pages
        if 'dc.extent' == label:
            rec['pages'] = data

        # Get the supervisor
        if 'dc.contributor.advisor' == label:
            rec['supervisor'].append([data])

        # Get the language
        #if 'dc.language' == label:
        #    rec['language'] = data

        # Get the keywords
        if label in ['dc.subject.mab', 'dc.subject.mesh',
                     'dc.subject.sciencefield', 'dc.subject.discipline', 'dc.subject']:
            rec['keyw'].append(data)

        # Get the title
        if 'dc.title' == label:
            rec['tit'] = data

        # Get the abstract
        if 'dc.description.abstract' == label:
            rec['abs'] = data

        # Get the translated title
        if 'dc.title.translated' == label:
            rec['transtit'] = data

    # Get the pdf link
    pdf_links = BeautifulSoup(site_rep.content.decode('utf-8'), 'lxml').find_all('a', attrs={'class': 'dont-break-out'})
    if len(pdf_links) == 4:
        rec['hidden'] = 'https://dea.lib.unideb.hu%s' % pdf_links[2].get('href')

    recs.append(rec)



with Session() as session:
    for page in range(1, pages+1):
        for scope in ['8637a0a8-f516-4a9d-8972-b6bfbd04864b',
                      '81df8221-23ab-4c95-86a9-a44f7d1ed63d']:
            tocurl = 'https://dea.lib.unideb.hu/browse/dateissued?scope=' + scope + '&bbm.page={}&bbm.rpp={}&bbm.sd=DESC'.format(page, rpp)
            print(tocurl)

            index_resp = session.get(tocurl)
            if index_resp.status_code != 200:
                continue

            for article in BeautifulSoup(index_resp.content.decode('utf-8'), 'lxml').find_all('a', attrs={'class': 'item-list-title'}):
                get_sub_site('https://dea.lib.unideb.hu{}/full'.format(article.get('href')), session)
                sleep(3)
            sleep(3)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
