# -*- coding: utf-8 -*-
#harvest British Columbia U.
#FS: 2020-02-10
#FS: 2022-09-26

import getopt
import sys
import os
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

publisher = 'British Columbia U.'
jnlfilename = 'THESES-BRITISHCOLUMBIA-%s' % (ejlmod3.stampoftoday())

pages = 1
skipalreadyharvested = True
deps = [('Mathematics', 'm'), ('Astronomy', 'a'), ('Physics', ''),
        ('Computer%20Science', 'c'), ('Statistics', 's')]

options = uc.ChromeOptions()
options.headless=True
options.binary_location='/usr/bin/chromium-browser'
options.add_argument('--headless')
chromeversion = int(re.sub('Chro.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

dokidir = '/afs/desy.de/user/l/library/dok/ejl/backup'
alreadyharvested = []
def tfstrip(x): return x.strip()
if skipalreadyharvested:
    filenametrunc = re.sub('\d.*', '*doki', jnlfilename)
    alreadyharvested = list(map(tfstrip, os.popen("cat %s/*%s %s/%i/*%s | grep URLDOC | sed 's/.*=//' | sed 's/;//' " % (dokidir, filenametrunc, dokidir, ejlmod3.year(backwards=1), filenametrunc))))
    print('%i records in backup' % (len(alreadyharvested)))

prerecs = []
artlinks = []
for (dep, fc) in deps:
    for page in range(pages):
        tocurl = 'https://open.library.ubc.ca/search?q=*&p=' + str(page) + '&sort=6&view=0&circle=y&dBegin=&dEnd=&c=1&affiliation=' + dep + '&degree=Doctor%20of%20Philosophy%20-%20PhD'
        tocurl = 'https://open.library.ubc.ca/search?q=&p=' + str(page) + '&sort=6&view=0&perPage=0&dBegin=&dEnd=&collection=ubctheses&degree=Doctor%20of%20Philosophy%20-%20PhD&program=' + dep
        ejlmod3.printprogress('=', [[dep], [page+1, pages], [tocurl]])
        try:
            driver.get(tocurl)
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'dl-r-title')))        
        except:            
            print('retry %s in 180 seconds' % (tocurl))
            time.sleep(180)
            driver.get(tocurl)
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'dl-r-title')))        
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
        time.sleep(5)
        for a in tocpage.find_all('a', attrs = {'class' : 'dl-r-title'}):
            if a.has_attr('href'):
                rec = {'tc' : 'T', 'jnl' : 'BOOK', 'note' : [],
                       'supervisor' : []}
                rec['tit'] = a.text.strip()
                rec['artlink'] = re.sub('\?.*', '', a['href'])
#                if 'UBCO' in dep:
#                    rec['note'].append('Okanagan Campus')
                if fc:
                    rec['fc'] = fc
                if not rec['artlink'] in artlinks:
                    prerecs.append(rec)
                    artlinks.append(rec['artlink'])
                else:
                    print('         %s already in recs' % (rec['artlink']))
        print('    %4i records so far' % (len(prerecs)))
            

i = 0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        driver.get(rec['artlink'])
        artpage = BeautifulSoup(driver.page_source, features="lxml")
        time.sleep(10)
    except:
        try:
            print('retry %s in 180 seconds' % (rec['artlink']))
            time.sleep(180)
            driver.get(rec['artlink'])
            artpage = BeautifulSoup(driver.page_source, features="lxml")
        except:
            print('no access to %s' % (rec['artlink']))
            continue
    ejlmod3.globallicensesearch(rec, artpage)
    ejlmod3.metatagcheck(rec, artpage, ['citation_doi', 'citation_author',
                                        'citation_pdf_url', 'citation_publication_date',
                                        'citation_abstract_content'])
    for tr in artpage.body.find_all('tr'):
        for td in tr.find_all('td', attrs = {'class' : 'dl-r-label'}):
            tdt = td.text.strip()
        for td in tr.find_all('td', attrs = {'class' : 'dl-r-data'}):
            #Supervisor
            if tdt == 'Supervisor':
                for a in td.find_all('a'):
                    rec['supervisor'].append([a.text.strip()])
            #Handle
            elif tdt == 'URI':
                for a in td.find_all('a'):
                    if a.has_attr('href') and re.search('handle.net\/', a['href']):
                        rec['hdl'] = re.sub('.*handle.net\/', '', a['href'])
    if 'autaff' in rec:
        if not rec['doi'] in alreadyharvested:
            rec['autaff'][-1].append(publisher)
            ejlmod3.printrecsummary(rec)
            recs.append(rec)
ejlmod3.writenewXML(recs, publisher, jnlfilename)
driver.quit()
