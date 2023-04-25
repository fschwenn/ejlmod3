# -*- coding: utf-8 -*-
#harvest theses from Bangalore, Indian Inst. Sci.
#FS: 2021-02-10
#FS: 2023-04-18

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

publisher = 'Bangalore, Indian Inst. Sci.'
jnlfilename = 'THESES-IISC-%s' % (ejlmod3.stampoftoday())

rpp = 50
numofpages = 1
skipalreadyharvested = True

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

hdr = {'User-Agent' : 'Magic Browser'}
recs = []
sections = [('44', ''), ('45', 'a'), ('46', ''), ('47', ''),
            ('48', 'i'), ('49', 'm'), ('50', '')]
j = 0
for (section, fc) in sections:
    j += 1
    for i in range(numofpages):
        tocurl = 'http://etd.iisc.ac.in/handle/2005/' + section + '/browse?rpp=' + str(rpp) + '&sort_by=3&type=title&offset=' + str(rpp*i) + '&etal=-1&order=DESC'
        ejlmod3.printprogress("=", [[i+1, numofpages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features='lxml')
        time.sleep(10)
        for div in tocpage.body.find_all('div', attrs = {'class' : 'artifact-description'}):
            for a in div.find_all('a'):
                rec = {'tc' : 'T', 'jnl' : 'BOOK', 'keyw' : [], 'note' : []}
                rec['link'] = 'http://etd.iisc.ac.in' + a['href']
                rec['doi'] = '20.2000/IISC/' + re.sub('\/handle\/', '', a['href'])
                rec['tit'] = a.text.strip()
                if fc:
                    rec['fc'] = fc
                if not rec['doi'] in alreadyharvested:
                    recs.append(rec)
                    alreadyharvested.append(rec['doi'])
        print('   %4i records so far' % (len(recs)))
                    
                    


options = uc.ChromeOptions()
options.binary_location='/opt/google/chrome/google-chrome'
options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)
driver.implicitly_wait(30)

j = 0
for rec in recs:
    j += 1
    ejlmod3.printprogress("-", [[j, len(recs)], [rec['link']]])
    try:
        driver.get(rec['link'])
        artpage = BeautifulSoup(driver.page_source, features='lxml')
    except:
        print('wait a minute')
        time.sleep(60)
        driver.get(rec['link'])
        artpage = BeautifulSoup(driver.page_source, features='lxml')
    time.sleep(5)
    #author
    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'citation_date', 
                                        'DCTERMS.abstract', 'DC.subject', 'dc.degree.level'])
    if 'dc.degree.level' in rec and rec['dc.degree.level']:
        rec['note'] += rec['dc.degree.level']
    rec['autaff'][-1].append( publisher )
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
