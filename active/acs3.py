# -*- coding: UTF-8 -*-
#!/usr/bin/python
#program to harvest ACS journals
# FS 2020-12-04

import sys
import os
import ejlmod3
import re
import time
from bs4 import BeautifulSoup
import undetected_chromedriver as uc

publisher = 'ACS'

jnl =  sys.argv[1]
vol = sys.argv[2]
iss = sys.argv[3]
jnlfilename = 'acs_%s%s.%s' % (jnl, vol, iss)
if jnl == 'nalefd': # 1 issue per month
    jnlname = 'Nano Lett.'
    letter = ''
elif jnl == 'jpccck': # 1 issue per week
    jnlname = 'J.Phys.Chem.'
    letter = 'C'
elif jnl == 'jctcce': # 1 issue per month
    jnlname = 'J.Chem.Theor.Comput.'
    letter = ''
elif jnl == 'apchd5': # 1 issue per month
    jnlname = 'ACS Photonics'
    letter = ''
elif jnl == 'jacsat': # 1 issue per week
    jnlname = 'J.Am.Chem.Soc.'
    letter = ''
else:
    print(' unknown journal "%s"' % (jnl))
    sys.exit(0)

try:
    options = uc.ChromeOptions()
    options.headless=True
    options.add_argument('--headless')
    driver = uc.Chrome(version_main=102, options=options)
except:
    print('try Chrome=99 instead')
    options = uc.ChromeOptions()
    options.headless=True
    options.add_argument('--headless')
    driver = uc.Chrome(version_main=99, options=options)
    #driver = uc.Chrome(options=options)

tocurl = 'https://pubs.acs.org/toc/%s/%s/%s' % (jnl, vol, iss)
print(tocurl)
driver.get(tocurl)
tocpage =  BeautifulSoup(driver.page_source, features="lxml")
section = False
recs = []
for div in tocpage.find_all('div', attrs = {'class' : 'toc'}):
    for child in div.children:
        try:
            child.name
        except:
            continue
        if child.name == 'h6':
            section = child.text.strip()
            print(section)
        elif  child.name == 'div':
            if not section in ['Mastheads', 'Editorial']:
                for input in child.find_all('input', attrs = {'name' : 'doi'}):
                    rec = {'jnl' : jnlname, 'vol' : letter+vol, 'issue' : iss, 'tc' : 'P',
                           'keyw' : [], 'note' : [], 'autaff' : []}
                    rec['doi'] = input['value']
                    rec['artlink'] = 'https://pubs.acs.org/doi/' + input['value']
                    if section:
                        rec['note'] = [ section ]
                    #title
                    for h5 in child.find_all('h5'):
                        rec['tit'] = h5.text.strip()
                    #authors
                    for author in child.find_all('span', attrs = {'class' : 'hlFld-ContribAuthor'}):
                        rec['autaff'].append([author.text.strip()])
                    #pages
                    for span in child.find_all('span', attrs = {'class' : 'issue-item_page-range'}):
                        rec['p1'] = re.sub('\D*(\d+).*', r'\1', span.text.strip())
                        rec['p2'] = re.sub('.*\D(\d+).*', r'\1', span.text.strip())
                    #abs
                    for span in child.find_all('span', attrs = {'class' : 'hlFld-Abstract'}):
                        rec['abs'] = span.text.strip()
                    #date
                    for span in child.find_all('span', attrs = {'class' : 'pub-date-value'}):
                        rec['date'] = re.sub('.*([12]\d\d\d).*', r'\1', span.text.strip())
                    recs.append(rec)

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress('-', [[i, len(recs)], [rec['artlink']]])
    try:
        time.sleep(60)
        driver.get(rec['artlink'])
        artpage = BeautifulSoup(driver.page_source, features="lxml")
    except:
        try:
            print('   wait 10 minutes')
            time.sleep(600)
            driver.get(rec['artlink'])
            artpage = BeautifulSoup(driver.page_source, features="lxml")
        except:
            print('  keep only', list(rec.keys()))
    rec['autaff'] = []
    ejlmod3.metatagcheck(rec, artpage, ['dc.Title', 'dc.Subject', 'og:description', 'dc.Date'])
    #keywords
    if not 'keyw' in rec or not rec['keyw']:
        for div in artpage.find_all('div', attrs = {'class' : 'article_header-taxonomy'}):
            rec['keyw'] = []
            for a in div.find_all('a'):
                rec['keyw'].append(a.text)
    #fulltext
    ejlmod3.globallicensesearch(rec, artpage)
    if 'license' in rec:
        for a in artpage.find_all('a', attrs = {'class' : 'pdf-button'}):
            rec['FFT'] = 'https://pubs.acs.org' + a['href']
    #authors
    for span in artpage.find_all('span'):
        for div in span.find_all('div', attrs = {'class' : 'loa-info-name'}):
            rec['autaff'].append([div.text.strip()])
            for a in span.find_all('a', attrs = {'title' : 'Orcid link'}):
                rec['autaff'][-1].append(re.sub('.*\/', r'ORCID:', a['href']))
            for div2 in span.find_all('div', attrs = {'class' : 'loa-info-affiliations-info'}):
                rec['autaff'][-1].append(div2.text.strip())
    #pages
    for span in artpage.find_all('span', attrs = {'class' : 'cit-fg-pageRange'}):
        rec['p1'] = re.sub('\D*(\d+).*', r'\1', span.text.strip())
        rec['p2'] = re.sub('.*\D(\d+).*', r'\1', span.text.strip())
    #references
    for ol in artpage.find_all('ol', attrs = {'id' : 'references'}):
        rec['refs'] = []
        for div in ol.find_all('div', attrs = {'class' : ['citationLinks', 'casRecord']}):
            div.decompose()
        for li in ol.find_all('li'):
            for a in li.find_all('a', attrs = {'class' : 'refNumLink'}):
                refnum = a.text
                a.replace_with('[%s] ' % (refnum))
            ref = li.text.strip()
            ref = re.sub('[\n\t\r]', ' ', ref)
            rec['refs'].append([('x', ref)])
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
