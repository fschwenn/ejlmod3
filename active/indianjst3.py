# -*- coding: UTF-8 -*-
#program to harvest  Indian.J.Sci.Techn.
# FS 2023-03-31

import sys
import os
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import json
import cloudscraper
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


publisher = 'Indian Society for Education and Environment (iSee)'
vol = sys.argv[1]
jnlfilename = 'indianjst%s.%s' % (vol, ejlmod3.stampoftoday())
jnlname = 'Indian.J.Sci.Techn.'
skipalreadyharvested = True

host = os.uname()[1]
if host == 'l00schwenn':
    options = uc.ChromeOptions()
    options.binary_location='/usr/bin/chromium'
#    options.add_argument('--headless')
#    options.add_argument('--no-sandbox')
    chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
    driver = uc.Chrome(version_main=chromeversion, options=options)
else:
    options = uc.ChromeOptions()
    options.binary_location='/usr/bin/google-chrome'
    options.add_argument('--headless')
    chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
    driver = uc.Chrome(version_main=chromeversion, options=options)
driver.implicitly_wait(60)
driver.set_page_load_timeout(30)


if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

tocurl = 'https://indjst.org/archives?volume=%s&issue=all#archives' % (vol)
print(tocurl)
driver.get(tocurl)
time.sleep(60)
complete = False
prerecs = []
artlinks = []
for i in range(100):
    tocpage = BeautifulSoup(driver.page_source, features="lxml")
    divs = tocpage.body.find_all('div', attrs = {'class' : 'Content-Sec'})
    if not divs:
        time.sleep(20)
        driver.get(tocurl)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
        divs = tocpage.body.find_all('div', attrs = {'class' : 'Content-Sec'})
    for div in divs:
        for a in div.find_all('a'):
            for h3 in a.find_all('h3', attrs = {'class' : 'Title'}):
                if not a['href'] in artlinks:
                    #print(h3.text.strip())                
                    prerecs.append({'jnl' : jnlname, 'tc' : 'P', 'vol' : vol, 'artlink' : a['href'], 'autaff' : []})
                    artlinks.append(a['href'])
    print('  %4i records so far' % (len(prerecs)))
    complete = True
    time.sleep(1)
    for button in tocpage.body.find_all('button', attrs = {'class' : 'blog_load_more_posts_btn'}):
        complete = False
        driver.find_element(By.CLASS_NAME, 'blog_load_more_posts_btn').click()
    if complete:
        break
    else:
        time.sleep(5)

i = 0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    driver.get(rec['artlink'])
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'Article-Footer')))
    time.sleep(5)
    artpage = BeautifulSoup(driver.page_source, features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ["citation_abstract", "citation_pdf_url", "citation_title",
                                        "citation_issue", "citation_online_date", "citation_language",
                                        "citation_doi", "citation_firstpage", "citation_lastpage",
                                        "keywords"])
    if 'abs' in rec:
        rec['abs'] = re.sub('Keywords:.*', '', rec['abs'])
    ejlmod3.globallicensesearch(rec, artpage)
    #detailed author-/aff-structure is a mess
    #for div in artpage.body.find_all('div', attrs = {'class' : 'Article-Author'}):
    for meta in artpage.find_all('meta', attrs = {'name' : 'citation_author'}):
        #print(' - ', meta)
        author = re.sub('nbsp ', '', meta['content'])
        author = re.sub('lowast ', '', author)
        author = re.sub('^and ', '', author)
        author = re.sub(' aacute ', 'á', author)
        author = re.sub(' eacute ', 'é', author)
        author = re.sub(' oacute ', 'ó', author)
        author = re.sub(' iacute ', 'í', author)
        author = re.sub(' agrave ', 'à', author)
        author = re.sub(' egrave ', 'è', author)
        author = re.sub(' ograve ', 'ò', author)
        author = re.sub(' igrave ', 'ì', author)
        author = author.strip()
        if author:
            for aut in re.split(' +and +', author):
                rec['autaff'].append([aut])
        #print(' = ', rec['autaff'])
    #references
    for div in artpage.body.find_all('div', attrs = {'class' : 'Article-References-Sec'}):
        rec['refs'] = []
        for li in div.find_all('li'):
            rec['refs'].append(([('x', li.text.strip())]))
    if not skipalreadyharvested or not 'doi' in rec or not rec['doi'] in alreadyharvested:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    time.sleep(5)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
