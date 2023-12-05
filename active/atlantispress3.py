# -*- coding: UTF-8 -*-
#program to harvest proceedings from atlantis press
# FS 2023-12-04

import os
import ejlmod3
import re
import time
from bs4 import BeautifulSoup
import sys
import undetected_chromedriver as uc


publisher = 'Springer Nature'
rpp = 100

vol = sys.argv[1]
if len(sys.argv) > 2:
    cnum = sys.argv[2]
    jnlfilename = 'atlantis_%s_%s' % (vol, cnum)
else:
    cnum = False
    jnlfilename = 'atlantis_%s' % (vol)

seriestofcdict = {'Advances in Computer Science Research' : 'c'}

options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)


(editors, volnum, isbn, conftit) = (False, False, False, '')
procurl = 'https://www.atlantis-press.com/proceedings/%s/publishing' % (vol)
ejlmod3.printprogress('=', [[0], [procurl]])
driver.get(procurl)
procpage = BeautifulSoup(driver.page_source, features="lxml")
for div in procpage.find_all('div', attrs = {'class' : 'src-components-series'}):
    for a in div.find_all('a'):
        series = a.text.strip()
for dl in procpage.find_all('dl', attrs = {'class' : 'src-components-metaList'}):
    for child in dl.children:
        try:
            child.name
        except:
            continue
        if child.name == 'dt':
            label = child.text.strip()
        elif child.name == 'dd':
            if label == 'Editors':
                for br in child.find_all('br'):
                    br.replace_with(' , ')
                editors = re.split(' *(,|and) +', re.sub('[\n\t\r]', ' ', child.text.strip()))
            elif label == 'Volume':
                volnum = child.text.strip()
            elif label == 'ISBN':
                isbn = child.text.strip()
            elif label == 'Title':
                conftit = child.text.strip()
                print(conftit)

time.sleep(5)                    
      




tocurl = 'https://www.atlantis-press.com/proceedings/%s/articles' % (vol)
ejlmod3.printprogress('=', [[1], [tocurl]])

tocreq = driver.get(tocurl)
tocpages = [BeautifulSoup(driver.page_source, features="lxml")]
for span in tocpages[0].find_all('span', attrs = {'class' : 'src-components-counterCount'}):
    numofarticles = int(span.text.strip())


if len(sys.argv) > 3:
    fc = sys.argv[3]
elif series in seriestofcdict:
    fc = seriestofcdict[series]
else:
    fc = False



for page in range((numofarticles-1) // rpp):
    ejlmod3.printprogress('=', [[page+2, (numofarticles-1) // rpp + 1], [tocurl]])
    time.sleep(10)
    tocreq = driver.get(tocurl + '?page=' + str(page+2))
    tocpages.append(BeautifulSoup(driver.page_source, features="lxml"))

recs = []
artlinks = []
for tocpage in tocpages:
    for div in tocpage.find_all('div', attrs = {'class', 'src-components-listItem'}):
        for a in div.find_all('a'):
            if re.search('proceedings', a['href']):
                rec = {'jnl' : 'BOOK', 'tc' : 'C', 'autaff' : [], 'note' : [conftit]}
                if cnum: rec['cnum'] = cnum
                if fc: rec['fc'] = fc
                if isbn: rec['motherisbn'] = isbn
                if volnum:
                    rec['bookseries'] = [('a', series), ('v', volnum)]
                else:
                    rec['bookseries'] = [('a', series)]
                rec['tit'] = a.text
                rec['artlink'] = 'https://www.atlantis-press.com' + a['href']
                if not rec['artlink'] in artlinks:
                    recs.append(rec)
                    artlinks.append(rec['artlink'])

for (i, rec) in enumerate(recs):
    time.sleep(6)
    ejlmod3.printprogress('-', [[i+1, numofarticles], [rec['artlink']]])
    artreq = driver.get(rec['artlink'])
    artpage = BeautifulSoup(driver.page_source, features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['citation_title', 'citation_author', 'citation_publication_date', 'citation_keywords', 'citation_doi', 'citation_firstpage', 'citation_lastpage', 'description'])
    for meta in artpage.find_all('meta', attrs = {'name' : 'citation_pdf_url'}):
        rec['pdf_url'] = 'https://www.atlantis-press.com' + meta['content']
    ejlmod3.globallicensesearch(rec, artpage)
    ejlmod3.printrecsummary(rec)


ejlmod3.printprogress('-', [[0, numofarticles], [rec['artlink']]])
rec = {'jnl' : 'BOOK', 'tc' : 'K', 'autaff' : [], 'note' : [conftit], 'link' : procurl}
if cnum: rec['cnum'] = cnum
if fc: rec['fc'] = fc
if isbn: rec['isbn'] = isbn
if editors:
    for editor in editors:
        rec['autaff'].append([re.sub('(.*) (.*)', r'\1, \2 (Ed.)', editor)])
recs.append(rec)
ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
