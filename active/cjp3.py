#!/usr/bin/python
#program to harvest CJP
# FS 2020-03-06

import os
import ejlmod3
import re
import sys
from bs4 import BeautifulSoup
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def tfstrip(x): return x.strip()

publisher = 'Canadian Science Publishing'
jnl = sys.argv[1]
vol = sys.argv[2]
isu = sys.argv[3]

month = {'January' : 1, 'February' : 2, 'March' : 3, 'April' : 4,
         'May' : 5, 'June' : 6, 'July' : 7, 'August' : 8,
         'September' : 9, 'October' : 10, 'November' : 11, 'December' : 12}

if   (jnl == 'cjp'):
    jnlname = 'Can.J.Phys.'
    issn = '0008-4204'

jnlfilename = jnl+vol+'.'+isu

urltrunk = 'https://cdnsciencepub.com'
tocurl = '%s/toc/%s/%s/%s' % (urltrunk, jnl, vol, isu)
print("get table of content of %s%s.%s via %s " % (jnlname, vol, isu, tocurl))

options = uc.ChromeOptions()
options.headless=True
options.binary_location='/usr/bin/chromium-browser'
options.add_argument('--headless')
chromeversion = int(re.sub('Chro.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

driver.get(tocurl)
tocpage = BeautifulSoup(driver.page_source, features="lxml")

recs = []
for div in tocpage.body.find_all('div', attrs = {'class' : 'table-of-content'}):
    sectiontitle = False
    for child in div.children:
        try:
            child.name
        except:
            continue
        for h3 in child.find_all('h3'):
            sectiontitle = h3.text.strip()
        for div in child.find_all('div', attrs = {'class' : 'issue-item__title'}):
            for a in div.find_all('a'):
                for h5 in a.find_all('h5'):
                    rec = {'jnl' : jnlname, 'vol' : vol, 'issue' : isu, 'tc' : 'P',
                           'note' : [], 'autaff' : [], 'keyw' : []}
                    rec['artlink'] = 'https://cdnsciencepub.com' + a['href']
                    rec['doi'] = re.sub('.*?(10.1139.*)', r'\1', a['href'])
                    if sectiontitle: rec['note'].append(sectiontitle)
                    recs.append(rec)

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress('-', [[i, len(recs)], [rec['artlink']]])
    driver.get(rec['artlink'])
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, 'citation-content')))
    artpage = BeautifulSoup(driver.page_source, features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['dc.Title', 'dc.Subject', 'dc.Date', 'dc.Identifier', 'dc.Language'])
    #abstract
    for section in artpage.body.find_all('section', attrs = {'id' : 'abstract'}):
        for h2 in section.find_all('h2'):
            h2.decompose()
        rec['abs'] = section.text.strip()
        if re.search('PACS Nos.: ', rec['abs']):
            pacss = re.sub('.*PACS Nos.: *', '', rec['abs'])
            rec['abs'] = re.sub('PACS Nos.*', '', rec['abs'])
            rec['pacs'] = re.split(' *, *', pacss)
    #pages, year
    for span in artpage.body.find_all('span', attrs = {'property' : 'datePublished'}):
        rec['year'] = re.sub('.*([12]\d\d\d).*', r'\1', span.text.strip())
    for span in artpage.body.find_all('span', attrs = {'property' : 'pageStart'}):
        rec['p1'] = span.text.strip()
    for span in artpage.body.find_all('span', attrs = {'property' : 'pageEnd'}):
        rec['p2'] = span.text.strip()
    #keywords
    for section in artpage.body.find_all('section', attrs = {'property' : 'keywords'}):
        if section.has_attr('xml:lang') and section['xml:lang'] == 'fr':
            continue
        for li in section.find_all('li'):
            keyword = li.text.strip()
            if not keyword in rec['keyw']:
                rec['keyw'].append(keyword)
    #authors
    for section in artpage.body.find_all('section', attrs = {'class' : 'core-authors'}):
        for div in section.find_all('div', attrs = {'property' : 'author'}):
            #name
            for author in div.find_all('div', attrs = {'class' : 'heading'}):
                for fn in author.find_all('span', attrs = {'property' : 'familyName'}):
                    name = fn.text.strip()
                for gn in author.find_all('span', attrs = {'property' : 'givenName'}):
                    name += ', ' + gn.text.strip()
                rec['autaff'].append([name])
                #email
                for email in author.find_all('a', attrs = {'property' : 'email'}):
                    rec['autaff'][-1].append(re.sub('mailto:', 'EMAIL:', email['href']))
            #affiliations
            for aff in div.find_all('div', attrs = {'typeof' : 'Organization'}):
                rec['autaff'][-1].append(aff.text.strip())
    #references
    for section in artpage.body.find_all('section', attrs = {'id' : 'bibliography'}):    
        rec['refs'] = []
        for div in section.find_all('div', attrs = {'data-has' : 'label'}):
            rdoi = False
            for a in div.find_all('a'):
                if re.search('rossref', a.text):
                    rdoi = re.sub('.*doi.org\/', '', a['href'])
                    rdoi = re.sub('%2F', '/', rdoi)
                    rdoi = re.sub('%28', '(', rdoi)
                    rdoi = re.sub('%29', ')', rdoi)
                    rdoi = re.sub('%3A', ':', rdoi)
                    a.replace_with(rdoi)
                else:
                    a.replace_with('')
            reference = [('x', re.sub(', *,', ',', re.sub('[\n\t\r]', ' ', div.text.strip())))]
            if rdoi:
                reference.append(('a', 'doi:%s' % (rdoi)))                
            rec['refs'].append(reference)
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)

