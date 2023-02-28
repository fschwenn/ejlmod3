# -*- coding: utf-8 -*-
#harvest thesis from Clemson U.
#FS: 2022-11-10

from requests import Session
from bs4 import BeautifulSoup
from time import sleep
import ejlmod3


publisher = 'Clemson U.'
pages = 4
years = 2
jnlfilename = 'THESES-CLEMSON-%s' % (ejlmod3.stampoftoday())

recs: list = []

def get_sub_site(url, sess):
    print("[{}] --> Harvesting data".format(url))

    rec: dict = {'tc': 'T', 'jnl': 'BOOK'}

    record_resp = sess.get(url)

    if record_resp.status_code != 200:
        print("[{}] --> Error: Can't reacht this site! Skipping...")
        return

    soup = BeautifulSoup(record_resp.content.decode('utf-8'), 'lxml')

    # Metatagcheck
    ejlmod3.metatagcheck(rec, soup, ['bepress_citation_author', 'bepress_citation_title', 'bepress_citation_pdf_url', 'bepress_citation_date', 'description'])

    # Get the committee members
    advisor_section = soup.find_all('div', attrs={'id': 'advisor1'})
    if len(advisor_section) == 1:
        rec['supervisor'] = [[advisor_section[0].find_all('p')[0].text]]

    # Get the pdf link
    pdf_link = soup.find_all('a', attrs={'id': 'pdf'})
    if len(pdf_link) == 1:
        rec['hidden'] = pdf_link[0].get('href')

    recs.append(rec)

with Session() as session:
    index_url = "https://tigerprints.clemson.edu/all_dissertations/index.html"

    index = session.get(index_url)

    if index.status_code != 200:
        print("Error: Can't open the index page")
        exit(0)

    for article in BeautifulSoup(index.content.decode('utf-8'), 'lxml').find_all('p', attrs={'class': 'article-listing'}):
        link = article.find_all('a')

        if len(link) == 1:
            get_sub_site(link[0].get('href'), session)
            sleep(5)


ejlmod3.writenewXML(recs, publisher, jnlfilename)
