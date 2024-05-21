# -*- coding: utf-8 -*-
#harvest theses from Leuven U.
#FS: 2020-12-22
#FS: 2023-04-03

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import json
import undetected_chromedriver as uc

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

publisher = 'Leuven U.'
jnlfilename = 'THESES-LEUVEN-%s' % (ejlmod3.stampoftoday())
skipalreadyharvested = True
pages = 15

prerecs = []

if skipalreadyharvested:    
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

options = uc.ChromeOptions()
options.binary_location='/usr/bin/google-chrome'
#options.binary_location='/usr/bin/chromium'
options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

driver.implicitly_wait(120)
driver.set_page_load_timeout(30)
for page in range(pages):
    tocurl = 'https://limo.libis.be/primo-explore/search?query=any,contains,lirias,AND&tab=default_tab&search_scope=Lirias&sortby=date&vid=Lirias&facet=local16,include,thesis-dissertation&lang=en_US&mode=advanced&offset=' + str(10*page)
    tocurl = 'https://kuleuven.limo.libis.be/discovery/search?query=any,contains,lirias&tab=LIRIAS&lang=en_US&sortby=date_d&search_scope=lirias_profile&vid=32KUL_KUL:Lirias&facet=lds07,include,thesis-dissertation&offset=' + str(10*page)
    ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
    driver.get(tocurl)
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, 'result-item-text')))
    tocpage = BeautifulSoup(driver.page_source, features="lxml")
    time.sleep(10)
    for div in tocpage.find_all('div', attrs = {'class' : 'result-item-text'}):
        for a in div.find_all('a', attrs = {'class' : 'md-primoExplore-theme'}):
            rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'supervisor' : [], 'oa' : False}
            liriasnr = a['data-emailref']
            rec['doi'] = '20.2000/Leuven/' + liriasnr.upper()
            rec['link'] = 'https://limo.libis.be/primo-explore/fulldisplay?docid=' + liriasnr + '&context=L&vid=Lirias&search_scope=Lirias&tab=default_tab&lang=en_US'
            rec['link'] = 'https://kuleuven.limo.libis.be/discovery/fulldisplay?docid=' + liriasnr + '&context=SearchWebhook&vid=32KUL_KUL:Lirias&search_scope=lirias_profile&tab=LIRIAS&adaptor=SearchWebhook&lang=en'
            if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
                for span in div.find_all('span', attrs = {'class' : 'availability-status'}):
                    if not re.search('No Online Access', span.text):


                        if not rec['doi'] in ['20.2000/Leuven/LIRIAS4073431', '20.2000/Leuven/LIRIAS4073432', '20.2000/Leuven/LIRIAS4072482', '20.2000/Leuven/LIRIAS4067150', '20.2000/Leuven/LIRIAS4067434', '20.2000/Leuven/LIRIAS3978592', '20.2000/Leuven/LIRIAS3965037', '20.2000/Leuven/LIRIAS3965444', '20.2000/Leuven/LIRIAS3949606', '20.2000/Leuven/LIRIAS3954780', '20.2000/Leuven/LIRIAS3790435', '20.2000/Leuven/LIRIAS3441955', '20.2000/Leuven/LIRIAS3832851', '20.2000/Leuven/LIRIAS3790347', '20.2000/Leuven/LIRIAS3828016', '20.2000/Leuven/LIRIAS3790558', '20.2000/Leuven/LIRIAS3791842', '20.2000/Leuven/LIRIAS3790351', '20.2000/Leuven/LIRIAS3777184', '20.2000/Leuven/LIRIAS3778268', '20.2000/Leuven/LIRIAS3779747', '20.2000/Leuven/LIRIAS3764528', '20.2000/Leuven/LIRIAS3748340', '20.2000/Leuven/LIRIAS3762707', '20.2000/Leuven/LIRIAS3750263', '20.2000/Leuven/LIRIAS3761708', '20.2000/Leuven/LIRIAS3762449', '20.2000/Leuven/LIRIAS3764521', '20.2000/Leuven/LIRIAS3751393', '20.2000/Leuven/LIRIAS3759423', '20.2000/Leuven/LIRIAS3759421', '20.2000/Leuven/LIRIAS3762645', '20.2000/Leuven/LIRIAS3743600', '20.2000/Leuven/LIRIAS3745983', '20.2000/Leuven/LIRIAS3746898', '20.2000/Leuven/LIRIAS3759452', '20.2000/Leuven/LIRIAS3752939']:
                            prerecs.append(rec)
    print('  %4i records so far' % (len(prerecs)))

i = 0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        driver.get(rec['link'])
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, 'item-detail')))
        artpage = BeautifulSoup(driver.page_source, features="lxml")
        time.sleep(10)
    except:
        try:
            driver.get(rec['link'])
            WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, 'item-detail')))
            artpage = BeautifulSoup(driver.page_source, features="lxml")
            time.sleep(20)        
        except:
            print('  could not load page')
            continue
    #abstract
    ejlmod3.metatagcheck(rec, artpage, ['description'])
    #title
    for span in artpage.find_all('span', attrs = {'data-field-selector' : '::title'}):
        for span2 in span.find_all('span', attrs = {'dir' : 'auto'}):
            rec['tit'] = span2.text.strip()
    #author
    for span in artpage.find_all('span', attrs = {'data-field-selector' : 'creator'}):
        for span2 in span.find_all('span', attrs = {'dir' : 'auto'}):
            rec['autaff'] = [[ span2.text.strip(), publisher ]]
    #supervisor
    for span in artpage.find_all('span', attrs = {'data-field-selector' : 'contributor'}):
        for span2 in span.find_all('span', attrs = {'dir' : 'auto'}):
            svs = re.sub('\(.*?\)', '', span2.text.strip())
            for sv in re.split(' *; *', svs):
                rec['supervisor'].append([sv])
    #date
    for span in artpage.find_all('span', attrs = {'data-field-selector' : 'creationdate'}):
        for span2 in span.find_all('span', attrs = {'dir' : 'auto'}):
            rec['date'] = span2.text.strip()
    #open access
    for div in artpage.find_all('div', attrs = {'class' : 'open-access-mark'}):
        for svg in div.find_all('svg', attrs = {'id' : 'open-access_cache14'}):
            rec['oa'] = True
    #fulltext
    for a in artpage.find_all('a', attrs = {'class' : 'arrow-link'}):
        if re.search('\.pdf', a.text):
            if rec['oa']:
                rec['FFT'] = a['href']
            else:
                rec['hidden'] = a['href']
    ejlmod3.printrecsummary(rec)
    recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
