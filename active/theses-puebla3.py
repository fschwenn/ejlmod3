# -*- coding: utf-8 -*-
#harvest theses from Puebla U.
#JH: 2022-06-07
#FS: 2022-09-04


import getopt
import sys
import os
import codecs
import re
import datetime
import ejlmod3
import undetected_chromedriver as uc
#from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep

# Initiate webdriver
#driver = webdriver.PhantomJS()
options = uc.ChromeOptions()
options.headless=True
options.binary_location='/usr/bin/google-chrome'
options.binary_location='/usr/bin/chromium'
options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)


publisher = 'Puebla U., Inst. Fis.'
jnlfilename = 'THESES-PUEBLA-%s' % (ejlmod3.stampoftoday())

recs = []

rpp = 50
pages = 2
skipalreadyharvested = True

boring = ['Facultad de Ciencias Químicas', 'Área de Ciencias Sociales y Humanidades',
          'Área Económico Administrativa', 'Área de Ciencias Sociales',
          'Área de Educación y Humanidades']
boring += ['Facultad de Economía', 'Facultad de Derecho y Ciencias Sociales',
           'Facultad de Arquitectura', 'Instituto de Fisiología',
           'nstituto de Ciencias de Gobierno y Desarrollo Estratégico<',
           'Facultad de Filosofía y Letras']

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
                                                   
def get_sub_site(url):
    keepit = True
    print('[%s] --> Harversting Data' % url)
    driver.get(url)

    rec = {'tc': 'T', 'jnl': 'BOOK', 'supervisor': [], 'autaff': [], 'keyw': [], 'link' : url, 'note' : []}

    artpage = BeautifulSoup(driver.page_source, 'lxml')
    ejlmod3.metatagcheck(rec, artpage, ['DC.rights', 'DC.subject', 'citation_title', 'citation_language',
                                        'citation_date', 'DC.identifier', 'DCTERMS.abstract',
                                        'citation_title', 'citation_pdf_url'])

    rows = artpage.find_all('tr', attrs={'class': 'ds-table-row'})
    for row in rows:
        columns = row.find_all('td')
        label = columns[0].text
        data = columns[1].text

        # Get the supervisor
        if label == 'dc.contributor.advisor':
            rec['supervisor'].append([data.split(';')[0]])

        # Get the author
        elif label == 'dc.contributor.author':
            rec['autaff'].append([data, publisher])

        # Check if it is really a PhD
        elif label == 'dc.type.degree':
            if data != 'Doctorado':
                keepit = False

        #department
        elif label in ['dc.thesis.degreegrantor', 'dc.thesis.degreediscipline']:
            if data in boring:
                keepit = False
            else:
                rec['note'].append(label+': '+data)

    if keepit:
        if not skipalreadyharvested or not 'hdl' in rec or not rec['hdl'] in alreadyharvested:
            recs.append(rec)
            ejlmod3.printrecsummary(rec)
    else:
        ejlmod3.adduninterestingDOI(url)
    return

for page in range(pages):
    to_curl = 'https://repositorioinstitucional.buap.mx/handle/20.500.12371/7/discover?rpp=' + str(rpp) + '&etal=0' \
                                                                                                          '&group_by' \
                                                                                                          '=none&page='\
              + str(page+1) + '&sort_by=dc.date.issued_dt&order=desc '
    ejlmod3.printprogress("=", [[page+1, pages], [to_curl]])
    driver.get(to_curl)
    for article in BeautifulSoup(driver.page_source, 'lxml').find_all('div', attrs={'class': 'col-sm-9 '
                                                                                             'artifact-description'}):
        article_link = article.find_all('a')
        if len(article_link) == 1:
            url = 'https://repositorioinstitucional.buap.mx%s?show=all' % article_link[0].get('href')
            if ejlmod3.checkinterestingDOI(url):
                get_sub_site(url)
                sleep(4)
            else:
                print('[%s] --> is uninteresting' % url)
    sleep(10)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
