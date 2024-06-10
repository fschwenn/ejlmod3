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


sample = {'10.1073/pnas.1603318113' : {'all' : 56 , 'core' : 56},
          '10.1073/pnas.1906861116' : {'all' : 18 , 'core' : 18},
          '10.1073/pnas.1801723115' : {'all' : 137 , 'core' : 137},
          '10.1073/pnas.1207329109' : {'all' : 16 , 'core' : 16},
          '10.1073/pnas.2026250118' : {'all' : 13 , 'core' : 13},
          '10.1073/pnas.1619152114' : {'all' : 155 , 'core' : 155},
          '10.1073/pnas.1616889113' : {'all' : 27 , 'core' : 27},
          '10.1073/pnas.1108174108' : {'all' : 125 , 'core' : 125},
          '10.1073/pnas.1603788113' : {'all' : 50 , 'core' : 50},
          '10.1073/pnas.241641898' : {'all' : 21 , 'core' : 21},
          '10.1073/pnas.1406966111' : {'all' : 44 , 'core' : 44},
          '10.1073/pnas.0703284104' : {'all' : 17 , 'core' : 17},
          '10.1073/pnas.2010580117' : {'all' : 139 , 'core' : 139},
          '10.1073/pnas.93.25.14256' : {'all' : 35 , 'core' : 35},
          '10.1073/pnas.1417132112' : {'all' : 68 , 'core' : 68},
          '10.1073/pnas.1002116107' : {'all' : 33 , 'core' : 33},
          '10.1073/pnas.1402365111' : {'all' : 39 , 'core' : 39},
          '10.1073/pnas.1601513113' : {'all' : 67 , 'core' : 67},
          '10.1073/pnas.1605716113' : {'all' : 45 , 'core' : 45},
          '10.1073/pnas.17.5.315' : {'all' : 57 , 'core' : 57},
          '10.1073/pnas.1711003114' : {'all' : 33 , 'core' : 33},
          '10.1073/pnas.1818752116' : {'all' : 39 , 'core' : 39},
          '10.1073/pnas.1110234108' : {'all' : 68 , 'core' : 68},
          '10.1073/pnas.1603251113' : {'all' : 27 , 'core' : 27},
          '10.1073/pnas.1603777113' : {'all' : 57 , 'core' : 57},
          '10.1073/pnas.1819316116' : {'all' : 95 , 'core' : 95},
          '10.1073/pnas.46.4.570' : {'all' : 49 , 'core' : 49},
          '10.1073/pnas.1412230111' : {'all' : 34 , 'core' : 34},
          '10.1073/pnas.1704827114' : {'all' : 47 , 'core' : 47},
          '10.1073/pnas.94.5.1634' : {'all' : 39 , 'core' : 39},
          '10.1073/pnas.1003052107' : {'all' : 64 , 'core' : 64},
          '10.1073/pnas.49.6.910' : {'all' : 92 , 'core' : 92},
          '10.1073/pnas.1111758109' : {'all' : 38 , 'core' : 38},
          '10.1073/pnas.2026805118' : {'all' : 39 , 'core' : 39},
          '10.1073/pnas.1619826114' : {'all' : 69 , 'core' : 69},
          '10.1073/pnas.1714936115' : {'all' : 54 , 'core' : 54},
          '10.1073/pnas.85.20.7428' : {'all' : 43 , 'core' : 43},
          '10.1073/pnas.20.5.259' : {'all' : 97 , 'core' : 97},
          '10.1073/pnas.1411728112' : {'all' : 132 , 'core' : 132},
          '10.1073/pnas.0808245105' : {'all' : 60 , 'core' : 60},
          '10.1073/pnas.1419326112' : {'all' : 133 , 'core' : 133},
          '10.1073/pnas.2006373117' : {'all' : 83 , 'core' : 83},
          '10.1073/pnas.1703516114' : {'all' : 196 , 'core' : 196},
          '10.1073/pnas.1618020114' : {'all' : 103 , 'core' : 103}}
sample = {'10.1073/pnas.0901550106' : {'all' : 73, 'core' : 20},
          '10.1073/pnas.17.5.315' : {'all' : 66, 'core' : 21},
          '10.1073/pnas.1306825110' : {'all' : 58, 'core' : 18},
          '10.1073/pnas.1715105115' : {'all' : 41, 'core' : 13},
          '10.1073/pnas.1005484107' : {'all' : 36, 'core' : 13},
          '10.1073/pnas.1804949115' : {'all' : 30, 'core' : 19},
          '10.1073/pnas.1207329109' : {'all' : 26, 'core' : 21},
          '10.1073/pnas.0703284104' : {'all' : 24, 'core' : 24},
          '10.1073/pnas.0803323105' : {'all' : 21, 'core' : 11},
          '10.1073/pnas.2026250118' : {'all' : 18, 'core' : 17},
          '10.1073/pnas.1922730117' : {'all' : 16, 'core' : 11}}

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



