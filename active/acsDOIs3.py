# -*- coding: UTF-8 -*-
#program to harvest individual DOIs from ACS journals
# FS 2023-12-12

import sys
import os
import ejlmod3
import re
import time
from bs4 import BeautifulSoup
import undetected_chromedriver as uc

publisher = 'ACS'

skipalreadyharvested = True
bunchsize = 10

jnlfilename = 'ACS_QIS_retro.' + ejlmod3.stampoftoday()
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

sample = {'10.1021/acs.jctc.0c01052' : {'all' : 12 , 'core' : 12},
          '10.1021/acs.jctc.1c00912' : {'all' : 10 , 'core' : 10},
          '10.1021/acs.jctc.7b00049' : {'all' : 16 , 'core' : 16},
          '10.1021/acs.nanolett.0c00339' : {'all' : 21 , 'core' : 21},
          '10.1021/acs.nanolett.9b03847' : {'all' : 16 , 'core' : 16},
          '10.1021/acsphotonics.0c00833' : {'all' : 15 , 'core' : 15},
          '10.1021/acs.jctc.0c00421' : {'all' : 16 , 'core' : 16},
          '10.1021/acs.jctc.8b00536' : {'all' : 14 , 'core' : 14},
          '10.1021/acs.jpclett.0c02213' : {'all' : 12 , 'core' : 12},
          '10.1021/jacs.8b05934' : {'all' : 12 , 'core' : 12},
          '10.1021/acs.nanolett.5b02561' : {'all' : 17 , 'core' : 17},
          '10.1021/ct301044e' : {'all' : 19 , 'core' : 19},
          '10.1021/nl070949k' : {'all' : 17 , 'core' : 17},
          '10.1021/acs.jpcb.7b10371' : {'all' : 17 , 'core' : 17},
          '10.1021/acs.jpclett.0c03410' : {'all' : 14 , 'core' : 14},
          '10.1021/cr2001417' : {'all' : 22 , 'core' : 22},
          '10.1021/acscentsci.5b00338' : {'all' : 19 , 'core' : 19},
          '10.1021/acs.jctc.0c00170' : {'all' : 16 , 'core' : 16},
          '10.1021/acs.jctc.9b00236' : {'all' : 17 , 'core' : 17},
          '10.1021/jacs.9b00984' : {'all' : 22 , 'core' : 22},
          '10.1021/acscentsci.8b00788' : {'all' : 19 , 'core' : 19},
          '10.1021/acs.jctc.9b00963' : {'all' : 20 , 'core' : 20},
          '10.1021/acs.jctc.0c00666' : {'all' : 25 , 'core' : 25},
          '10.1021/acsphotonics.9b00250' : {'all' : 55 , 'core' : 55},
          '10.1021/acs.chemrev.8b00803' : {'all' : 281 , 'core' : 281},
          '10.1021/acs.jctc.0c00113' : {'all' : 30 , 'core' : 30},
          '10.1021/acs.jctc.8b00450' : {'all' : 33 , 'core' : 33},
          '10.1021/acsnano.5b01651' : {'all' : 31 , 'core' : 31},
          '10.1021/jp040647w' : {'all' : 53 , 'core' : 53},
          '10.1021/nl303758w' : {'all' : 377 , 'core' : 377},
          '10.1021/jz501649m' : {'all' : 32 , 'core' : 32},
          '10.1021/acs.jctc.8b00943' : {'all' : 31 , 'core' : 31},
          '10.1021/nl401216y' : {'all' : 76 , 'core' : 76},
          '10.1021/acs.jctc.9b01083' : {'all' : 35 , 'core' : 35},
          '10.1021/jp970984n' : {'all' : 48 , 'core' : 48},
          '10.1021/acs.jctc.9b01084' : {'all' : 48 , 'core' : 48},
          '10.1021/acs.jctc.9b01125' : {'all' : 50 , 'core' : 50},
          '10.1021/acs.jctc.9b00791' : {'all' : 55 , 'core' : 55},
          '10.1021/acs.jctc.0c00008' : {'all' : 52 , 'core' : 52},
          '10.1021/jp030708a' : {'all' : 100 , 'core' : 100},
          '10.1021/ac60214a047' : {'all' : 157 , 'core' : 157},
          '10.1021/acs.jctc.8b00932' : {'all' : 63 , 'core' : 63},
          '10.1021/acs.jctc.8b01004' : {'all' : 92 , 'core' : 92},
          '10.1021/acsnano.0c03167' : {'all' : 14 , 'core' : 14},
          '10.1021/acs.nanolett.0c02589' : {'all' : 12 , 'core' : 12}}


host = os.uname()[1]
if host == 'l00schwenn':
    options = uc.ChromeOptions()
    options.binary_location='/usr/bin/chromium'
    chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
    driver = uc.Chrome(version_main=chromeversion, options=options)
    tmpdir = '/home/schwenn/tmp'
else:
    options = uc.ChromeOptions()
#    options.headless=True
    options.binary_location='/usr/bin/google-chrome'
    options.add_argument('--headless')
    chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
    print(chromeversion)
    driver = uc.Chrome(version_main=chromeversion, options=options)
    tmpdir = '/tmp'


i = 0
recs = []
missingjournals = []
for doi in sample:
    if missingjournals:
        print('\nmissing journals:', missingjournals, '\n')

    i += 1
    ejlmod3.printprogress('-', [[i, len(sample)], [doi, sample[doi]['all'], sample[doi]['core']], [len(recs)]])
    rec = {'tc' : 'P', 'artlink' : 'https://pubs.acs.org/doi/' + doi, 'doi' : doi}
    jnl = re.sub('^10.\d+\/([a-z]+).*', r'\1', re.sub('\/acs\.', '/', doi))
    if jnl in ['nanolett', 'nalefd', 'nl']: # 1 issue per month
        rec['jnl'] = 'Nano Lett.'
        letter = ''
    elif jnl in ['jpccck', 'jp']: # 1 issue per week
        rec['jnl'] = 'J.Phys.Chem.'
        letter = 'C'
    elif jnl == 'jctcce': # 1 issue per month
        rec['jnl'] = 'J.Chem.Theor.Comput.'
        letter = ''
    elif jnl in ['apchd5', 'acsphotonics']: # 1 issue per month
        rec['jnl'] = 'ACS Photonics'
        letter = ''
    elif jnl in ['jacs', 'jacsat']: # 1 issue per week
        rec['jnl'] = 'J.Am.Chem.Soc.'
        letter = ''
    elif jnl in ['chemrev', 'chreay', 'cr']: # 1 issue per two weaks
        rec['jnl'] = 'Chem.Rev.'
        letter = ''
    elif jnl == 'jpcafh': # 1 issue per week
        rec['jnl'] = 'J.Phys.Chem.A'
        letter = ''
    elif jnl in ['jctc', 'ct']:
        rec['jnl'] = 'J.Chem.Theor.Comput.'
        letter = ''
    elif jnl in ['jz', 'jpclett']:
        rec['jnl'] = 'J.Phys.Chem.Lett.'
        letter = ''
    elif jnl == 'jpcb':
        rec['jnl'] = 'J.Phys.Chem.B'
        letter = ''
    elif jnl == 'acscentsci':
        rec['jnl'] = 'ACS Central Sci.'
        letter = ''
    elif jnl == 'acsnano':
        rec['jnl'] = 'ACS Nano'
        letter = ''
    elif jnl == 'ac':
        rec['jnl'] = 'Anal.Chem.'
        letter = ''
    else:
        missingjournals.append(doi)
        continue
        

    if sample[doi]['core'] < 20:
        print('   too, few citations')
        continue
    if skipalreadyharvested and doi in alreadyharvested:
        print('   already in backup')
        continue
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
            continue
    ejlmod3.metatagcheck(rec, artpage, ['dc.Title', 'dc.Subject', 'og:description', 'dc.Date'])     
    #keywords
    for div in artpage.find_all('div', attrs = {'class' : 'article_header-taxonomy'}):
        if not 'keyw' in rec or not rec['keyw']:
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
        divs = span.find_all('div', attrs = {'class' : 'loa-info-name'})
        if divs:
            rec['autaff'] = []
            for div in divs:
                rec['autaff'].append([div.text.strip()])
                for a in span.find_all('a', attrs = {'title' : 'Orcid link'}):
                    rec['autaff'][-1].append(re.sub('.*\/', r'ORCID:', a['href']))
                for div2 in span.find_all('div', attrs = {'class' : 'loa-info-affiliations-info'}):
                    rec['autaff'][-1].append(div2.text.strip())
    if not 'autaff' in rec:
        ejlmod3.metatagcheck(rec, artpage, ['dc.Creator'])
    #pages
    for span in artpage.find_all('span', attrs = {'class' : 'cit-fg-pageRange'}):
        rec['p1'] = re.sub('\D*(\d+).*', r'\1', span.text.strip())
        rec['p2'] = re.sub('.*\D(\d+).*', r'\1', span.text.strip())
    #volume, issue
    for span in artpage.find_all('span', attrs = {'class' : 'cit-fg-issue'}):
        rec['issue'] = re.sub(', ', '', span.text.strip())
    for span in artpage.find_all('span', attrs = {'class' : 'cit-fg-volume'}):
        rec['vol'] = re.sub(', ', '', span.text.strip())
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


    #sample note
    rec['note'] = ['reharvest_based_on_refanalysis',
                   '%i citations from INSPIRE papers' % (sample[doi]['all']),
                   '%i citations from CORE INSPIRE papers' % (sample[doi]['core'])]
    ejlmod3.printrecsummary(rec)
    recs.append(rec)
    ejlmod3.writenewXML(recs[((len(recs)-1) // bunchsize)*bunchsize:], publisher, jnlfilename + '--%04i' % (1 + (len(recs)-1) // bunchsize), retfilename='retfiles_special')

