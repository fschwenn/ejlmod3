# -*- coding: utf-8 -*-
# program to harvest theses from University South Dakota
# JH 2020-02-05

from requests import Session
from bs4 import BeautifulSoup
from time import sleep
import re
import ejlmod3


jnlfilename = 'THESES-SOUTHDAKOTA-%s' % (ejlmod3.stampoftoday())
publisher = 'South Dakota U.'
recs = []
boring = ['Basic Biomedical Science', 'Biology', 'Biomedical Engineering',
          'Chemistry', 'Counseling and Human Services', 'Curriculum & Instruction',
          'Educational Leadership', 'Education', 'English', 'Health Science',
          'Political Science', 'Psychology', 'School Psychology']

def get_sub_site(url, sess):
    print("[{}] --> Harvesting data".format(url))

    rec: dict = {'tc': 'T', 'jnl': 'BOOK', 'link': url, 'note' : []}

    data_resp = sess.get(url)

    if data_resp.status_code != 200:
        print("[{}] --> Error: Can't open the site. Skipping...".format(url))
        return

    data_soup = BeautifulSoup(data_resp.content.decode('utf-8'), 'lxml')

    ejlmod3.metatagcheck(rec, data_soup, ['og:title', 'bepress_citation_author', 'og:description', 'bepress_citation_date', 'bepress_citation_pdf_url'])

    # Get the supervisor
    supervisor = data_soup.find_all('div', attrs={'id': re.compile('advisor')})
    if len(supervisor) != 0:
        rec['supervisor'] = []
        for i in supervisor:
            rec['supervisor'].append([i.find_all('p')[0].text])

    # Get the number of pages
    pages = data_soup.find_all('div', attrs={'id': re.compile('numberofpages')})
    if len(pages) == 1:
        rec['pages'] = pages[0].find_all('p')[0].text

    # Get the pdf link
    pdf = data_soup.find_all('a', attrs={'id': 'pdf'})
    if len(pdf) == 1:
        rec['hidden'] = pdf[0].get('href')

    #department
    for div in data_soup.find_all('div', attrs={'id': 'department'}):
        for p in div.find_all('p'):
            department = p.text.strip()
            if department in boring:
                ejlmod3.adduninterestingDOI(url)
                print("[{}] --> Skipping because '%s' is boring".format(url) % (department))
                return
            elif department != 'Physics':
                rec['note'].append(department)
    # Check if really PhD
    phd = data_soup.find_all('div', attrs={'id': 'degree_name'})
    if len(phd) == 1:
        if phd[0].text.find('PhD') == -1 and phd[0].text.find('EdD') == -1:
            print("[{}] --> Skipping because no PhD!".format(url))
            ejlmod3.adduninterestingDOI(url)
            return
    else:
        print("[{}] --> Skipping because no PhD!".format(url))
        return
    ejlmod3.printrecsummary(rec)
    recs.append(rec)


with Session() as session:
    index_url = "https://red.library.usd.edu/diss-thesis/"

    index_resp = session.get(index_url)

    if index_resp.status_code != 200:
        print("Error: Can't reach this site!")
        exit(0)
    v = 0
    for link in BeautifulSoup(index_resp.content.decode('utf-8'), 'lxml').find_all('a'):
        if link.parent.get('class') == ['article-listing']:
            if ejlmod3.checkinterestingDOI(link.get('href')):
                get_sub_site(link.get('href'), session)
                sleep(5)
                v += 1
#        if v == 5:
#            break

ejlmod3.writenewXML(recs, publisher, jnlfilename)
