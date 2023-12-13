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
skipalreadyharvested = True
bunchsize = 10

jnlfilename = 'TANDF_QIS_retro.' + ejlmod3.stampoftoday()
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)


options = uc.ChromeOptions()
options.binary_location='/usr/bin/google-chrome'
#options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)


sample = {'10.1080/01969727308546046' : {'all' : 14 , 'core' : 14},
          '10.1080/00268976.2012.668289' : {'all' : 12 , 'core' : 12},
          '10.1080/09500340601101575' : {'all' : 16 , 'core' : 16},
          '10.1080/00018730902831009' : {'all' : 19 , 'core' : 19},
          '10.1080/00107514.2016.1148333' : {'all' : 16 , 'core' : 16},
          '10.1080/01621459.1927.10502953' : {'all' : 30 , 'core' : 30},
          '10.1080/09500340.2013.856482' : {'all' : 28 , 'core' : 28},
          '10.1080/09500349414552171' : {'all' : 239 , 'core' : 239},
          '10.1080/09500340008235138' : {'all' : 26 , 'core' : 26},
          '10.1080/00107514.2014.964942' : {'all' : 174 , 'core' : 174},
          '10.1080/00401706.1970.10488634' : {'all' : 21 , 'core' : 21},
          '10.1080/03610919008812866' : {'all' : 17 , 'core' : 17},
          '10.1080/14789940801912366' : {'all' : 379 , 'core' : 379},
          '10.1080/00018730802218067' : {'all' : 21 , 'core' : 21},
          '10.1080/01621459.1954.10501232' : {'all' : 30 , 'core' : 30},
          '10.1080/01621459.1979.10481038' : {'all' : 35 , 'core' : 35},
          '10.1080/10448639208218770' : {'all' : 40 , 'core' : 40},
          '10.1080/23746149.2017.1343097' : {'all' : 41 , 'core' : 41},
          '10.1080/09500340701352581' : {'all' : 25 , 'core' : 25},
          '10.1080/23307706.2017.1397554' : {'all' : 29 , 'core' : 29},
          '10.1080/03610927808827599' : {'all' : 45 , 'core' : 45},
          '10.1080/09500340903477756' : {'all' : 32 , 'core' : 32},
          '10.1080/14786440608635919' : {'all' : 21 , 'core' : 21},
          '10.1080/14786449508620739' : {'all' : 56 , 'core' : 56},
          '10.1198/106186006X136976' : {'all' : 32 , 'core' : 32},
          '10.1080/01621459.1951.10500769' : {'all' : 44 , 'core' : 44},
          '10.1080/00107514.2018.1488463' : {'all' : 43 , 'core' : 43},
          '10.1080/00405000.2013.829687' : {'all' : 53 , 'core' : 53},
          '10.1080/14786437208229210' : {'all' : 37 , 'core' : 37},
          '10.1080/00107510701342313' : {'all' : 46 , 'core' : 46},
          '10.1080/09500340108240904' : {'all' : 21 , 'core' : 21},
          '10.1080/09500349414552221' : {'all' : 35 , 'core' : 35},
          '10.1080/23746149.2018.1457981' : {'all' : 29 , 'core' : 29},
          '10.1080/09500348714550721' : {'all' : 65 , 'core' : 65},
          '10.1080/00107514.2019.1631555' : {'all' : 45 , 'core' : 45},
          '10.1080/09500340410001730986' : {'all' : 23 , 'core' : 23},
          '10.1080/00018736100101281' : {'all' : 73 , 'core' : 73},
          '10.1080/14786440009463897' : {'all' : 44 , 'core' : 44},
          '10.1080/00107510010002599' : {'all' : 51 , 'core' : 51},
          '10.1080/23746149.2016.1230476' : {'all' : 74 , 'core' : 74},
          '10.1080/00268976400100041' : {'all' : 41 , 'core' : 41},
          '10.1080/14786440109462720' : {'all' : 97 , 'core' : 97},
          '10.1080/18811248.2011.9711675' : {'all' : 226 , 'core' : 226},
          '10.1080/01621459.1949.10483310' : {'all' : 63 , 'core' : 63},
          '10.1080/14786435.2011.609152' : {'all' : 63 , 'core' : 63},
          '10.1080/09500349314551321' : {'all' : 89 , 'core' : 89},
          '10.1080/14786440108520416' : {'all' : 40 , 'core' : 40},
          '10.1080/09500340.2016.1148212' : {'all' : 74 , 'core' : 74},
          '10.1080/01621459.1963.10500830' : {'all' : 77 , 'core' : 77},
          '10.1080/0950034021000011536' : {'all' : 76 , 'core' : 76},
          '10.1080/00018732.2010.514702' : {'all' : 172 , 'core' : 172},
          '10.1080/00018730701223200' : {'all' : 195 , 'core' : 195},
          '10.1080/14786440308520318' : {'all' : 58 , 'core' : 58},
          '10.1080/00107510601101934' : {'all' : 116 , 'core' : 116},
          '10.1080/00107510802091298' : {'all' : 111 , 'core' : 111},
          '10.1080/00018732.2015.1055918' : {'all' : 244 , 'core' : 244},
          '10.1080/00107151031000110776' : {'all' : 135 , 'core' : 135},
          '10.1080/00268976.2011.552441' : {'all' : 90 , 'core' : 90},
          '10.1080/00107514.2016.1201896' : {'all' : 227 , 'core' : 227}}

i = 0
recs = []
missingjournals = []
for doi in sample:
    artlink = 'https://iopscience.iop.org/article/' + doi
    rec = {'doi' : doi, 'tc' : 'P', 'autaff' : [], 'keyw' : [], 'refs' : [], 'note' : []}
    i += 1
    ejlmod3.printprogress('-', [[i, len(sample)], [doi, sample[doi]['all'], sample[doi]['core']], [len(recs)]])
    if sample[doi]['core'] < 20:
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

