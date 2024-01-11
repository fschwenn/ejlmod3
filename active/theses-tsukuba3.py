# -*- coding: utf-8 -*-
#harvest theses from Tsukuba U.
#FS: 2021-10-21
#FS: 2023-01-09

import getopt
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
from selenium.webdriver.firefox.options import Options
import requests

rpp = 20
skipalreadyharvested = True

publisher = 'Tsukuba U.'
jnlfilename = 'THESES-TSUKUBA-%s' % (ejlmod3.stampoftoday())

#driver
options = uc.ChromeOptions()
options.headless=True
options.binary_location='/usr/bin/google-chrome'
options.binary_location='/usr/bin/chromium'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)
#driver.implicitly_wait(30)

prerecs = []
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
deps = [('253', 1), ('250', 1), ('254', 3)]
for (dep, pages) in deps:
    for i in range(pages):
        tocurl = 'https://tsukuba.repo.nii.ac.jp/items/export?page=' + str(i+1) + '&size=' + str(rpp) + '&sort=-controlnumber&search_type=2&q=' + dep
        ejlmod3.printprogress("=", [[dep], [i+1, pages], [tocurl]])
        driver.get(tocurl)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'ng-binding')))
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
        for a in tocpage.body.find_all('a', attrs = {'class' : 'ng-binding'}):
            if a.has_attr('href') and re.search('records', a['href']):
                rec = {'tc' : 'T', 'jnl' : 'BOOK', 'note' : []}
                rec['link'] = 'https://tsukuba.repo.nii.ac.jp' + a['href']
                rec['doi'] = '30.3000/Tsukuba' + a['href'] 
                recid = int(re.sub('\D', '', a['href']))
                rec['note'].append('DOI guessed from theses ID: 10.15068/%010i' % (recid))
                if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
                    prerecs.append(rec)            
        time.sleep(4)
        print('  %4i records so far' % (len(prerecs)))

i = 0
recs = []
for rec in prerecs:
    i += 1
    disstyp = False    
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        driver.get(rec['link'])
        artpage = BeautifulSoup(driver.page_source, features="lxml")
    except:
        print(' ... wait 20s')
        time.sleep(20)
        driver.get(rec['link'])
        time.slee(2)
        artpage = BeautifulSoup(driver.page_source, features="lxml")        
    for span in artpage.find_all('span', attrs = {'class' : 'pull-right'}):
        st = re.sub('[\n\t\r]', '', span.text.strip())
        if re.search('handle.net', st):
            rec['hdl'] = re.sub('.*handle.net\/', '', st)
        elif  re.search('doi.org', st):
            rec['doi'] = re.sub('.*doi.org\/', '', st)
    time.sleep(2)    
    try:
        artjson = requests.get(rec['link'] + '/export/json').json()
    except:
        print(' ... wait 20s')
        time.sleep(20)
        artjson = requests.get(rec['link'] + '/export/json').json()        
    time.sleep(4)
    #date
    if 'item_12_date_granted_46' in list(artjson['metadata'].keys()):
        for entry in artjson['metadata']['item_12_date_granted_46']['attribute_value_mlt']:
            if 'subitem_dategranted' in list(entry.keys()):
                rec['date'] = entry['subitem_dategranted']
    elif 'publish_date' in list(artjson['metadata'].keys()):
        rec['date'] = artjson['metadata']['publish_date']
    #abstract
    if 'item_12_description_4' in list(artjson['metadata'].keys()):
        for entry in artjson['metadata']['item_12_description_4']['attribute_value_mlt']:
            if 'subitem_description_type' in list(entry.keys()) and entry['subitem_description_type'] == 'Abstract':
                rec['abs'] = entry['subitem_description']
    #PIDs
    if 'item_12_identifier_34' in list(artjson['metadata'].keys()):
        for entry in artjson['metadata']['item_12_identifier_34']['attribute_value_mlt']:
            if 'subitem_identifier_type' in list(entry.keys()):
                if entry['subitem_identifier_type'] == 'HDL':
                    rec['hdl'] = re.sub('.*handle.net\/', '', entry['subitem_identifier_uri'])
                elif entry['subitem_identifier_type'] == 'DOI':
                    rec['doi'] = re.sub('.*doi.org\/', '', entry['subitem_identifier_uri'])
    #PDF
    if 'item_files' in list(artjson['metadata'].keys()):
        for entry in artjson['metadata']['item_files']['attribute_value_mlt']:
            if 'accessrole' in list(entry.keys()):
                if entry['accessrole'] == 'open_access':
                    for entry in artjson['metadata']['item_files']['attribute_value_mlt']:
                        rec['FFT'] = entry['url']['url']
    #language
    for entry in artjson['metadata']['item_language']['attribute_value_mlt']:
        if entry['subitem_language'] == 'jpn':
            rec['language'] = 'Japanese'
        elif entry['subitem_language'] != 'eng':
            rec['note'].append('language:'+entry['subitem_language'])
            rec['language'] = entry['subitem_language']
    #title
    rec['tit'] = artjson['metadata']['title'][0]
    for entry in artjson['metadata']['item_titles']['attribute_value_mlt']:
        if 'subitem_title_language' in list(entry.keys()):
            if entry['subitem_title_language'] == 'en':
                if 'language' in list(rec.keys()):
                    rec['transtit'] = entry['subitem_title']
                else:
                    rec['tit'] = entry['subitem_title']
            elif entry['subitem_title_language'] == 'ja':
                if 'language' in list(rec.keys()):
                    rec['tit'] = entry['subitem_title']
                else:
                    rec['otits'] = [entry['subitem_title']]
        elif not 'tit' in list(rec.keys()):
            rec['tit'] = entry['subitem_title']
    #author
    for entry in artjson['metadata']['item_creator']['attribute_value_mlt']:
        janame = False
        if 'creatorNames' in list(entry.keys()):
            for subentry in entry['creatorNames']:
                if 'creatorNameLang' in list(subentry.keys()):
                    if subentry['creatorNameLang'] == 'en':
                        rec['auts'] = [ subentry['creatorName'] ]
                    elif subentry['creatorNameLang'] == 'ja':
                        janame = subentry['creatorName']
                else:
                    rec['auts'] = [ subentry['creatorName'] ]
            if janame:
                if 'auts' in list(rec.keys()):
                    rec['auts'][-1] += ', CHINESENAME: ' + janame
                else:
                    rec['auts'] = [ subentry['creatorName'] ]
        rec['aff'] = [publisher]
    if skipalreadyharvested and 'doi' in rec and rec['doi'] in alreadyharvested:
        print('   %s already in backup' % (rec['doi']))
    elif skipalreadyharvested and 'hdl' in rec and rec['hdl'] in alreadyharvested:
        print('   %s already in backup' % (rec['hdl']))
    else:        
        ejlmod3.printrecsummary(rec)
        recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
