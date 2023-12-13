# -*- coding: utf-8 -*-
#program to harvest journals individual DOIs  from OSA publishing
# FS 2023-12-12

import sys
import os
import ejlmod3
import re
import codecs
from bs4 import BeautifulSoup
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

publisher = 'OSA Publishing'
typecode = 'P'
bunchsize = 10
skipalreadyharvested = True

jnlfilename = 'OSA_QIS_retro.' + ejlmod3.stampoftoday()
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

sample = {'10.1364/OE.17.010976' : {'all' : 13 , 'core' : 13},
          '10.1364/OL.26.001714' : {'all' : 14 , 'core' : 14},
          '10.1364/OL.417851' : {'all' : 10 , 'core' : 10},
          '10.1364/OPEX.12.003865' : {'all' : 15 , 'core' : 15},
          '10.1364/PRJ.396115' : {'all' : 50 , 'core' : 50},
          '10.1364/OPTICA.394667' : {'all' : 15 , 'core' : 15},
          '10.1364/AOP.411024' : {'all' : 22 , 'core' : 22},
          '10.1364/JOSAB.6.002023' : {'all' : 33 , 'core' : 33},
          '10.1364/OE.15.003568' : {'all' : 23 , 'core' : 23},
          '10.1364/OL.30.002001' : {'all' : 39 , 'core' : 39},
          '10.1364/OPTICA.388773' : {'all' : 19 , 'core' : 19},
          '10.1364/JOSAB.32.000A40' : {'all' : 21 , 'core' : 21},
          '10.1364/OE.417856' : {'all' : 15 , 'core' : 15},
          '10.1364/OL.4.000205' : {'all' : 63 , 'core' : 63},
          '10.1364/OPTICA.412211' : {'all' : 22 , 'core' : 22},
          '10.1364/OE.15.015377' : {'all' : 30 , 'core' : 30},
          '10.1364/OPTICA.398628' : {'all' : 29 , 'core' : 29},
          '10.1364/OPTICA.425414' : {'all' : 36 , 'core' : 36},
          '10.1364/JOSA.31.000488' : {'all' : 53 , 'core' : 53},
          '10.1364/OPTICA.400751' : {'all' : 49 , 'core' : 49},
          '10.1364/OPTICA.413657' : {'all' : 22 , 'core' : 22},
          '10.1364/PRJ.388790' : {'all' : 26 , 'core' : 26},
          '10.1364/PRJ.428309' : {'all' : 20 , 'core' : 20},
          '10.1364/OPTICA.387306' : {'all' : 29 , 'core' : 29},
          '10.1364/OPTICA.4.000611' : {'all' : 21 , 'core' : 21},
          '10.1364/JOSAB.10.000524' : {'all' : 112 , 'core' : 112},
          '10.1364/ON.11.2.000011' : {'all' : 47 , 'core' : 47},
          '10.1364/JOSA.62.000055' : {'all' : 78 , 'core' : 78},
          '10.1364/OE.16.003032' : {'all' : 94 , 'core' : 94},
          '10.1364/AOP.1.000238' : {'all' : 87 , 'core' : 87},
          '10.1364/OE.16.019118' : {'all' : 13 , 'core' : 13},
          '10.1364/OE.405832' : {'all' : 12 , 'core' : 12},
          '10.1364/OE.418323' : {'all' : 11 , 'core' : 11}}
          


downloadpath = '/tmp'
pdfpath = '/afs/desy.de/group/library/publisherdata/pdf'

options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium'
options.add_experimental_option("prefs", {"download.prompt_for_download": False, "plugins.always_open_pdf_externally": True, "download.default_directory": downloadpath})
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)
#driver = uc.Chrome(options=options)


i = 0
recs = []
missingjournals = []
for doi in sample:
    i += 1
    ejlmod3.printprogress('-', [[i, len(sample)], [doi, sample[doi]['all'], sample[doi]['core']], [len(recs)]])
    if sample[doi]['core'] < 20:
        print('   too, few citations')
        continue
    if skipalreadyharvested and doi in alreadyharvested:
        print('   already in backup')
        continue
    
    if missingjournals:
        print('\nmissing journals:', missingjournals, '\n')
    rec = {'tc' : 'P', 'artlink' : 'https://doi.org/' + doi, 'doi' : doi, 'autaff' : [], 'keyw' : [], 'note' : []}
    jnl = re.sub('^10\.\d+\/([a-zA-Z]+).*', r'\1', doi).lower()
    if (jnl == 'oe'): 
        rec['jnl'] = 'Opt.Express'
    elif (jnl == 'ao'): 
        rec['jnl'] = 'Appl.Opt.'
    elif (jnl == 'on'):
        rec['jnl'] = 'Optics News'
    elif (jnl == 'ol'):
        rec['jnl'] = 'Opt.Lett.'
    elif (jnl == 'josa'): 
        rec['jnl'] = 'J.Opt.Soc.Am.'
    elif (jnl == 'josaa'): 
        rec['jnl'] = 'J.Opt.Soc.Am.A'
    elif (jnl == 'josab'): 
        rec['jnl'] = 'J.Opt.Soc.Am.B'
    elif (jnl == 'optica'):
        rec['jnl'] = 'Optica'
    elif (jnl == 'aop'):
        rec['jnl'] = 'Adv.Opt.Photon.'
    elif (jnl == 'prj'):
        rec['jnl'] = 'Photonics Res.'
    else:
        missingjournals.append(doi)
        continue
    try:
        driver.get(rec['artlink'])
        artpage = BeautifulSoup(driver.page_source, features="lxml")
    except:
        print('   try again in 60s...')
        time.sleep(60)
        driver.get(rec['artlink'])
        artpage = BeautifulSoup(driver.page_source, features="lxml")
    if len(artpage.find_all('meta')) < 10:
        print('  -- try again after 180 s  --  ')
        time.sleep(180)
        try:
            driver.get(rec['artlink'])
            artpage = BeautifulSoup(driver.page_source, features="lxml")
        except:
            print('   try again in 60s...')
            time.sleep(60)
            driver.get(rec['artlink'])
            artpage = BeautifulSoup(driver.page_source, features="lxml")
        if len(artpage.find_all('meta')) < 10:
            print('  -- try again after 300 s  --  ')
            time.sleep(300)
            try:
                driver.get(rec['artlink'])
                artpage = BeautifulSoup(driver.page_source, features="lxml")
            except:
                print('   try again in 60s...')
                time.sleep(60)
                driver.get(rec['artlink'])
                artpage = BeautifulSoup(driver.page_source, features="lxml")
        
        
    print('   read meta tags')
    ejlmod3.metatagcheck(rec, artpage, ['dc.description', 'citation_doi', 'dc.subject',
                                        'citation_firstpage', 'citation_lastpage',
                                        'citation_online_date', 'citation_volume',
                                        'citation_issue', 'citation_title'])
    #ORCIDs
    orciddict = {}
    for div in artpage.find_all('div', attrs = {'id' : 'authorAffiliations'}):        
        for tr in div.find_all('tr'):
            tds = tr.find_all('td')
            if len(tds) == 2 and re.search('orcid.org', tds[1].text):
                author = tds[0].text.strip()
                orcid = re.sub('.*orcid.org\/', 'ORCID:', tds[1].text.strip())
                if author in orciddict:
                    orciddict[author] = False #if author name is not unique
                else:
                    orciddict[author] = orcid
    for meta in artpage.find_all('meta'):
        if meta.has_attr('name'):
            #print meta['name']
            if meta['name'] == 'citation_author':                
                rec['autaff'].append([ meta['content'] ])
                if meta['content'] in orciddict and orciddict[meta['content']]:
                    rec['autaff'][-1].append(orciddict[meta['content']])
            elif meta['name'] == 'citation_author_institution':
                rec['autaff'][-1].append(meta['content'])
            elif meta['name'] == 'citation_author_orcid':
                orcid = re.sub('.*\/', '', meta['content'])
                rec['autaff'][-1].append('ORCID:%s' % (orcid))
            elif meta['name'] == 'citation_author_email':
                email = meta['content']
                rec['autaff'][-1].append('EMAIL:%s' % (email))    
            elif meta['name'] == 'citation_publication_date':
                rec['year'] = meta['content'][:4]
            elif meta['name'] == 'citation_pdf_url':
                if jnl in ['oe', 'boe', 'optica', 'ome', 'osac']:
                    rec['FFT'] = meta['content']
    #references
    j = 0
    for ol in artpage.find_all('ol', attrs = {'id' : 'referenceById'}):
        lis = ol.find_all('li')
        print('   read %i references' % (len(lis)))
        for li in lis:
            j += 1
            for a in li.find_all('a'):
                if re.search('Crossref', a.text):
                    alink = a['href']
                    a.replace_with(re.sub('.*doi.org\/', ', DOI: ', alink))
                elif not re.search('osa\.org\/abstract', a['href']):
                    a.replace_with('')
            ref = re.sub('[\n\t]', ' ', li.text.strip())
            ref = '[%i] %s' % (j, re.sub('\. *, DOI', ', DOI', ref))
            rec['refs'].append([('x', ref)])
    if not rec['autaff']:
        del rec['autaff']
    

    #sample note
    rec['note'] = ['reharvest_based_on_refanalysis',
                   '%i citations from INSPIRE papers' % (sample[doi]['all']),
                   '%i citations from CORE INSPIRE papers' % (sample[doi]['core'])]
    ejlmod3.printrecsummary(rec)
    recs.append(rec)
    ejlmod3.writenewXML(recs[((len(recs)-1) // bunchsize)*bunchsize:], publisher, jnlfilename + '--%04i' % (1 + (len(recs)-1) // bunchsize), retfilename='retfiles_special')
    #store pdf - but only for QIS as OSA likes to block
    for rec2 in recs:
        if 'FFT' in rec2 and 'fc' in rec2 and 'k' in rec2['fc']:
            targetfilename = '%s/%s/%s.pdf' % (pdfpath, re.sub('\/.*', '', rec2['doi']), re.sub('[\(\)\/]', '_', rec2['doi']))
            if os.path.isfile(targetfilename):
                print('     %s already exists' % (targetfilename))
            else:
                savedfilename = '%s/%s.pdf' % (downloadpath, re.sub('.*uri=(.*)&.*', r'\1', rec2['FFT']))
                if not os.path.isfile(savedfilename):            
                    print('     get %s from %s' % (savedfilename, rec2['FFT']))
                    driver.get(rec2['FFT'])
                    time.sleep(30)
                if os.path.isfile(savedfilename):
                    print('     mv %s to %s' % (savedfilename, targetfilename))
                    os.system('mv %s %s' % (savedfilename, targetfilename))
                    time.sleep(300)
                else:
                    print('     COULD NOT DOWNLOAD PDF')


