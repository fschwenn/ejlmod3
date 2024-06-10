 # -*- coding: UTF-8 -*-
#program to harvest DOIs from Science
# FS 2023-12-08

import sys
import os
import ejlmod3
import re
import time
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
import random
import cloudscraper

publisher = 'American Association for the Advancement of Science'
skipalreadyharvested = False
bunchsize = 10
corethreshold = 15
pdfpath = '/afs/desy.de/group/library/publisherdata/pdf'

jnlfilename = 'AAAS_QIS_retro.' + ejlmod3.stampoftoday() + '_2'
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium-browser'
options.binary_location='/usr/bin/chromium'
#options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
options.add_experimental_option("prefs", {"download.prompt_for_download": False, "plugins.always_open_pdf_externally": True, "download.default_directory": downloadpath})
driver = uc.Chrome(version_main=chromeversion, options=options)
    
#scraper = cloudscraper.create_scraper()


sample = {'10.1126/sciadv.aat3174' : {'all' : 49, 'core' : 19},
          '10.1126/science.1192065' : {'all' : 49, 'core' : 16},
          '10.1126/science.1078446' : {'all' : 48, 'core' : 23},
          '10.1126/sciadv.aar4994' : {'all' : 48, 'core' : 23},
          '10.1126/science.1136303' : {'all' : 48, 'core' : 16},
          '10.1126/sciadv.aaw8586' : {'all' : 47, 'core' : 28},
          '10.1126/science.286.5439.509' : {'all' : 47, 'core' : 18},
          '10.1126/science.aak9611' : {'all' : 47, 'core' : 17},
          '10.1126/science.1225258' : {'all' : 46, 'core' : 21},
          '10.1126/sciadv.1400255' : {'all' : 46, 'core' : 20},
          '10.1126/science.1250057' : {'all' : 46, 'core' : 15},
          '10.1126/science.1146204' : {'all' : 45, 'core' : 21},
          '10.1126/science.aax9406' : {'all' : 45, 'core' : 19},
          '10.1126/sciadv.aaz4888' : {'all' : 45, 'core' : 19},
          '10.1126/science.1143835' : {'all' : 44, 'core' : 26},
          '10.1126/science.aao0290' : {'all' : 44, 'core' : 22},
          '10.1126/science.1226487' : {'all' : 43, 'core' : 35},
          '10.1126/science.1177077' : {'all' : 43, 'core' : 32},
          '10.1126/sciadv.aap9416' : {'all' : 43, 'core' : 14},
          '10.1126/sciadv.aas9401' : {'all' : 42, 'core' : 29},
          '10.1126/science.1247715' : {'all' : 42, 'core' : 19},
          '10.1126/science.aau1949' : {'all' : 42, 'core' : 14},
          '10.1126/sciadv.aax1950' : {'all' : 40, 'core' : 23},
          '10.1126/science.aaw2906' : {'all' : 40, 'core' : 20},
          '10.1126/sciadv.aav2372' : {'all' : 40, 'core' : 17},
          '10.1126/sciadv.aba9186' : {'all' : 40, 'core' : 16},
          '10.1126/science.1209524' : {'all' : 39, 'core' : 31},
          '10.1126/sciadv.aau5999' : {'all' : 39, 'core' : 23},
          '10.1126/sciadv.aaz1192' : {'all' : 39, 'core' : 20},
          '10.1126/sciadv.aau0823' : {'all' : 39, 'core' : 19},
          '10.1126/sciadv.abc5055' : {'all' : 38, 'core' : 26},
          '10.1126/science.abc7821' : {'all' : 37, 'core' : 18},
          '10.1126/sciadv.aat8978' : {'all' : 37, 'core' : 16},
          '10.1126/sciadv.abc3847' : {'all' : 37, 'core' : 14},
          '10.1126/sciadv.aay2652' : {'all' : 37, 'core' : 11},
          '10.1126/science.1217635' : {'all' : 36, 'core' : 17},
          '10.1126/sciadv.1501531' : {'all' : 35, 'core' : 30},
          '10.1126/science.1201034' : {'all' : 35, 'core' : 29},
          '10.1126/sciadv.aba4508' : {'all' : 35, 'core' : 25},
          '10.1126/science.1183628' : {'all' : 35, 'core' : 21},
          '10.1126/science.aaa0754' : {'all' : 35, 'core' : 18},
          '10.1126/sciadv.1501165' : {'all' : 34, 'core' : 21},
          '10.1126/sciadv.abh0952' : {'all' : 34, 'core' : 16},
          '10.1126/science.aaw4329' : {'all' : 34, 'core' : 13},
          '10.1126/sciadv.aaw6664' : {'all' : 33, 'core' : 17},
          '10.1126/science.1170730' : {'all' : 33, 'core' : 16},
          '10.1126/science.aat3581' : {'all' : 32, 'core' : 18},
          '10.1126/science.abb9352' : {'all' : 32, 'core' : 13},
          '10.1126/sciadv.1600036' : {'all' : 31, 'core' : 14},
          '10.1126/sciadv.1601915' : {'all' : 30, 'core' : 23},
          '10.1126/science.1134008' : {'all' : 30, 'core' : 22},
          '10.1126/sciadv.abf3630' : {'all' : 30, 'core' : 11},
          '10.1126/sciadv.1500022' : {'all' : 29, 'core' : 22},
          '10.1126/science.aat4625' : {'all' : 29, 'core' : 19},
          '10.1126/sciadv.abm5912' : {'all' : 29, 'core' : 18},
          '10.1126/science.1093649' : {'all' : 29, 'core' : 16},
          '10.1126/sciadv.aba9636' : {'all' : 29, 'core' : 11},
          '10.1126/sciadv.aay3050' : {'all' : 28, 'core' : 26},
          '10.1126/science.261.5128.1569' : {'all' : 28, 'core' : 24},
          '10.1126/sciadv.aaw4530' : {'all' : 28, 'core' : 21},
          '10.1126/science.288.5467.824' : {'all' : 28, 'core' : 15},
          '10.1126/sciadv.abb8375' : {'all' : 28, 'core' : 13},
          '10.1126/sciadv.1602743' : {'all' : 28, 'core' : 11},
          '10.1126/science.1249802' : {'all' : 27, 'core' : 22},
          '10.1126/science.abe2824' : {'all' : 26, 'core' : 18},
          '10.1126/sciadv.aau1946' : {'all' : 26, 'core' : 18},
          '10.1126/sciadv.1602273' : {'all' : 26, 'core' : 17},
          '10.1126/science.1248905' : {'all' : 26, 'core' : 13},
          '10.1126/science.1103346' : {'all' : 25, 'core' : 19},
          '10.1126/science.1246164' : {'all' : 25, 'core' : 17},
          '10.1126/science.1154643' : {'all' : 25, 'core' : 15},
          '10.1126/sciadv.aat9331' : {'all' : 25, 'core' : 15},
          '10.1126/sciadv.aap8598' : {'all' : 25, 'core' : 14},
          '10.1126/sciadv.abj9786' : {'all' : 25, 'core' : 12},
          '10.1126/science.aay5820' : {'all' : 24, 'core' : 19},
          '10.1126/sciadv.1602811' : {'all' : 23, 'core' : 19},
          '10.1126/sciadv.abb8780' : {'all' : 21, 'core' : 13},
          '10.1126/sciadv.abf2447' : {'all' : 20, 'core' : 14},
          '10.1126/sciadv.1700930' : {'all' : 20, 'core' : 12},
          '10.1126/science.aay6779' : {'all' : 19, 'core' : 11},
          '10.1126/sciadv.abg9158' : {'all' : 18, 'core' : 17}}




def harvestarticle(jnl, rec, i, l, r):
    sleepingtime = random.randint(30, 150)
    ejlmod3.printprogress('-', [[i, l], [rec['artlink']], ['%isec' % (sleepingtime)], [r]])
    try:
        driver.get(rec['artlink'])
        artpage = BeautifulSoup(driver.page_source, features="lxml")
        #artpage = BeautifulSoup(scraper.get(rec['artlink']).text, features="lxml")
    except:
        print("retry in 900 seconds")
        time.sleep(900)
        driver.get(rec['artlink'])
        artpage = BeautifulSoup(driver.page_source, features="lxml")
        #artpage = BeautifulSoup(scraper.get(rec['artlink']).text, features="lxml")
    #meta-tags 
    ejlmod3.metatagcheck(rec, artpage, ['dc.Title', 'dc.Date'])
    if 'tit' in rec:
        if rec['tit'] in ['In Science Journals']:
            return False
    else:
        print(artpage.text)
    #volume, issue
    for span in artpage.find_all('span', attrs = {'property' : 'volumeNumber'}):
        rec['vol'] = span.text.strip()
    for span in artpage.find_all('span', attrs = {'property' : 'issueNumber'}):
        rec['issue'] = span.text.strip()
    #pages
    for meta in artpage.find_all('meta', attrs = {'name' : 'dc.Identifier'}):
        if meta.has_attr('scheme'):
            if meta['scheme'] == 'publisher-id':
                rec['p1'] = meta['content']
            elif meta['scheme'] == 'doi':
                rec['doi'] = meta['content']
    #authors and affiliations
    for div in artpage.find_all('div', attrs = {'property' : 'author'}):
        name = False
        for span in div.find_all('span', attrs = {'property' : 'familyName'}):
            name = span.text.strip()
        for span in div.find_all('span', attrs = {'property' : 'givenName'}):
            name += ', ' + span.text.strip()
        if name:
            rec['autaff'].append([name])
            for a in div.find_all('a', attrs = {'class' : 'orcid-id'}):
                rec['autaff'][-1].append(re.sub('.*\/', 'ORCID:', a['href']))
            for div2 in div.find_all('div', attrs = {'property' : ['affiliation', 'organization']}):
                rec['autaff'][-1].append(div2.text.strip())
        else:
            rec['autaff'].append([re.sub('View all articles by this author', '', div.text.strip())])
            print('\n  added "%s" as author - is it ok or a collaboration or ...?\n' % (rec['autaff'][-1][0]))
    #abstract
    for section in artpage.find_all('section', attrs = {'id' : 'abstract'}):
        for h2 in section.find_all('h2'):
            h2.decompose()
        rec['abs'] = section.text.strip()
    #strange page
    if not 'p1' in list(rec.keys()):
        rec['p1'] = re.sub('.*\.', '', rec['doi'])
    #references
    divs = artpage.find_all('div', attrs = {'class' : 'labeled'})
    if not len(divs):
         divs = artpage.find_all('div', attrs = {'role' : 'doc-biblioentry'})
    if not len(divs):
        for section in artpage.find_all('section', attrs = {'id'  : 'bibliography'}):
            divs = section.find_all('div', attrs = {'role' : 'listitem'})
    for div in divs:
        for d2 in div.find_all('div', attrs = {'class' : 'label'}):
            d2t = d2.text
            d2.replace_with('[%s] ' % d2t)
        for a in div.find_all('a'):
            if a.has_attr('href'):
                at = a.text.strip()
                ah = a['href']
                if at == 'Crossref':
                    a.replace_with(re.sub('.*doi.org\/', ', DOI: ', ah))
                else:
                    a.decompose()
        rec['refs'].append([('x', div.text.strip())])
    #PDF    
    for a in artpage.find_all('a', attrs = {'data-toggle' : 'tooltip'}):
        if a.has_attr('href') and re.search('doi\/pdf', a['href']):
            if jnl == 'research':
                rec['pdf_url'] = 'https://spj.science.org' + a['href']
            else:
                rec['pdf_url'] = 'https://science.org' + a['href']
    if 'license' in rec and 'pdf_url' in rec:
        targetfilename = '%s/%s/%s.pdf' % (pdfpath, re.sub('\/.*', '', rec['doi']), re.sub('[\(\)\/]', '_', rec['doi']))
        if os.path.isfile(targetfilename):
            print('     %s already exists' % (targetfilename))
        else:
            savedfilename = '%s/%s.pdf' % (downloadpath, re.sub('.*uri=(.*)&.*', r'\1', rec['pdf_url']))
            savedfilename = '%s/%s.pdf' % (downloadpath, re.sub('.*\/(.*)\?.*', r'\1', rec['pdf_url']))
            if not os.path.isfile(savedfilename):            
                print('     get %s from %s' % (savedfilename, rec['pdf_url']))
                driver.get(rec['pdf_url'])
                time.sleep(30)
            if os.path.isfile(savedfilename):
                print('     mv %s to %s' % (savedfilename, targetfilename))
                os.system('mv %s %s' % (savedfilename, targetfilename))
                time.sleep(300)
            else:
                print('     COULD NOT DOWNLOAD PDF')
    ejlmod3.globallicensesearch(rec, artpage)
    time.sleep(sleepingtime)
    return True


i = 0
recs = []
missingjournals = []
for doi in sample:
    i += 1
    ejlmod3.printprogress('-', [[i, len(sample)], [doi, sample[doi]['all'], sample[doi]['core']], [len(recs)]])
    if sample[doi]['core'] < corethreshold:
        print('   too, few citations')
        continue
    if skipalreadyharvested and doi in alreadyharvested:
        print('   already in backup')
        continue
    if re.search('10.1126\/science\.', doi):
        jnlname = 'Science'
        jnl = 'science'
    elif re.search('10.1126\/sciadv', doi):
        jnlname = 'Sci.Adv.'
        jnl = 'sciadv'
    else:
        missingjournals.append(meta['content'])
        continue

    rec = {'tc' : 'P', 'jnl' : jnlname, 'autaff' : [], 'note' : [],
           'refs' : [], 'doi' : doi}
    rec['artlink'] = 'https://doi.org/' + doi
    rec['artlink'] = 'https://www.science.org/doi/' + doi
    #check article pages
    if harvestarticle(jnl, rec, i, len(sample), len(recs)):
        #sample note
        rec['note'] = ['reharvest_based_on_refanalysis',
                       '%i citations from INSPIRE papers' % (sample[doi]['all']),
                       '%i citations from CORE INSPIRE papers' % (sample[doi]['core'])]
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
        ejlmod3.writenewXML(recs[((len(recs)-1) // bunchsize)*bunchsize:], publisher, jnlfilename + '--%04i' % (1 + (len(recs)-1) // bunchsize), retfilename='retfiles_special')
        if missingjournals:
            print('\nmissing journals:', missingjournals, '\n')

