# -*- coding: utf-8 -*-
#program to harvest Philosophy of Science
# FS 2019-10-28
# FS 2023-04-23

import sys
import os
import ejlmod3
import re
import urllib.request, urllib.error, urllib.parse

from bs4 import BeautifulSoup
import time
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC




tmpdir = '/tmp'
def tfstrip(x): return x.strip()
regexpref = re.compile('[\n\r\t]')

publisher = 'The University of Chicago Press Books'
typecode = 'P'
jnl = sys.argv[1]
year = sys.argv[2]
vol = sys.argv[3]
issue = sys.argv[4]
hdr = {'User-Agent' : 'Magic Browser'}


jnlfilename = 'chicago.%s%s.%s' % (jnl, vol, issue)

if jnl == 'phos':
    jnlname = 'Phil.Sci.'
elif jnl == 'bjps':
    jnlname = 'Brit.J.Phil.Sci.'
else:
    print('journal not known')
    
tocurl = 'https://www.journals.uchicago.edu/toc/%s/%s/%s/%s' % (jnl, year, vol, issue)
print(tocurl)

options = uc.ChromeOptions()
options.add_argument('--headless')
options.binary_location='/usr/bin/google-chrome'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

driver.implicitly_wait(30)
driver.get(tocurl)
tocpage = BeautifulSoup(driver.page_source, features="lxml")
#print tocpage.text
recs = []
#for div in tocpage.body.find_all('div', attrs = {'class' : 'tocContent'}):
for div in tocpage.body.find_all('ul', attrs = {'class' : 'table-of-content__section-body'}):
    section = ''
    for child in div.children:
        try:
            child.name
            print(child.name)
        except:
            continue
        if child.name == 'h2':
            section = child.text.strip()
            print(section)
        elif child.name == 'h4':
            section = child.text.strip()
            print(section)
#        elif child.name == 'table' and not section in ['Book Reviews', 'Discussions', '', 'Essay Reviews']:
        elif child.name == 'li' and not section in ['Book Reviews', 'Discussions', 'Essay Reviews']:
            #print child
            rec = {'jnl' : jnlname, 'vol' : vol, 'issue' : issue, 'year' : year, 'tc' : 'P', 'auts' : []}
            if section:
                rec['note'] = [section]
            #title
            for span in child.find_all('span', attrs = {'class' : 'hlFld-Title'}):
                rec['tit'] = span.text.strip()
            for h5 in child.find_all('h5', attrs = {'class' : 'issue-item__title'}):
                rec['tit'] = h5.text.strip()
            #authors
            for span in child.find_all('span', attrs = {'class' : 'hlFld-ContribAuthor'}):
                rec['auts'].append(re.sub(' and$', '', span.text.strip()))               
            #pages
            divs = child.find_all('div', attrs = {'class' : 'art_meta citation'})
            if not divs:
                divs = child.find_all('div', attrs = {'class' : 'issue-item__pages'})
            for div in divs:
                divt = re.sub('[\n\t\r]', '', div.text.strip())
                pages = re.sub('.*pp. (\d.*\d).*', r'\1', divt)
                rec['p1'] = re.sub('\D.*', '', pages)
                rec['p2'] = re.sub('.*\D', '', pages)
            #DOI
            links = child.find_all('a', attrs = {'class' : 'ref'})
            if not links:
                links = child.find_all('a', attrs = {'class' : 'issue-item__btn', 'title' : 'Full Text'})                
            for a in links:
                if re.search('10.10(86|93)', a['href']):
                    rec['doi'] = re.sub('.*(10.1086|10.1093)', r'\1', a['href'])
                    if re.search('\/(abs|full)\/', a['href']):
                        rec['artlink'] = 'https://www.journals.uchicago.edu' + a['href']
            #abstract
            for div in child.find_all('div', attrs = {'class' : 'issue-item__abstract'}):
                for div2 in div.find_all('div', attrs = {'class' : 'accordion__content'}):
                    rec['abs'] = div2.text.strip()
            if 'artlink' in list(rec.keys()):
                recs.append(rec)
                ejlmod3.printrecsummary(rec)

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['artlink']]])
    time.sleep(10)
    driver.get(rec['artlink'])
    artpage = BeautifulSoup(driver.page_source, features="lxml")
    #abstract
    ejlmod3.metatagcheck(rec, artpage, ['dc.Description', 'dc.Date', 'dc.Title'])
 
ejlmod3.writenewXML(recs, publisher, jnlfilename)
