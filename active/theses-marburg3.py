# -*- coding: utf-8 -*-
#harvest theses from Philipps U. Marburg
#FS: 2022-04-19
#FS: 2023-03-24

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
from selenium.webdriver.firefox.options import Options

publisher = 'Philipps U. Marburg'
jnlfilename = 'THESES-MARBURG-%s' % (ejlmod3.stampoftoday())

pages = 1
skipalreadyharvested = True

prerecs = []
hdr = {'User-Agent' : 'Magic Browser'}
options = uc.ChromeOptions()
options.add_argument('--headless')
options.binary_location='/usr/bin/google-chrome-stable'
options.binary_location='/usr/bin/chromium'
options.binary_location='/usr/bin/google-chrome'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)



if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

driver.implicitly_wait(300)
for (fc, fachbereich) in [('', 'Fachbereich+Physik'), ('m', 'Fachbereich+Mathematik+und+Informatik')]:
    for page in range(pages):
        tocurl = 'https://archiv.ub.uni-marburg.de/ubfind/Search/Results?sort=year&filter%5B%5D=%7Eformat%3A%22DoctoralThesis%22&filter%5B%5D=building%3A%22' + fachbereich + '%22&join=AND&bool0%5B%5D=AND&lookfor0%5B%5D=&type0%5B%5D=AllFields&page=' + str(page+1)
        ejlmod3.printprogress("=", [[fachbereich], [page+1, pages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        for div in tocpage.body.find_all('div', attrs = {'class' : 'result-body'}):
            for a in div.find_all('a', attrs = {'class' : 'title'}):
                rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'supervisor' : []}
                rec['artlink'] = 'https://archiv.ub.uni-marburg.de' + a['href']
                prerecs.append(rec)
        time.sleep(5)

i = 0
recs = []
redoi = re.compile('.*(citeseerx.ist.*doi=|doi.org\/|link.springer.com\/|tandfonline.com\/doi\/abs\/|link.springer.com\/article\/|link.springer.com\/chapter\/|nlinelibrary.wiley.com\/doi\/|ournals.aps.org\/pr.*\/abstract\/|scitation.aip.org\/.*)(10\.[0-9]+\/.*)')
rebase = re.compile('base\-search.net')
for rec in prerecs:
    i += 1
    time.sleep(3)
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    req = urllib.request.Request(rec['artlink'] + '/Description', headers=hdr)
    artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    for tr in  artpage.body.find_all('tr'):
        for th in tr.find_all('th'):
            tht = th.text.strip()
        for td in tr.find_all('td'): 
            #language
            if tht in ['Sprache', 'Language:']:
                language = td.text.strip()
                if not language in ['Englisch', 'English']:
                    if language == 'Deutsch':
                        rec['language'] = 'German'
                    else:
                        rec['language'] = language
            #keywords
            elif tht in ['Subjects:', 'Schlagworte:']:
                for a in td.find_all('a'):
                    rec['keyw'].append(a.text.strip())
            #abstract
            elif tht in ['Summary:', 'Zusammenfassung:']:
                rec['abs'] = td.text.strip()
            #pages
            elif tht in ['Physical Description:', 'Umfang:']:
                pages = td.text.strip()
                if re.search('\d\d', pages):
                    rec['pages'] = re.sub('.*?(\d\d+).*', r'\1', pages)
            #DOI
            elif tht == 'DOI:':
                rec['doi'] = re.sub('.*doi.org\/', '', td.text.strip())
    #title
    for h1 in artpage.body.find_all('h1', attrs = {'property' : 'name'}):
        rec['tit'] = h1.text.strip()
    #author
    for span in artpage.body.find_all('span', attrs = {'property' : 'author'}):
        rec['autaff'] = [[ span.text.strip(), publisher ]]
    #supervisor
    for span in artpage.body.find_all('span', attrs = {'property' : 'contributor'}):
        for sp in span.find_all('span', attrs = {'class' : 'author-property-role'}):
            if re.search('(advisor|etreuer)', sp.text):
                sp.decompose()
                rec['supervisor'].append([re.sub(' *\(.*', '', span.text.strip())])
    #date
    for span in artpage.body.find_all('span', attrs = {'property' : 'datePublished'}):
        rec['date'] = span.text.strip()
    #PDF
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'citation_pdf_url'}):
        rec['pdf_url'] = 'https://archiv.ub.uni-marburg.de' + meta['content']
    #references
    time.sleep(2)
    driver.get(rec['artlink'] + '/References')
    refpage = BeautifulSoup(driver.page_source, features="lxml")
    for div in refpage.body.find_all('div', attrs = {'class' : 'references-tab'}):
        rec['refs'] = []
        for p in div.find_all('p'):
            pt = re.sub('\.$', '', p.text.strip())
            doi = False
            for a in p.find_all('a'):
                link = a['href']
            if redoi.search(link):
                doi = redoi.sub(r'doi:\2', link)
            elif not rebase.search(link):
                pt += ', ' + link
            if doi:
                rec['refs'].append([('x', pt), ('a', doi)])
            else:
                rec['refs'].append([('x', pt)])
    if not 'doi' in list(rec.keys()):
        rec['doi'] = '20.2000/Marburg/' + re.sub('\W', '', rec['artlink'][40:])
        rec['link'] = rec['artlink']
    if skipalreadyharvested and rec['doi'] in alreadyharvested:
        print('   already in backup')
    else:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
