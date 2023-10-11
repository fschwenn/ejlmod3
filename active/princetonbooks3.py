# -*- coding: UTF-8 -*-
#program to harvest Princeton University Press Books
# FS 2023-09-25

import sys
import os
import ejlmod3
import re
import urllib.request, urllib.error, urllib.parse
import time
from bs4 import BeautifulSoup
import undetected_chromedriver as uc

skipalreadyharvested = True

publisher = 'Princeton University Press'
jnlfilename = 'PrincetonBooks_%s' % (ejlmod3.stampoftoday())

serieses = [('22694', ''), ('22691', 'a'),
            ('22661', 'm'), ('22662', 'm'), ('22691', 'm'), ('22663', 'm'),
            ('22664', 'm'), ('22665', 'm'), ('22666', 'm'), ('22667', 'm'),
            ('22668', 'm'), ('22669', 'm'), ('22670', 'm'),
            ('22606', 'c'), ('22607', 'c'), ('22608', 'c'), ('22609', 'c'),
            ('22610', 'c'), ('22611', 'c'), ('22612', 'c'), ('22613', 'c'),
            ('22614', 'c'), ('22615', 'c')]

options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium'
options.add_argument("--enable-javascript")
options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

driver.get('https://press.princeton.edu')
time.sleep(18)

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

#scan serieses
prerecs = []
i= 0
for (series, fc) in serieses:
    i += 1
    toclink = 'https://press.princeton.edu/books?search=&subjects%5B%5D=' + series + '&field_general_interest_value=All&field_on_sale_value=All&sort_by=field_book_published_date_value'
    ejlmod3.printprogress('=', [ [i, len(serieses)], [series], [toclink] ])
    driver.get(toclink)
    time.sleep(60)
    tocpage = BeautifulSoup(driver.page_source, features="lxml")
    for li in tocpage.find_all('li', attrs = {'class' : 'm-book-listing'}):
        rec = {'tc' : 'B', 'jnl' : 'BOOK', 'autaff' : []}
        for a in li.find_all('a', attrs = {'class' : 'm-book-listing__link'}):
            rec['link'] = 'https://press.princeton.edu' + a['href']
            rec['tit'] = a.text.strip()
            rec['isbn'] = re.sub('\/isbn\/', '', a['href'])
            rec['doi'] = '20.2000/ISBN/' + rec['isbn']
        for em in li.find_all('em', attrs = {'class' : 'm-book-listing__author'}):
            for a in em.find_all('a'):
                rec['autaff'].append([a.text.strip()])
        if not rec['doi'] in alreadyharvested:
            prerecs.append(rec)
            alreadyharvested.append(rec['doi'])
    print('  %4i records so far' % (len(prerecs)))
    time.sleep(130)

#scan individual book pages
i = 0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['link']], [len(recs)]])
    driver.get(rec['link'])
    artpage = BeautifulSoup(driver.page_source, features="lxml")
    #title
    for h1 in artpage.find_all('h1'):
        rec['tit'] = h1.text.strip()
    #date
    ejlmod3.metatagcheck(rec, artpage, ['book:release_date'])
    #pages
    for dl in artpage.find_all('dl', attrs = {'class' : 'm-edition-info__attrs'}):
        dlt = re.sub('[\n\t\r]', ' ', dl.text.strip())
        if re.search('Pages: *\d+', dlt):
            rec['pages'] = re.sub('.*Pages: *(\d+).*', r'\1', dlt)
    #abstract
    for div in artpage.find_all('div', attrs = {'id' : 'overview'}):
        rec['abs'] = ''
        for p in div.find_all('p'):
            rec['abs'] = p.text.strip() + ' '
    #authors
    if not rec['autaff']:
        for ul in artpage.find_all('ul', attrs = {'class' : 'o-book__authors'}):
            for li in ul.find_all('li'):
                if re.search('Edited by', li.text):
                    edited = ' (Ed.)'
                else:
                    edited = ''
            for a in ul.find_all('a'):
                rec['autaff'].append([re.sub('(.*) (.*)', r'\2, \1', a.text.strip()) + edited])
    #year
    try:
        rec['year'] = re.sub('.*([21]\d\d\d).*', r'\1', rec['date'])
        if rec['year'] <= ejlmod3.stampoftoday()[:4]:
            ejlmod3.printrecsummary(rec)
            recs.append(rec)
    except:
        print('  problems?')
    if not rec['autaff']:
        sys.exit(0)
    time.sleep(12)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
