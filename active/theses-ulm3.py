# -*- coding: utf-8 -*-
#harvest theses from Ulm
#JH: 2023-04-01

from bs4 import BeautifulSoup
from requests import Session
from time import sleep
import ejlmod3


rpp = 20
pages = 2
recs = []
publisher = 'Ulm U.'
jnlfilename = 'THESES-ULM-%s' % (ejlmod3.stampoftoday())

with Session() as session:
    for page in range(pages):
        tocurl = 'https://oparu.uni-ulm.de/xmlui/browse?rpp=' + str(rpp) + '&offset=' + str(rpp*page) + '&etal=-1&sort_by=2&type=resourcetype&value=Dissertation&order=DESC'
        print("--- OPENING PAGE {} OF {} ---".format(page+1, pages+1))
        page_resp = session.get(tocurl)

        if page_resp.status_code != 200:
            print("# Error: Can't reach site:", tocurl)
            continue

        recs += ejlmod3.getdspacerecs(BeautifulSoup(page_resp.content.decode('utf-8'), 'lxml'), 'https://oparu.uni-ulm.de', fakehdl=True)
        sleep(5)

    recs = recs[:2]
        
    for rec in recs:
        print("# Harvesting data -->", rec.get('link'))
        article_resp = session.get(rec.get('link'))

        if article_resp.status_code != 200:
            print("# Error: Can't reach site:", rec.get('link'))
            continue
        article_soup = BeautifulSoup(article_resp.content.decode('utf-8'), 'lxml')

        # Get the faculty
        faculty = article_soup.find_all('b', string='Fakultät')
        if len(faculty) == 1:
            row = faculty[0].parent.parent.parent
            cols = row.find_all('td')
            rec['note'] = ["Faculty: " + cols[1].text]

        # Get the institution
        institutions = article_soup.find_all('b', string='Institution')
        for institution in institutions:
            row = institution.parent.parent.parent
            cols = row.find_all('td')
            rec["note"].append("Institution: " + cols[1].text)
        
        ejlmod3.metatagcheck(rec, article_soup, ["DC.creator", "DCTERMS.issued", "DCTERMS.abstract", "DC.language", "DC.rights", "DC.subject", "DC.title", "citation_doi", "citation_pdf_url"])
        rec['autaff'][-1].append(publisher)
        ejlmod3.printrec(rec)
        sleep(5)
#        break

ejlmod3.writenewXML(recs, publisher, jnlfilename), retfilename='retfiles_special')
