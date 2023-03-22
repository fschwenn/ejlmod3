# -*- coding: utf-8 -*-
#program to harvest theses from Utah State U.
# FS 2023-03-20

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from bs4 import BeautifulSoup
import ejlmod3
import re
import os


publisher = 'Utah State U.'
jnlfilename = 'THESES-UTAHSTATE-%s' % (ejlmod3.stampoftoday())
rpp = 25
pages = 1000
skipalreadyharvested = True

startyear = ejlmod3.year(backwards=1)
stopyear = ejlmod3.year()
boring = ['Master of Science (MS)']
boring += ['Special Education and Rehabilitation Counseling', 'Psychology', 'Biology', 'Applied Sciences, Technology, and Education', 'Animal, Dairy, and Veterinary Sciences', 'Civil and Environmental Engineering', 'Wildland Resources']

# Initiate webdriver
options = uc.ChromeOptions()
options.add_argument('--headless')
#options.binary_location='/usr/bin/google-chrome'
options.binary_location='/usr/bin/chromium'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

recs = []
complete = False
for page in range(pages):
    tocurl = 'https://digitalcommons.usu.edu/do/search/?q=document_type%3Athesis&start=' + str(rpp*page) + '&start_date=' + str(startyear) + '-01-01&end_date=' + str(stopyear) + '-12-31&context=656526&sort=date_desc&facet=#query-results'
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    if page == 0:
        driver.get(tocurl)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'title')))
        sleep(1)
        xp = '//a[@aria-label="dismiss cookie message"]'
        driver.find_element(by=By.XPATH, value=xp).click()
    else:
        try:
            for a in page_soup.find_all('a', attrs = {'id' : 'next-page'}):
                print(a)
            sleep(3)
            xp = '//a[@id="next-page"]'
            driver.find_element(by=By.XPATH, value=xp).click()
            sleep(3)
        except:
            complete = True
    if complete:
        break

    page_soup = BeautifulSoup(driver.page_source, 'lxml')


    for article in page_soup.find_all('span', attrs={'class': 'title'}):
        keepit = True
        article_link = article.find_all('a')

        if len(article_link) != 1:
            continue
        rec = {'tc': 'T', 'jnl': 'BOOK', 'note': []}
        rec['artlink'] = article_link[0].get('href')
        if ejlmod3.checkinterestingDOI(rec['artlink']):
            print("[{}] --> uninteresting".format(rec['artlink']))
            continue
        else:
            print("[{}] --> Harvesting data".format(rec['artlink']))

        driver.get(rec['artlink'])

        article_soup = BeautifulSoup(driver.page_source, 'lxml')
        ejlmod3.metatagcheck(rec, article_soup, ['bepress_citation_author',
           'bepress_citation_title', 'bepress_citation_date', 'keywords', 'keywords', 'description'])

        # Get the degree
        degree_section = article_soup.find_all('div', attrs={'id': 'degree_name'})
        if len(degree_section) == 1:
            if degree_section[0].find_all('p')[0].text in boring:
                print("[{}] --> Skipping because of boring degree".format(article_link[0].get('href')))
                keepit = False
            else:
                rec['note'].append(degree_section[0].find_all('p')[0].text)

        # Get the department
        department_section = article_soup.find_all('div', attrs={'id': 'department'})
        if len(department_section) == 1:
            if department_section[0].find_all('p')[0].text in boring:
                print("[{}] --> Skipping because of boring department".format(article_link[0].get('href')))
                keepit = False
            else:
                rec['note'].append(department_section[0].find_all('p')[0].text)

        # Get the committee
        committee_section = article_soup.find_all('div', attrs={'id': 'committee_chair'})
        if len(committee_section) == 1:
            rec['supervisor'] = [[committee_section[0].find_all('p')[0].text]]

        # Get the DOI
        doi_section = article_soup.find_all('div', attrs={'id': 'doi'})
        if len(doi_section) == 1:
            doi_link = doi_section[0].find_all('a')[0].text

            rec['doi'] = doi_link.replace('https://doi.org/', '')

        # Get the PDF link
        pdf_link = article_soup.find_all('a', attrs={'id': 'pdf', 'class': 'btn'})
        if len(pdf_link) == 1:
            rec['hidden'] = pdf_link[0].get('href')

        if keepit:
            if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
                recs.append(rec)
                ejlmod3.printrecsummary(rec)
        else:
            ejlmod3.adduninterestingDOI(rec['doi'])

        sleep(5)
    print('  %4i records so far' % (len(recs)))
    sleep(5)

driver.close()

ejlmod3.writenewXML(recs, publisher, jnlfilename)
