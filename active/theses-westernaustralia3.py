# -*- coding: utf-8 -*-
# Harvest theses from Western Australia
# JH: 2022-03-19

from time import sleep
from bs4 import BeautifulSoup
import os
import codecs
import ejlmod3
import re
import undetected_chromedriver as uc


pages = 1
skipalreadyharvested = True

publisher = 'Western Australia U.'
jnlfilename = 'THESES-WESTERN-AUSTRALIA-%s' % (ejlmod3.stampoftoday())

options = uc.ChromeOptions()
options.binary_location='/usr/bin/google-chrome'
options.binary_location='/usr/bin/chromium'
options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

recs = []


def get_sub_site(url):
    rec = {'link': url, 'tc': 'T', 'jnl': 'BOOK', 'autaff' : [], 'keyw' : [], 'supervisor' : []}
    if not ejlmod3.checkinterestingDOI(url):
        return
    elif skipalreadyharvested and '20.2000/WesternAustralia/'+re.sub('.*\/', '', url) in alreadyharvested:
        return
    print(url)
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    
    ejlmod3.metatagcheck(rec, soup, ['citation_keywords', 'citation_author',
                                     'citation_author_email', 'citation_author_orcid',
                                     'citation_publication_date', 'citation_pdf_url',
                                     'citation_title'])
    rec['autaff'][-1].append(publisher)


    # Get the abstract
    abstract_section = soup.find_all('div', attrs={'class': 'rendering_researchoutput_abstractportal'})
    if len(abstract_section) == 1:
        abstract = abstract_section[0].text
        rec['abs'] = abstract

    # Get properties
    properties_section = soup.find_all('table', attrs={'class': 'properties'})
    if len(properties_section) == 1:
        for prop in properties_section[0].find_all('tr'):
            title = prop.find_all('th')[0].text
            data = prop.find_all('td')[0]

            # Check if the theses is a P.h.D
            if title.find('Qualification') != -1:
                if data.text.find('Doctor of Philosophy') == -1:
                    ejlmod3.adduninterestingDOI(url)
                    return

            # Get the supervisors
            if title.find('Supervisors/Advisors') != -1:
                raw_supervisors = data.find_all('strong', attrs={'class': 'title'})
                supervisors = []
                for supervisor in raw_supervisors:
                    supervisors.append([supervisor.text])

                rec['supervisor'] = supervisors

            # Get the award date
            if title.find('Award date') != -1:
                rec['date'] = data.text.strip()
    if not 'date' in list(rec.keys()):
        try:
            rec['date'] = year
        except:
            print(url)

    # Get the DOI
    doi_section = soup.find_all('div', attrs={'doi'})
    if len(doi_section) == 1:
        doi_sub_section = doi_section[0].find_all('span')
        if len(doi_sub_section) == 1:
            doi = doi_sub_section[0].text
            rec['doi'] = doi
    if not 'doi' in list(rec.keys()):
        rec['doi'] = '20.2000/WesternAustralia/'+re.sub('.*\/', '', url)

    # Get the pdf link
    pdf_link_section = soup.find_all('a', attrs={'class': 'link document-link'})
    if len(pdf_link_section) == 1:
        if pdf_link_section[0].get('href') is not None:
            pdf_link = "https://research-repository.uwa.edu.au%s" % pdf_link_section[0].get('href')

            rec['hidden'] = pdf_link
    if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    sleep(5)


for page in range(pages):
    to_curl = 'https://research-repository.uwa.edu.au/en/publications/?type=%2Fdk%2Fatira%2Fpure%2Fresearchoutput' \
              '%2Fresearchoutputtypes%2Fthesis%2Fdoc&nofollow=true&organisationIds=3bece221-0399-4ae7-a111' \
              '-eecc4a1d60e1&organisationIds=a6413e77-1fd9-4a6e-beac-53cff1299a0f&organisationIds=564bce6b-6946-40f3' \
              '-a9c9-10c6ad7a1122&format=&page=' + str(page)
    print('==={ %i/%i }==={ %s }===' % (page+1, pages, to_curl))
    driver.get(to_curl)
    for h3 in BeautifulSoup(driver.page_source, 'lxml').find_all('h3', attrs={'class': 'title'}):
        article_link_box = h3.find_all('a', attrs={'class': 'link', 'rel': 'Thesis'})
        if len(article_link_box) == 1:
            if article_link_box[0].get('href') is not None:
                get_sub_site(article_link_box[0].get('href'))
    sleep(5)


ejlmod3.writenewXML(recs, publisher, jnlfilename)
driver.quit()
