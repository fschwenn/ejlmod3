# -*- coding: utf-8 -*-
#harvest theses from Waseda
#JH: 2019-04-03

from bs4 import BeautifulSoup
from requests import Session
from time import sleep
import ejlmod3
import re
import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


publisher = 'Waseda U.'
recs = []
years = 2
rpp = 100
skipalreadyharvested = True
jnlfilename = 'THESES-WASEDA-%s' % (ejlmod3.stampoftoday())
deps = [('Advanced Science and Engineering', '338'),
        ('Creative Science and Engineering', '341'),
        ('Fundamental Science and Engineering', '347')]


if skipalreadyharvested:    
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

searchstrings = {}
for (dep, q) in deps:
    searchstrings[dep] = []
    for y in range(years):
        #print('octoral.*' + dep + '.*' + str(ejlmod3.year(backwards=y)))
        searchstrings[dep].append(re.compile('octoral.*' + dep + '.*' + str(ejlmod3.year(backwards=y))))

options = Options()
#options.add_argument("--headless")
options.add_argument("--enable-javascript")
options.add_argument("--incognito")
options.add_argument("--nogpu")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1200,1980")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument('--disable-blink-features=AutomationControlled')
driver = webdriver.Chrome(options=options)

theseslinks = ['https://waseda.repo.nii.ac.jp/records/78514',
               'https://waseda.repo.nii.ac.jp/records/78481',
               'https://waseda.repo.nii.ac.jp/records/78511']
if theseslinks:
    index = 'https://waseda.repo.nii.ac.jp'
    recs = []
    for (i, thesislink) in enumerate(theseslinks):
        ejlmod3.printprogress('-', [[i+1, len(theseslinks)], [thesislink]])
        
        driver.get(thesislink)
        sleep(5)
        data_soup = BeautifulSoup(driver.page_source, 'lxml')

        rec = {'tc': 'T', 'jnl': 'BOOK', 'link' : thesislink}

        ejlmod3.metatagcheck(rec, data_soup, ['citation_publication_date',
                                              'citation_title', 'citation_author'])
        for pre in data_soup.find_all('pre', attrs = {'class' : 'hide'}):
            scripttjson = json.loads(pre.text.strip())
            #print(scripttjson.keys())
            if 'permalink_uri' in scripttjson:
                rec['hdl'] = re.sub('.*handle.net\/', '', scripttjson['permalink_uri'])
            if 'item_10006_biblio_info_24' in scripttjson:
                if 'bibliographicPageEnd' in scripttjson['item_10006_biblio_info_24']['attribute_value_mlt']:
                    rec['pages'] = scripttjson['item_10006_biblio_info_24']['attribute_value_mlt']['bibliographicPageEnd']
            if 'item_files' in scripttjson:
                size = 0
                for datei in scripttjson['item_files']['attribute_value_mlt']:
                    if datei['size'] > size:
                        rec['pdf_url'] = datei['url']['url']
                        size = datei['size']
                    
        recs.append(rec)
        ejlmod3.printrecsummary(rec)
        sleep(5)

    ejlmod3.writenewXML(recs, publisher, jnlfilename)        
else:
    print('Scheiß Javascript - Links per Hand raussuchen -> theseslinks')
    index = 'https://waseda.repo.nii.ac.jp'
    driver.get(index)
    index_soup = BeautifulSoup(driver.page_source, 'lxml')
    lines = []
    for div in index_soup.find_all('div'):
        if div.has_attr('ng-init'):
            scriptt = div['ng-init']
            scriptt = re.sub('[\n\t]', '', scriptt)[10:-2]
            #print(scriptt[:100])
            #print(scriptt[-100:])
            scripttjson = json.loads(scriptt)
            if "condition_setting"  in scripttjson:
                for cs in scripttjson["condition_setting"]:
                    if "check_val" in cs:
                        lines += cs["check_val"]
    print(len(lines))

    for (dep, q) in deps:
        ejlmod3.printprogress('\n', [[dep]])
        subqs = []
        for line in lines:
            if 'contents' in line:                                
                for sstring in searchstrings[dep]:
                    if sstring.search(line['contents']):
                        q = line['id']
                        if not q in subqs:
                            subqs.append(q)
                            print('   ', line['contents'])
        recs = []
        for (i, q) in enumerate(subqs):
            toclink = 'https://waseda.repo.nii.ac.jp/search?page=1&size=' + str(rpp) + '&sort=-createdate&search_type=2&q=' + str(q)
            ejlmod3.printprogress('=', [[dep], [i+1, len(subqs)], [toclink]])
            sleep(30)
            driver.get(toclink)
            toc_soup = BeautifulSoup(driver.page_source, 'lxml')
            #print(toc_soup.prettify())
            
