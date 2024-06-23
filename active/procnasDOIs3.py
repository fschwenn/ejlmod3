# -*- coding: UTF-8 -*-
#program to harvest individual DOIs from Proc.Nat.Acad.Sci.
# FS 2023-12-28

import sys
import os
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import json
import cloudscraper
import undetected_chromedriver as uc



publisher = 'National Academy of Sciences of the USA'

skipalreadyharvested = False
bunchsize = 10
corethreshold = 15

jnlfilename = 'PROCNAS_QIS_retro.' + ejlmod3.stampoftoday()
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)


    
scraper = cloudscraper.create_scraper()
host = os.uname()[1]
options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

driver.implicitly_wait(60)
driver.set_page_load_timeout(30)


sample = {'10.1073/pnas.17.5.315' : {'all' :  68, 'core' :      21},
          '10.1073/pnas.1715105115' : {'all' :  42, 'core' :      14},
          '10.1073/pnas.1906861116' : {'all' :  20, 'core' :      13},
          '10.1073/pnas.1815884116' : {'all' :  20, 'core' :      11},
          '10.1073/pnas.2026250118' : {'all' :  18, 'core' :      17},
          '10.1073/pnas.1922730117' : {'all' :  16, 'core' :      11}}
    
i = 0
recs = []
missingjournals = []
jnlname = 'Proc.Nat.Acad.Sci.'
for doi in sample:
    rec = {'jnl' : jnlname, 
           'note' : [], 'autaff' : [], 'tc' : 'P'}
    i += 1
    ejlmod3.printprogress('-', [[i, len(sample)], [doi, sample[doi]['all'], sample[doi]['core']], [len(recs)]])
    if sample[doi]['core'] < corethreshold:
        print('   too, few citations')
        continue
    if skipalreadyharvested and doi in alreadyharvested:
        print('   already in backup')
        continue
    artlink = 'https://doi.org/' + doi
    try:
        driver.get(artlink)
        artpage = BeautifulSoup(driver.page_source, features="lxml")
        ejlmod3.metatagcheck(rec, artpage, ["citation_firstpage", "citation_pdf_url", "citation_doi",
                                            'citation_volume', 'citation_issue',
                                            "citation_online_date", "citation_title"])
    except:
        print('... try again in 120s')
        time.sleep(120)
        driver.get(artlink)
        artpage = BeautifulSoup(driver.page_source, features="lxml")
        ejlmod3.metatagcheck(rec, artpage, ["citation_firstpage", "citation_pdf_url", "citation_doi",
                                            'citation_volume', 'citation_issue',
                                            "citation_online_date", "citation_title"])        
    #print(artpage)
    #metadata in script
    for script in artpage.head.find_all('script'):
        if script.contents:
            scriptt = re.sub('.*?= *(\{.*?);.*', r'\1', re.sub('[\n\t]', '', script.contents[0].strip()))
            if re.search('^\{', scriptt):
                try:
                    metadata = json.loads(scriptt)
                except:
                    print("  could  not load JSON")
                    metadata = {}
                if 'page' in metadata:
                    print("   metadata in JSON found")
                    if 'pageInfo' in metadata['page']:
                        #date
                        if 'pubDate' in metadata['page']['pageInfo']:
                            rec['date'] = metadata['page']['pageInfo']['pubDate']
                        #DOI
                        if 'DOI' in metadata['page']['pageInfo']:
                            rec['doi'] = metadata['page']['pageInfo']['DOI']
                    if 'attributes' in metadata['page']:
                        #keywords
                        if 'keywords' in metadata['page']['attributes']: 
                            rec['keyw'] = metadata['page']['attributes']['keywords']
                        #license
                        if 'openAccess' in metadata['page']['attributes']:
                            if metadata['page']['attributes']['openAccess'] == 'yes':
                                rec['license'] = {'statement' : metadata['page']['attributes']['licenseType']}
    #p1
    for span in artpage.body.find_all('span', attrs = {'property' : 'identifier'}):
        rec['p1'] = span.text.strip()
    #abstract
    for section in artpage.body.find_all('section', attrs = {'id' : 'abstract'}):
        for div in section.find_all('div', attrs = {'role' : 'paragraph'}):
            rec['abs'] = div.text.strip()                
    #references
    for section in artpage.body.find_all('section', attrs = {'id' : 'bibliography'}):
        rec['refs'] = []
        for div in section.find_all('div', attrs = {'role' : ['doc-biblioentry listitem', 'listitem']}):
            for a in div.find_all('a'):
                at = a.text.strip()
                if at == 'Crossref': 
                    a.replace_with(re.sub('.*org\/', ', DOI: ', a['href']))
                    a.decompose()
                elif at in ['Google Scholar', 'PubMed']:
                    a.decompose()                                                       
            ref = div.text.strip()            
            rec['refs'].append([('x', ref)])
    #authors
    for div in artpage.body.find_all('div', attrs = {'property' : 'author'}):
        #print(div)
        for name in div.find_all('span', attrs = {'property' : 'familyName'}):
            author = name.text
        for name in div.find_all('span', attrs = {'property' : 'givenName'}):
            author += ', ' + name.text
        rec['autaff'].append([author])
        for a in div.find_all('a', attrs = {'class' : 'orcid-id'}):
            rec['autaff'][-1].append(re.sub('.*org\/', 'ORCID:', a['href']))
        for div2 in div.find_all('div', attrs = {'property' : 'affiliation'}):
            for span in div2.find_all('span'):
                rec['autaff'][-1].append(span.text.strip())
    #license
    for section in artpage.body.find_all('section', attrs = {'class' : 'core-copyright'}):
        for a in section.find_all('a'):
            if a.has_attr('href') and re.search('creativecom', a['href']):
                rec['license'] = {'url' : a['href']}
    ejlmod3.printrecsummary(rec)
    time.sleep(10)

    #sample note
    rec['note'] = ['reharvest_based_on_refanalysis',
                   '%i citations from INSPIRE papers' % (sample[doi]['all']),
                   '%i citations from CORE INSPIRE papers' % (sample[doi]['core'])]
    ejlmod3.printrecsummary(rec)
    recs.append(rec)
    ejlmod3.writenewXML(recs[((len(recs)-1) // bunchsize)*bunchsize:], publisher, jnlfilename + '--%04i' % (1 + (len(recs)-1) // bunchsize), retfilename='retfiles_special')
    if missingjournals:
        print('\nmissing journals:', missingjournals, '\n')



