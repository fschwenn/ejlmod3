#!/usr/bin/python
# -*- coding: UTF-8 -*-
#program to harvest individual DOIs from Taylor and Francis
# FS 2023-12-13

import os
import sys
import ejlmod3
import re
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import cloudscraper
import cookiecache
import requests
import random

def tfstrip(x): return x.strip()

publisher = 'Taylor and Francis'
skipalreadyharvested = False
bunchsize = 10
corethreshold = 15

jnlfilename = 'TANDF_QIS_retro.' + ejlmod3.stampoftoday()
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)


options = uc.ChromeOptions()
options.binary_location='/usr/bin/google-chrome'
#options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)


sample = {'10.1080/00107514.2016.1201896' : {'all' : 294, 'core' :     106},
          '10.1080/00018730701223200' : {'all' : 248, 'core' :      70},
          '10.1080/09500349314551321' : {'all' : 118, 'core' :      48},
          '10.1080/01621459.1963.10500830' : {'all' : 106, 'core' :      67},
          '10.1080/01621459.1949.10483310' : {'all' :  86, 'core' :      43},
          '10.1080/00107514.2019.1631555' : {'all' :  62, 'core' :      29},
          '10.1080/00107514.2018.1488463' : {'all' :  56, 'core' :      27},
          '10.1080/00268976400100041' : {'all' :  52, 'core' :      38},
          '10.1080/23746149.2018.1457981' : {'all' :  35, 'core' :      26}}

    
i = 0
recs = []
missingjournals = []
for doi in sample:
    artlink = 'https://iopscience.iop.org/article/' + doi
    rec = {'doi' : doi, 'tc' : 'P', 'autaff' : [], 'keyw' : [], 'refs' : [], 'note' : []}
    i += 1
    ejlmod3.printprogress('-', [[i, len(sample)], [doi, sample[doi]['all'], sample[doi]['core']], [len(recs)]])
    if sample[doi]['core'] < corethreshold:
        print('   too, few citations')
        continue
    if skipalreadyharvested and doi in alreadyharvested:
        print('   already in backup')
        continue
    try:
        driver.get('http://www.tandfonline.com/doi/full/%s' % (rec['doi']))
        apage = BeautifulSoup(driver.page_source, features="lxml")
        time.sleep(random.randint(20,100))
        driver.get('http://www.tandfonline.com/doi/ref/%s' % (rec['doi']))
        rpage = BeautifulSoup(driver.page_source, features="lxml")
        #apage = BeautifulSoup(scraper.get('http://www.tandfonline.com/doi/full/%s' % (rec['doi'])).text, features="lxml")
        time.sleep(random.randint(20,100))
        #rpage = BeautifulSoup(scraper.get('http://www.tandfonline.com/doi/ref/%s' % (rec['doi'])).text, features="lxml")
    except:
        print('try without references')
        time.sleep(random.randint(50,90))
        driver.get('http://www.tandfonline.com/abs/%s' % (rec['doi']))
        apage = BeautifulSoup(driver.page_source, features="lxml")
        #apage = BeautifulSoup(scraper.get('http://www.tandfonline.com/full/ref/%s' % (rec['doi'])).text, features="lxml")
        rpage = apage
    if re.search('Cloudflare', apage.text):
        print('Cloudflare :(')
        sys.exit(0)
    ejlmod3.metatagcheck(rec, apage, ['dc.Title', 'dc.Date', 'keywords'])
    jnl = doi
    for meta in apage.find_all('meta', attrs = {'name' : 'dc.Identifier', 'scheme' : 'coden'}):
        print('    ', meta['content'])
        jnl = re.sub(', Vol.*', '', meta['content'])
        if jnl in ['Molecular Physics']:
            rec['jnl'] = 'Mol.Phys.'
        elif jnl in ['Contemporary Physics']:
            rec['jnl'] = 'Contemp.Phys.'
        elif jnl in ['Journal of the American Statistical Association']:
            rec['jnl'] = 'J.Am.Statist.Assoc.'
        elif jnl in ['Journal of Modern Optics']:
            rec['jnl'] = 'J.Mod.Opt.'
        elif jnl in ['Technometrics']:
            rec['jnl'] = 'Technometrics'
        elif jnl in ['Advances in Physics']:
            rec['jnl'] = 'Adv.Phys.'
        elif jnl in ['Journal of the American Statistical Association']:
            rec['jnl'] = 'J.Am.Statist.Assoc.'
        elif jnl in ['Neutron News']:
            rec['jnl'] = 'Neutron News'
        elif jnl in ['Philosophical Magazine']:
            rec['jnl'] = 'Phil.Mag.'
        elif jnl in ['Journal of Modern Optics, November 20, 2002']:
            rec['jnl'] = 'J.Mod.Opt.'
        elif jnl in ['']:
            rec['jnl'] = ''
        elif jnl in ['']:
            rec['jnl'] = ''
        elif jnl in ['']:
            rec['jnl'] = ''
        elif jnl in ['']:
            rec['jnl'] = ''
        if re.search(', Vol\.', meta['content']):
            rec['vol'] = re.sub('.*Vol\. *(\d+).*', r'\1', meta['content'])
        if re.search(', No\.', meta['content']):
            rec['issue'] = re.sub('.*No\. *(\d+).*', r'\1', meta['content'])
        if re.search(', pp\.', meta['content']):
            rec['p1'] = re.sub('.*, pp\. *(\d+).*', r'\1', meta['content'])
            rec['p2'] = re.sub('.*, pp\..*\D(\d+).*', r'\1', meta['content'])
        elif re.search('\d–\d', meta['content']):
            rec['p1'] = re.sub('.*?(\d+)–\d.*', r'\1', meta['content'])
            rec['p2'] = re.sub('.*?\d+–(\d+).*', r'\1', meta['content'])
    if doi in ['10.1080/14786440608635919']:
        rec['jnl'] = 'Phil.Mag.Ser.6'
    elif doi in ['10.1080/14786449508620739']:
        rec['jnl'] = 'Phil.Mag.Ser.5'
    elif doi in ['10.1080/09500340.2013.856482']:
        rec['jnl'] = 'J.Mod.Opt.'
    elif doi in ['10.1080/00107514.2014.964942', '10.1080/00107514.2018.1488463']:
        rec['jnl'] = 'Contemp.Phys.'
    elif doi in ['10.1080/23746149.2017.1343097', '10.1080/23746149.2018.1457981',
                 '10.1080/23746149.2016.1230476']:
        rec['jnl'] = 'Adv.Phys.X'
    elif doi in ['10.1080/03610927808827599']:
        rec['jnl'] = 'Commun.Stat.'
    elif doi in ['10.1198/106186006X136976']:
        rec['jnl'] = 'J.Comp.Graph.Stat.'
    elif doi in ['10.1080/00018732.2015.1055918']:
        rec['jnl'] = 'Adv.Phys.'
    elif doi in ['10.1080/00107514.2016.1201896', '10.1080/00405000.2013.829687',
                 '10.1080/00107514.2019.1631555', '10.1080/00107514.2016.1148333']:
        rec['jnl'] = 'Contemp.Phys.'
    elif doi in ['10.1080/09500340.2016.1148212']:
        rec['jnl'] = 'J.Mod.Opt.'
    elif doi in ['10.1080/23307706.2017.1397554']:
        rec['jnl'] = 'J.Control Decis.'
    elif doi in ['']:
        rec['jnl'] = ''
    elif doi in ['']:
        rec['jnl'] = ''
    elif doi in ['']:
        rec['jnl'] = ''
    elif doi in ['']:
        rec['jnl'] = ''
    elif doi in ['']:
        rec['jnl'] = ''
    time.sleep(random.randint(10,170-120))
    if not 'jnl' in rec:
        missingjournals.append(jnl)
        continue
    #article type
    for div in apage.body.find_all('div', attrs = {'class' : 'toc-heading'}):
        for h3 in div.find_all('h3'):
            rec['note'].append(h3.text.strip())
        for h2 in div.find_all('h2'):
            rec['note'].append(h3.text.strip())
    #year
    for h2 in apage.body.find_all('h2'):
        if re.search('Volume \d.* \d\d\d\d', h2.text):
            rec['year'] = re.sub('.* (\d\d\d\d).*', r'\1', re.sub('\n', ' ', h2.text.strip()))
    #pdf
    #authorstructure
    for span in apage.body.find_all('div', attrs = {'class' : 'hlFld-ContribAuthor'}):
        for div in span.find_all('div', attrs = {'class' : 'entryAuthor'}):
            #author's name
            for a in div.find_all('a', attrs = {'class' : 'author'}):
                rec['autaff'].append([ re.sub('(.*) (.*)', r'\2, \1', a.text.strip()) ])
            #ORCID
            for a in div.find_all('a', attrs = {'class' : 'orcid-author'}):
                rec['autaff'][-1].append(re.sub('.*org\/', 'ORCID:', a['href']))
            for affspan in div.find_all('span', attrs = {'class' : 'overlay'}):
                #EMAIL
                for a in affspan.find_all('a'):
                    if a.has_attr('href') and re.search('@[a-z]', a['href']):
                        rec['autaff'][-1].append(re.sub('.*mailto:', 'EMAIL:', a['href']))
                    a.decompose()
                #correspondance/funding note 
                for corr in div.find_all('span', attrs = {'class' : 'corr-sec'}):
                    corr.decompose()
                for fund in div.find_all('a', attrs = {'class' : 'author-extra-info'}):
                    fund.decompose()
                #AFFILLIATION
                rec['autaff'][-1].append(affspan.text.strip())
    #abstract
    for div in apage.body.find_all('div', attrs = {'class' : 'abstractInFull'}):
        rec['abs'] = div.text.strip()
    if not 'abs' in rec:
        for div in apage.body.find_all('div', attrs = {'class' : 'hlFld-Abstract'}):
            for h2 in div.find_all('h2'):
                h2.decompose()
            rec['abs'] = div.text.strip()        
    #pages
    for span in apage.body.find_all('span', attrs = {'class' : 'contentItemPageRange'}):
        pages = re.sub('[Pp]ages? *', '', span.text).strip()
        try:
            [rec['p1'], rec['p2']] = re.split('\-', pages)
        except:
            rec['p1'] = re.sub('Article: ', '', pages)

    #references
    for ul in rpage.body.find_all('ul', attrs = {'class' : 'references numeric-ordered-list'}):
        rec['refs'] = []
        for li in ul.find_all('li'):
            rdoi = ''
            for a in li.find_all('a'): 
                if a.has_attr('href'):
                    if re.search('Cross[rR]ef', a.text):
                        rdoi = re.sub('.*=', ', DOI: ', a['href'])
                        a.replace_with('')
                    elif re.search('Web of Science', a.text):
                        if not rdoi:
                            rdoi = re.sub('.*doi=', ', DOI: ', a['href'])
                            rdoi = re.sub('\&.*', '', rdoi)
                        a.replace_with('')
                    elif re.search('(PubMed|Taylor|Google Scholar)', a.text):
                        a.replace_with('')                        
            lit = re.sub('\. *$', '', li.text)
            lit = re.sub('\xa0', ' ', li.text)
            lit = re.sub('[\n\t]', ' ', lit)
            lit = re.sub(',\s*,', ',', lit)
            lit = re.sub(',\s*,', ',', lit)
            lit = re.sub('; *(\d)', r', \1', lit)
            if rdoi:
                rdoi = re.sub('%2F', '/', rdoi)
                rdoi = re.sub('%28', '(', rdoi)
                rdoi = re.sub('%29', ')', rdoi)
                rec['refs'].append([('x',  re.sub(',\s*,', ',', lit + rdoi))])
            else:
                rec['refs'].append([('x', lit)])
    if 'note' in rec and rec['note'] and rec['note'][0] in ['Book reviews', 'Essay reviews']:
        print(rec['note'])
        continue
    elif 'note' in rec and rec['note'] and rec['note'][0] in ['Review Article']:
        rec['tc'] += 'R'
    #sample note
    rec['note'] = ['reharvest_based_on_refanalysis',
                   '%i citations from INSPIRE papers' % (sample[doi]['all']),
                   '%i citations from CORE INSPIRE papers' % (sample[doi]['core'])]
    ejlmod3.printrecsummary(rec)
    recs.append(rec)
    ejlmod3.writenewXML(recs[((len(recs)-1) // bunchsize)*bunchsize:], publisher, jnlfilename + '--%04i' % (1 + (len(recs)-1) // bunchsize), retfilename='retfiles_special')
    if missingjournals:
        print('\nmissing journals:', missingjournals, '\n')



if missingjournals:
    print('\nmissing journals:', missingjournals, '\n')

