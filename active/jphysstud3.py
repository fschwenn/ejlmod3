# -*- coding: UTF-8 -*-
#program to harvest Journal of Physical Studies
# FS 2021-02-16
# FS 2023-04-26

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


publisher = 'National University of Lviv'
tc = 'P'
year = sys.argv[1]
issue = sys.argv[2]

toclink = 'https://physics.lnu.edu.ua/jps/%s/%s/index.html' % (year, issue)
jnlfilename = "jphysstud%s.%s" % (year, issue)

print("get table of content... from %s" % (toclink))

options = uc.ChromeOptions()
options.binary_location='/usr/bin/google-chrome'
#options.binary_location='/usr/bin/chromium'
options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)
driver.implicitly_wait(30)

driver.get(toclink)
tocpage =  BeautifulSoup(driver.page_source, features='lxml')


recs = []

for title in tocpage.find_all('title'):
    year = re.sub('.*([12]\d\d\d).*', r'\1', title.text.strip())
for h3 in tocpage.body.find_all('h3'):
    vol = re.sub('.*vol\D*(\d+).*', r'\1', h3.text.strip())
for a in tocpage.body.find_all('a'):
    if a.has_attr('href') and a.text.strip() == 'abs':
        rec = {'jnl' : 'J.Phys.Stud.', 'tc' : tc, 'issue' : issue, 'note' : [],
               'refs' : [], 'auts' : [], 'aff' : [], 'keyw' : [], 'year' : year, 'vol' : vol}
        rec['link'] = 'https://physics.lnu.edu.ua/jps/%s/%s/%s' % (year, issue, a['href'])
        recs.append(rec)

i = 0
for rec in recs:
    i += 1
    (auts, affs) = (False, False)
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['link']]])
    time.sleep(3)
    driver.get(rec['link'])
    artpage =  BeautifulSoup(driver.page_source, features='lxml')
    #title
    for h1 in artpage.find_all('h1'):
        rec['tit'] = re.sub('[\n\t\r]', ' ', h1.text.strip())
        h1.replace_with('TITTITTIT')
    if not 'tit' in list(rec.keys()):
        for h2 in artpage.find_all('h2'):
            rec['tit'] = re.sub('[\n\t\r]', ' ', h2.text.strip())
            h2.replace_with('TITTITTIT')
    #pages
    for big in artpage.find_all('big'):
        bigt = big.text.strip()
        rec['p1'] = re.sub('.*rticle (\d+).*', r'\1', bigt)
        rec['pages'] = re.sub('.*\[(\d+).*', r'\1', bigt)
    #DOI
    for a in artpage.find_all('a'):
        if re.search('doi.org', a.text) and not 'doi' in list(rec.keys()):
            rec['doi'] = re.sub('.*org\/(10.*)', r'\1', a['href'])
    #references
    for ol in artpage.find_all('ol'):
        for li in ol.find_all('li'):
            for a in li.find_all('a'):
                if re.search('Crossref', a.text):
                    rdoi = re.sub('.*doi.org\/', '', a['href'])
                    a.replace_with(', DOI:'+rdoi)
            ref = re.sub('[\n\t\r]', ' ', li.text.strip())
            ref = re.sub('; *, DOI', ', DOI', ref)
            rec['refs'].append([('x', ref)])
        ol.replace_with('')
    #FFT
    for a in artpage.find_all('a'):
        if re.search('Full text', a.text):
            rec['FFT'] = 'https://physics.lnu.edu.ua/jps/%s/%s/%s' % (year, issue, a['href'][3:])
            a.replace_with('FFTFFTFFT')
    #abstract/keywords/PACS
    body = re.sub('[\n\t\r]', ' ', artpage.body.text.strip())
    abs = re.sub(' *FFTFFTFFT.*', '', body)
    abs = re.sub('.*published online \d* [A-Za-z]* \d* *', '', abs)
    abs = re.sub(' +pdf *$', '',  abs)
    if re.search('[kK]ey *words:', abs):
        rec['keyw'] = re.split(', ', re.sub('.*[kK]ey *words: *', '', abs))
        abs = re.sub('[kK]ey *words:.*', '', abs)
    if re.search('PACS.*:', abs):
        rec['pacs'] = re.split(', ', re.sub('.*PACS.*?: *', '', abs))
        abs = re.sub('PACS.*', '', abs)
    rec['abs'] = abs
    #autaff
    for sup in artpage.find_all('sup'):
        supt = sup.text.strip()
        supnr = re.sub('\D', '', supt)
        sup.replace_with(' , =Aff%s , ' % (supnr))
    for a in artpage.find_all('a', attrs = {'target' : 'orcidtab'}):
        orcid = re.sub('.*org\/', '', a['href'])
        a.replace_with(' , ORCID:%s , ' % (orcid))
    j = 0
    ps = []
    for p in artpage.find_all('p'):
        ps.append(p.text)
        if re.search('eceived.*accepted.*published', p.text):
            auts = ps[j-2]
            affs = ps[j-1]
        j += 1
    if not affs and len(ps) > 2:
        auts = ps[1]
        affs = ps[2]
    if auts:    
        #authors
        auts = re.sub('[\n\t\r]', ' ', auts)
        auts = re.sub(', *,', ',', auts)
        auts = re.sub('^ *,', '', auts)
        auts = re.sub(', *$', '', auts)
        auts = re.sub(', *,', ',', auts)
        auts = re.sub(',\s*,', ',', auts)
        affs = re.sub('[\n\t\r]', ' ', affs)
        affs = re.sub('[eE].?[mM]ails?:.*', '', affs)
        affpuffer = []
        author = False
        for aut in re.split('\s*,\s*', auts):
            if len(aut) > 3:
                if re.search('=Aff', aut):
                    affpuffer.append(aut.strip())
                elif re.search('ORCID', aut):
                    rec['auts'].append(author.strip() + ', ' + aut.strip())
                    for aff in affpuffer:
                        rec['auts'].append(aff)
                    affpuffer = []
                    author = False
                elif author:
                    rec['auts'].append(author)
                    for aff in affpuffer:
                        rec['auts'].append(aff)
                    affpuffer = []
                    author = aut.strip()
                else:
                    author = aut.strip()
        if author:
            rec['auts'].append(author)
                    
        for aff in re.split(' *,? *=Aff', affs)[1:]:
            rec['aff'].append(re.sub('^(\d+) *,? *', r'Aff\1= ', aff))
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
