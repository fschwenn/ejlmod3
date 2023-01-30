# -*- coding: utf-8 -*-
#harvest theses from Colorado School of Mines
#JH: 2023-01-23

from bs4 import BeautifulSoup
from requests import Session
from urllib.parse import parse_qs
from time import sleep
import ejlmod3

def dspace_extract_links(content: str):
    soup = BeautifulSoup(content, 'lxml')
    artifacts: list = soup.find_all('div', attrs={'class': 'description-content'})
    out: list = []

    for artifact in artifacts:
        out.append('https://repository.mines.edu' + artifact.find_all('a')[0].get('href') + '?show=full')
    return out

publisher = 'Colorado School of Mines'
rpp = 100
pages = 1
recs = []
boring = ['Mining Engineering', 'Metallurgical and Materials Engineering',
          'Chemical and Biological Engineering', 'Civil and Environmental Engineering',
          'Economics and Business', 'Geology and Geological Engineering', 'Geophysics',
          'Mechanical Engineering', 'Chemistry', 'Petroleum Engineering',
          'Electrical Engineering', 'Chemistry and Geochemistry',
          'Chemical Engineering and Petroleum Refining', 'Chemical Engineering',
          'Engineering', 'Environmental Science and Engineering',
          'Geology, Geological Engineering', 'Geology', 'Interdisciplinary Program',
          'Liberal Arts and International Studies', 'Materials Science',
          'Mining and Earth Systems Engineering']
jnlfilename = 'THESES-COLORADOMINES-%s' % (ejlmod3.stampoftoday())

i = 0
with Session() as session:
    for page in range(pages):
        print("#### OPEN PAGE %i/%i ####" % (page+1, pages))
        to_curl = 'https://repository.mines.edu/handle/11124/7/browse?view=list&rpp=' + str(rpp) + '&offset=' + str(rpp*page) + '&etal=-1&sort_by=2&type=dateissued&order=DESC'
        ejlmod3.printprogress('=', [[page+1, pages], [to_curl]])
        index_resp = session.get(to_curl)

        if index_resp.status_code != 200:
            print("Error: Can't open page %i" % (page+1))
            continue

        soup = BeautifulSoup(index_resp.content.decode('utf-8'), 'lxml')
        links = dspace_extract_links(index_resp.content.decode('utf-8'))


        for link in links:
            i += 1
            ejlmod3.printprogress('-', [[page+1, pages], [i], [link], [len(recs)]])
            jump = False
            rec: dict = {'tc': 'T', 'jnl': 'BOOK', 'supervisor': [], 'autaff': [], 'link': link, 'note' : []}
            if not ejlmod3.checkinterestingDOI(link):
#                print("   already identified as uninteresting")
                continue

            data_resp = session.get(link)

            if data_resp.status_code != 200:
                print("[%s] --> Error: Can't open the site" % link)
                continue

            data_soup = BeautifulSoup(data_resp.content.decode('utf-8'), 'lxml')

            ejlmod3.metatagcheck(rec, data_soup, ['DC.creator', 'DCTERMS.issued', 'DCTERMS.abstract', 'DC.subject', 'DC.title', 'DC.contributor'])
            rec['autaff'][-1].append(publisher)

            for row in data_soup.find_all('tr', attrs={'class': 'ds-table-row'}):
                cols = row.find_all('td')

                title = cols[0].text
                data = cols[1].text

                # Get the handle
                if title == 'dc.identifier.uri':
                    rec['hdl'] = data.replace('	https://hdl.handle.net/', '')

                # Get the degree
                if title == 'thesis.degree.level':
                    if data != 'Doctoral':
                        jump = True

                #topic
                if title == 'thesis.degree.discipline':
                    if data in boring:
                        jump = True
                    elif data == 'Computer Science':
                        rec['fc'] = 'c'
                    elif data == 'Applied Mathematics and Statistics':
                        rec['fc'] = 'm'
                    elif data != 'Physics':
                        rec['note'].append('thesis.degree.discipline:::' + data)

            # Get the pdf link
            pdf_link = data_soup.find_all('a', attrs={'class': 'file-download-button'})
            if len(pdf_link) == 1:
                params = parse_qs('https://e-archivo.uc3m.es' + pdf_link[0].get('href'))

                if len(params.get('isAllowed')) == 1:
                    if params.get('isAllowed')[0] == 'y':
                        rec['hidden'] = 'https://e-archivo.uc3m.es' + pdf_link[0].get('href')

            sleep(10)
            if jump:
                ejlmod3.adduninterestingDOI(link)
            else:
                recs.append(rec)
                ejlmod3.printrecsummary(rec)
        sleep(5)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
