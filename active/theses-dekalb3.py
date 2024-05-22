# -*- coding: utf-8 -*-
#program to harvest theses from NIU, DeKalb
# FS 2023-03-20

import re
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
from bs4 import BeautifulSoup
import ejlmod3
import os

publisher: str = 'NIU, DeKalb'
pages: int = 2
skipalreadyharvested = True
jnlfilename = 'THESES-NIUDeKalb-%s' % (ejlmod3.stampoftoday())
rpp: int = 10

reboring = re.compile('Thesis \((M.S.|Ed.D/)')
boring = ['Chemistry', 'Chemical engineering', 'Chemistry -- Computer simulation',
          'Chemistry, Physical and theoretical', 'Educational evaluation',
          'Educational psychology', 'Educational technology', 'Education, Higher',
          'Education, Secondary', 'Education', 'Higher education',
          'Hydrologic sciences', 'Hydrology', 'Instructional Design',
          'Instructional systems -- Design', 'Linguistics', 'Plate tectonics',
          'Special education', 'Translating and interpreting -- Study and teaching',
          'Translation studies']
# Init webdriver
options = uc.ChromeOptions()
options.add_argument('--headless')
options.binary_location='/usr/bin/chromium-browser'
options.binary_location='/usr/bin/google-chrome'
#options.binary_location='/usr/bin/chromium'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
#chromeversion = 108
driver = uc.Chrome(version_main=chromeversion, options=options)

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

recs = []

def get_sub_site(url):
    if ejlmod3.checkinterestingDOI(url):
        print("\n[{}] --> Harvesting data".format(url))
    else:
        #print("\n[{}] --> uninteresting".format(url))
        return
    
    keepit = True
    rec: dict = {'tc': 'T', 'jnl': 'BOOK', 'note' : []}

    driver.get(url)
    sleep(5)

    data_soup = BeautifulSoup(driver.page_source, 'lxml')
    #print(data_soup)
    titles = ['Title', 'Creator', 'Dissertation', 'Creation Date', 'Format', 'Description', 'Notes']
    # Get the title
    title_section = data_soup.find_all('span', string='Title')
    if len(title_section) == 1:
        rec['tit'] = title_section[0].parent.parent.text.split('\n')[0].split(' / ')[0]

    # Get the creator
    creator_section = data_soup.find_all('span', string='Creator')
    if len(creator_section) == 1:
        creator_section[0].parent.parent.find_all('div', attrs={'class': 'item-details-element item-details-element-multiple'})

    # Get the creation date
    date_section = data_soup.find_all('span', string='Creation Date')
    if len(date_section) == 1:
        rec['date'] = date_section[0].parent.parent.find_all('span')[1].text

    # Get the abstract
    abstract_section = data_soup.find_all('span', string='Description')
    if len(abstract_section) == 1:
        rec['abs'] = abstract_section[0].parent.parent.find_all('div', attrs={'class': 'item-details-element-container flex'})[0].text.split('\n')[0]

    # Extract the infos from the notes
    note_section = data_soup.find_all('span', string='Notes')
    if len(note_section) == 1:
        for line in note_section[0].parent.parent.find_all('div', attrs={'class': 'item-details-element-container flex'})[0].text.split('\n'):
            splitted_line = line.split(': ')
            title = ""
            data = ""
            advanced_data = ""
            if len(splitted_line) == 3:
                title, data, advanced_data = line.split(': ')
            if len(splitted_line) == 2:
                title, data = line.split(': ')

            if title == 'Committee members':
                rec['supervisor']: list = []
                for i in advanced_data.split('; '):
                    rec['supervisor'].append([i])

    # Get the author
    author_section = data_soup.find_all('span', string=re.compile("author\."))
    if len(author_section) != 0:
        author = author_section[0].text
        rec['autaff'] = [[author.replace(', author.', ''), publisher]]

    # Get the supervisor
    supervisor_section = data_soup.find_all('span', string=re.compile('supervisor\.'))
    if len(supervisor_section) != 0:
        supervisor = supervisor_section[0].text.replace(', degree supervisor.', '')
        rec['supervisor'] = [[supervisor]]

    # Get the pdf link
    pdf_section = data_soup.find_all('a', string='view full text')
    if len(pdf_section) == 1:
        rec['hidden'] = "https://i-share-niu.primo.exlibrisgroup.com" + pdf_section[0].get('href')

    for div in data_soup.find_all('div', attrs = {'class' : 'layout-block-xs'}):
        for span in div.find_all('span', attrs = {'class' : 'bold-text'}):
            spant = span.text.strip()
            break
        #ISBN
        if spant == 'Identifier':
            for a in div.find_all('a'):
                if a.has_attr('aria-label') and re.search('978\d+', a['aria-label']):
                    rec['isbn'] = a['aria-label']
        #pages
        elif spant == 'Format':
            if re.search('\d+ pages', div.text):
                rec['pages'] = re.sub('.*\D(\d\d+) pages.*', r'\1', div.text.strip())
        #Subject
        elif spant == 'Subject':
            for a in div.find_all('a'):
                if a.has_attr('aria-label'):
                    subject = a['aria-label']
                    if subject in ['Theoretical mathematics', 'Mathematics education',
                                   'Mathematics -- Study and teaching', 'Mathematics',
                                   'Applied mathematics']:
                        rec['fc'] = 'm'
                    elif subject in ['Condensed matter physics', 'Condensed matter']:
                        rec['fc'] = 'f'
                    elif subject in ['Computer science']:
                        rec['fc'] = 'c'
                    elif subject in ['Astrophysics']:
                        rec['fc'] = 'a'
                    elif subject in boring:
                        keepit = False
                    else:
                        rec['note'].append(a['aria-label'])
        #degree
        elif spant == 'Dissertation':
            for span in div.find_all('span', attrs = {'dir' : 'auto'}):
                st = span.text.strip()
                if reboring.search(st):
                    keepit = False
                else:
                    rec['note'].append(st)


    #permalink
    for link in data_soup.find_all('link', attrs = {'rel' : 'canonical'}):
        rec['link'] = link['href']
        rec['doi'] = re.sub('.*fulldisplay', '30.3000/NIUDeKalb', link['href'])

    if keepit:
        if ejlmod3.checkinterestingDOI(rec['doi']):
            if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
                ejlmod3.printrecsummary(rec)
                recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['doi'])
        ejlmod3.adduninterestingDOI(url)


for page in range(pages):
    to_curl: str = 'https://i-share-niu.primo.exlibrisgroup.com/discovery/search?query=any,contains,physics,OR&query=' \
                  'any,contains,mathematics,OR&query=any,contains,computing,OR&query=any,contains,informatics,OR&query=' \
                  'any,contains,quantum,AND&pfilter=rtype,exact,dissertations,AND&pfilter=dr_s,exact,20180101,AND&pfilter=' \
                  'dr_e,exact,99991231,AND&tab=LibraryCatalog&search_scope=MyInstitution&sortby=date_d&vid=01CARLI_NIU:FML_DE' \
                  'FAULT&mode=advanced&offset=' + str(rpp*page)

    driver.get(to_curl)
    sleep(5)
    ejlmod3.printprogress('=', [[page+1, pages], [to_curl], [len(recs)]])
    index_soup = BeautifulSoup(driver.page_source, 'lxml')

    for article_link in index_soup.find_all('a', attrs={'class': 'md-primoExplore-theme'}):
        if article_link.parent.get('class') == ['item-title']:
            get_sub_site(article_link.get('href'))
            sleep(5)


ejlmod3.writenewXML(recs, publisher, jnlfilename)
