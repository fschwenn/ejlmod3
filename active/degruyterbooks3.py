# -*- coding: UTF-8 -*-
#program to harvest PDe Gruyter Book series
# FS 2016-01-03
# FS 2023-04-14

import os
import ejlmod3
import re
import sys
#import unicodedata
#import string
import urllib.request, urllib.error, urllib.parse
import time

from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC



urltrunc = 'https://www.degruyter.com'
publisher = 'De Gruyter'

serial = sys.argv[1]
skipalreadyharvested = True
rpp = 100
years = 2*10


jnlfilename = 'dg' + serial + ejlmod3.stampoftoday()
if serial == 'GSTMP':
    jnl = "De Gruyter Stud.Math.Phys."
    tocurl = 'https://www.degruyter.com/view/serial/GSTMP-B?contents=toc-59654'
    tocurl = 'https://www.degruyter.com/serial/GSTMP-B/html#volumes'
    todo = [(1, publisher, tocurl, jnlfilename)]
elif serial == 'QC':
    jnl = 'BOOK'
    tocurl = 'https://www.degruyter.com/serial/qc-b/html#volumes'
    todo = [(1, publisher, tocurl, jnlfilename)]
elif serial in ['PY', 'MT', 'CO']:
    publishers = ["De Gruyter", "De Gruyter Oldenbourg", "EDP Sciences",
                  "Princeton University Press", "Harvard University Press",
                  "Yale University Press", "Columbia University Press",
                  "Mercury Learning And Information", "University of Hawai'i Press",
                  "University of Toronto Press", "University of California Press",
                  "Presses De L'université Laval", "University of Pennsylvania Press",
                  "Duke University Press", "Mcgill-queen's University Press",
                  "Stanford University Press", "Cornell University Press",
                  "Deutscher Kunstverlag", "Penn State University Press",
                  "Rutgers University Press", "Amsterdam University Press",
                  "Fordham University Press", "New York University Press",
                  "University of Chicago Press"]
    jnl = 'BOOK'
    todo = []
    for (i, publisher) in enumerate(publishers):
        if 'Universi' in publisher:
            house = re.sub('Universi[a-zé]', 'U', publisher)
            house = re.sub('Presses', 'P', house)
            house = re.sub('Press', 'P', house)
            house = re.sub(' (of|De) ', '', house)
            house = re.sub('[\- é\']', '', house).lower()
        else:
            house = re.sub('[a-z\- é\']', '', publisher).lower()        
        tocurl = 'https://www.degruyter.com/search?documentVisibility=all&publisherFacet=' + re.sub(' ', '+', publisher)+ '&subjectFacet=' + serial + '&documentTypeFacet=book&query=*&pageSize=' + str(rpp) + '&sortBy=mostrecent'
        jnlfilename = 'dg' + house + serial + ejlmod3.stampoftoday()
        todo.append((i+1, publisher, tocurl, jnlfilename))

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested('dg')

options = uc.ChromeOptions()
options.binary_location='/opt/google/chrome/google-chrome'
options.binary_location='/usr/bin/chromium'
options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)



for (n, publisher, tocurl, jnlfilename) in todo:
    ejlmod3.printprogress('=', [[n, len(todo)], [publisher, serial], [tocurl]])

    driver.implicitly_wait(30)
    try:
        driver.get(tocurl)
        tocpage = BeautifulSoup(driver.page_source, features='lxml')
    except:
        time.sleep(15)
        driver.get(tocurl)
        tocpage = BeautifulSoup(driver.page_source, features='lxml')

    #get volumes
    recs = []
    i = 0
    #divs = tocpage.body.find_all('div', attrs = {'class' : 'cover-image'})
    #divs = tocpage.body.find_all('h4', attrs = {'class' : 'resultTitle'})
    divs = tocpage.body.find_all('div', attrs = {'class' : 'searchResultContent'})
    for div in divs:
        i += 1
        skip = False
        for span in div.find_all('span', attrs = {'title' : 'Ahead of Publication'}):
            skip = 'Ahead of Publication'
        for span in div.find_all('span', attrs = {'class' : 'pubDate'}):
            try:
                year = int(span.text.strip())
                if year <= ejlmod3.year(backwards=years):
                    skip = '%i too old' % (year)
            except:
                pass
        if skip:
            ejlmod3.printprogress('-', [[i, len(divs)], [skip]])
        else:
            bookseries = False
            for a in div.find_all('a'):
                if re.search('serial\/', a['href']):
                    bookseries = a.text.strip()
                    a.decompose()
            for a in div.find_all('a'):
                if not re.search('document\/.*html', a['href']):
                    continue
                rec = {'tc' : 'B', 'jnl' : jnl, 'autaff' : []}
                if bookseries:
                    rec['bookseries'] = [('a', bookseries)]
                if serial == 'QC':
                    rec['fc'] = 'k'
                elif serial == 'MT':
                    rec['fc'] = 'm'
                elif serial == 'CO':
                    rec['fc'] = 'c'
                rec['artlink'] = urltrunc + a['href']
                ejlmod3.printprogress('-', [[i, len(divs)], [rec['artlink']], [len(recs)]])
                #DOI
                rec['doi'] = re.sub('.*doi\/(10.\d+\/.*)\/html', r'\1', rec['artlink'])
                if skipalreadyharvested and rec['doi'] in alreadyharvested:
                    print('  %s already in backup' % (rec['doi']))
                    continue
                #get details
                artfilename = '/tmp/dg%s' % (re.sub('[\(\)\/]', '_', rec['doi']))
                if not os.path.isfile(artfilename) or int(os.path.getsize(artfilename)) == 0:
                    time.sleep(10)
                    os.system("wget -T 300 -t 3 -q -O %s %s" % (artfilename, rec['artlink']))
                inf = open(artfilename, 'r')
                volpage = BeautifulSoup(''.join(inf.readlines()), features='lxml')
                inf.close()
                ejlmod3.metatagcheck(rec, volpage, ['citation_title', 'citation_keywords', 'citation_isbn',
                                                    'citation_publication_date', 'dc.identifier',
                                                    'citation_author', 'og:description',
                                                    'citation_pdf_url'])
                #license
                ejlmod3.globallicensesearch(rec, volpage)
                #volume
                for div in volpage.find_all('div', attrs = {'class' : 'font-content '}):
                    for a in div.find_all('a', attrs = {'class' : 'c-Button--primary"'}):
                        atext = a.text.strip()
                        if re.search('\d$', atext):
                            rec['vol'] = re.sub('.*\D', '', atext)
                #pages
                for dd in volpage.find_all('dd', attrs = {'class' : 'pagesarabic'}):
                    rec['pages'] = re.sub('[\n\t\r]', '', dd.text.strip())
                if not 'pages' in list(rec.keys()):
                    for li in volpage.find_all('li', attrs = {'class' : 'pageCounts'}):
                        rec['pages'] = 0
                        for li2 in li.find_all('li'):
                            rec['pages'] += int(re.sub('\D', '', li2.text.strip()))
                #ISBNS
                for dd in volpage.find_all('dd', attrs = {'class' : 'publisherisbn'}):
                    if 'isbn' in list(rec.keys()):
                        del rec['isbn']
                    if 'isbns' in list(rec.keys()): 
                        rec['isbns'].append([('a', re.sub('[\n\t\r\-]', '', dd.text.strip()))])
                    else:
                        rec['isbns'] = [[('a', re.sub('[\n\t\r\-]', '', dd.text.strip()))]]
                for li in volpage.find_all('li', attrs = {'class' : 'isbn'}):
                    if 'isbn' in list(rec.keys()):
                        del rec['isbn']
                    if 'isbns' in list(rec.keys()):
                        rec['isbns'].append([('a', re.sub('\D', '', li.text.strip()))])
                    else:
                        rec['isbns'] = [[('a', re.sub('\D', '', li.text.strip()))]]
                #authors
                if not rec['autaff']:
                    for div in volpage.find_all('div', attrs = {'class' : 'content-box'}):
                        for h2 in div.find_all('h2'):
                            if re.search('Author', h2.text):
                                for strong in div.find_all('strong'):
                                    rec['autaff'].append([strong.text.strip()])
                if not rec['autaff']:
                    for li in volpage.find_all('li', attrs = {'class=' : 'contributors-EDITOR'}):
                        for span in li.find_all('span', attrs = {'class' : 'displayName'}):
                            rec['autaff'].append([spant.text.strip() + ' (Ed.)'])
                if not rec['autaff']:
                    for div in volpage.find_all('div', attrs = {'class' : 'productInfo'}):
                        for h2 in div.find_all('h2'):
                            if re.search('Author', h2.text):
                                for strong in div.find_all('strong'):
                                    rec['autaff'].append([strong.text.strip()])
                                if not rec['autaff']:
                                    h2.decompose()
                                    rec['autaff'].append([re.sub(',*', '', div.text.strip())])
                if not rec['autaff']:
                    for div in volpage.find_all('div', attrs = {'class' : 'productInfo'}):
                        for h3 in div.find_all('h3'):
                            if re.search('[Aa]uthor information', h3.text) or re.search('[Aa]uthor *\/ *[eE]ditor information', h3.text) :
                                for div2 in div.find_all('div', attrs = {'class' : 'metadataInfoFont'}):
                                    for s in div2.find_all(['strong', 'b', 'B']):
                                        st = s.text.strip()
                                        if len(st) > 2:
                                            rec['autaff'].append([s.text.strip()])
                                            s.decompose()
                                    if rec['autaff']:
                                        rec['autaff'][-1].append(div2.text.strip())
                                    else:
                                        rec['autaff'] = [re.split(',', div2.text.strip(), 1)]
                    #print rec['autaff']
                if 'date' in list(rec.keys()):
                    ejlmod3.printrecsummary(rec)
                    recs.append(rec)
                else:
                    print('  no date!')
                    print(rec)
    
    ejlmod3.writenewXML(recs, publisher, jnlfilename)
    time.sleep(30)
