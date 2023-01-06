# -*- coding: utf-8 -*-
#harvest theses Patras U.
#FS: 2022-10-30

import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from time import sleep
import ejlmod3
import os
import re

publisher = 'Patras U.'
jnlfilename = 'THESES-PATRAS-%s' % (ejlmod3.stampoftoday())

rpp = 100
pages = 3
years = 2

# Initialize webdriver

options = uc.ChromeOptions()
options.headless=True
options.binary_location='/usr/bin/chromium-browser'
options.add_argument('--headless')
driver = uc.Chrome(version_main=103, options=options)

departments = [('92cf5d27-5f6e-4960-802b-c6e5ad6802c6', ''),
               ('f07587d0-4696-4a7d-b2d4-c9035d9e6896', 'm'),
               ('0cd5ea47-d5bc-4fd4-adee-5e1d548e315c', 'c')]

prerecs = []
i = 0 
ids = []
for (dep, fc) in departments:
    for page in range(1, pages+1):
        tocurl = 'https://nemertes.library.upatras.gr/browse/dateissued?scope=' + dep + '&bbm.page=' + str(page) + '&bbm.rpp=' + str(rpp) + '&bbm.sd=DESC'
        ejlmod3.printprogress('=', [[i*pages+page, len(departments)*pages], [tocurl]])
        driver.get(tocurl)
        tocpage = BeautifulSoup(driver.page_source, 'lxml')
        for script in tocpage.find_all('script'):
            scriptt = script.text
            for part in re.split('https...nemertes.library.upatras.gr.server.api.core.items.', scriptt):
                identifier = re.sub('(\/|\&|\{|q;\}).*', '', part)
                if identifier and not identifier in ids:
                    if not ' ' in identifier:
                        ids.append(identifier)
                        rec = {'tc' : 'T', 'jnl' : 'BOOK'}
                        rec['artlink'] = 'https://nemertes.library.upatras.gr/items/' + identifier
                        if fc: rec['fc'] = fc
                        if ejlmod3.checkinterestingDOI(rec['artlink']):
                            prerecs.append(rec)
        print('   %3i records so far' % (len(prerecs)))
        sleep(5)
    i += 1


recs = []
for (i, rec) in enumerate(prerecs):
    ejlmod3.printprogress('-', [[i+1, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        driver.get(rec['artlink'])
        artpage = BeautifulSoup(driver.page_source, 'lxml')
        ejlmod3.metatagcheck(rec, artpage, ['description', 'citation_title', 'citation_author',
                                            'citation_publication_date', 'citation_language',
                                            'citation_keywords', 'citation_pdf_url'])
        rec['autaff'][-1].append(publisher)
    except:
        print('\n   wait 3 minutes\n')
        sleep(180)
        driver.get(rec['artlink'])
        artpage = BeautifulSoup(driver.page_source, 'lxml')
        ejlmod3.metatagcheck(rec, artpage, ['description', 'citation_title', 'citation_author',
                                            'citation_publication_date', 'citation_language',
                                            'citation_keywords', 'citation_pdf_url'])
        rec['autaff'][-1].append(publisher)
    #get HDL from URL
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'citation_abstract_html_url'}):
        if re.search('handle.net', meta['content']):
            rec['hdl'] = re.sub('.*net\/', '', meta['content'])
    #fix link to fulltext
    if 'pdf_url' in rec:
        rec['pdf_url'] = re.sub('.*:4000', 'https://nemertes.library.upatras.gr', rec['pdf_url'])
    #check age of thesis
    rec['year'] = re.sub('.*([12]\d\d\d).*', r'\1', rec['date'])
    if int(rec['year']) <= ejlmod3.year(backwards=years):
        #not really uninteresting but too old
        ejlmod3.adduninterestingDOI(rec['artlink'])
    else:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    sleep(5)
        
ejlmod3.writenewXML(recs, publisher, jnlfilename)
driver.quit()
