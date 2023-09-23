# -*- coding: utf-8 -*-
#harvest theses from Thueringen
#FS: 2020-04-30
#FS: 2023-03-15

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import undetected_chromedriver as uc

publisher = 'db-thueringen.de'
jnlfilename = 'THESES-THUERINGEN-%s' % (ejlmod3.stampoftoday())

startyear = str(ejlmod3.year(backwards=2))
rpp = 50
skipalreadyharvested = True

options = uc.ChromeOptions()
options.binary_location='/opt/google/chrome/google-chrome'
#options.binary_location='/usr/bin/chromium'
options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)
    
identifiers = []
recs = []
tocpages = []
recs = []

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

ddcs = [('004', 'c'), ('006', 'c'), ('500', ''), ('510', 'm'), ('520', 'a'), ('530', '')]
k = 0
for (ddc, fc) in ddcs:
    k += 1
    tocurl = 'https://www.db-thueringen.de/servlets/solr/select?q=%2Bcategory.top%3A%22SDNB%5C%3A' + ddc + '%22+%2Bmods.dateIssued%3A%7B' + str(startyear) + '%5C-01%5C-01+TO+*%5D+%2Bstate%3A%22published%22+%2Bcategory.top%3A%22mir_genres%5C%3Adissertation%22+%2BobjectType%3A%22mods%22&fl=*&sort=mods.dateIssued+desc&rows=20&version=4.5&mask=content%2Fsearch%2Fcomplex.xed'
    ejlmod3.printprogress("=", [[k, len(ddcs)], ['DDC:'+ddc], [tocurl]])
    driver.get(tocurl)
    tocpages = [BeautifulSoup(driver.page_source, features='lxml')]
    for h1 in tocpages[-1].find_all('h1'):
        print(h1.text.strip())
        print(h1.text.strip())
        if re.search('\d', h1.text):
            numoftheses = int(re.sub('\D', '', h1.text.strip()))
            numofpages = (numoftheses-1) // rpp  + 1
        else:
            numoftheses = 0
            numofpages = 0
    if not numoftheses: continue
    
    for i in range(numofpages-1):
        tocurl = 'https://www.db-thueringen.de/servlets/solr/select?q=%2Bcategory.top%3A%22SDNB%5C%3A' + ddc + '%22+%2Bmods.dateIssued%3A%7B' + str(startyear) + '%5C-01%5C-01+TO+*%5D+%2Bstate%3A%22published%22+%2Bcategory.top%3A%22mir_genres%5C%3Adissertation%22+%2BobjectType%3A%22mods%22&fl=*&sort=mods.dateIssued+desc&rows=20&version=4.5&mask=content%2Fsearch%2Fcomplex.xed&start=' + str(rpp*(i+1)) + '&rows=' + str(rpp)
        ejlmod3.printprogress("=", [[k, len(ddcs)], ['DDC:'+ddc], [i+2, numofpages], [tocurl]])
        driver.get(tocurl)
        tocpages.append(BeautifulSoup(driver.page_source, features='lxml'))
    
    i = 0
    for tocpage in tocpages:
        i += 1
        j = 0
        divs = tocpage.find_all('div', attrs = {'class' : 'single_hit_option'})
        for div in divs:
            j += 1
            for a in div.find_all('a'):
                rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK'}
                if fc:
                    rec['fc'] = fc
                identifier = re.sub('.*id=(dbt_mods_\d+).*', r'\1', a['href'])
                rec['artlink'] = 'https://www.db-thueringen.de/receive/' + identifier
                if not identifier in identifiers:
                    identifiers.append(identifier)
                    ejlmod3.printprogress("-", [[k, len(ddcs)], ['DDC:'+ddc], [i, len(tocpages)], [j, len(divs)], [rec['artlink']], [len(recs)]])
                    try:
                        driver.get(rec['artlink'])
                        artpage = BeautifulSoup(driver.page_source, features='lxml')
                        time.sleep(3)
                    except:
                        try:
                            print("retry %s in 180 seconds" % (rec['artlink']))
                            time.sleep(180)
                            artpage = BeautifulSoup(driver.page_source, features='lxml')
                            time.sleep(3)
                        except:
                            print("no access to %s" % (rec['artlink']))
                            continue    
                    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'DC.description', 'DC.title',
                                                        'DC.date', 'DC.identifier', 'DC.rights',
                                                        'citation_doi'])
                    for dl in artpage.find_all('dl'):
                        for child in dl.children:
                            try:
                                child.name
                            except:
                                continue
                            if child.name == 'dt':
                                dtt = child.text
                            elif child.name == 'dd':
                                ddt = child.text.strip()
                                if ddt:
                                    #language
                                    if dtt in ['Sprache', 'Language:'] and ddt in['Deutsch', 'German']:
                                        rec['language'] = 'german'
                                    #pages
                                    elif dtt in ['Umfang', 'Extent:']:
                                        rec['pages'] = re.sub('.*?(\d\d+).*', r'\1', ddt)
                                    #affiliation
                                    elif dtt in ['Einrichtung:', 'Hosting institution:']:
                                        rec['autaff'][0].append(ddt + ', Deutschland')
                                    #keywords
                                    elif re.search('(Schlagw|Keywords)', dtt):
                                        for sup in child.find_all('sup'):
                                            sup.decompose()
                                        rec['keyw'] = re.split('; ', child.text.strip())
                    #fulltext
                    for noscript in artpage.find_all('noscript'):
                        nt = noscript.text.strip()
                        if re.search('\.pdf"', nt):
                            pdflink = re.sub('.*?(http.*?pdf)".*', r'\1', nt)
                            if 'license' in rec:
                                rec['FFT'] = pdflink
                            else:
                                rec['hidden'] = pdflink
                    #DOI ?
                    if not 'doi' in rec:
                        rec['link'] = driver.current_url
                    if skipalreadyharvested and 'doi' in rec and rec['doi'] in alreadyharvested:
                        print('  %s already in backup' % (rec['doi']))
                    else:
                        ejlmod3.printrecsummary(rec)
                        recs.append(rec)
        
ejlmod3.writenewXML(recs, publisher, jnlfilename)
