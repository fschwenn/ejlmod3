# -*- coding: UTF-8 -*-
#program to harvest individual DOIs from ACM journals
# FS 2024-06-06

import sys
import os
import ejlmod3
import re
import time
from bs4 import BeautifulSoup
import undetected_chromedriver as uc

publisher = 'Association for Computing Machinery'

skipalreadyharvested = False
bunchsize = 10
corethreshold = 15

jnlfilename = 'ACM_QIS_retro.' + ejlmod3.stampoftoday()
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

sample = {'10.1145/3065386' : {'all' : 101, 'core' :      59},
          '10.1145/3183895.3183901' : {'all' :  63, 'core' :      60},
          '10.1145/3341302.3342070' : {'all' :  48, 'core' :      41},
          '10.1145/285861.285868' : {'all' :  37, 'core' :      17},
          '10.1145/3422622' : {'all' :  36, 'core' :      23},
          '10.1145/3233188.3233224' : {'all' :  35, 'core' :      33},
          '10.1145/3386367.3431293' : {'all' :  27, 'core' :      23},
          '10.1145/3485628' : {'all' :  27, 'core' :      12},
          '10.1137/1.9781611975482.87' : {'all' :  21, 'core' :      21},
          '10.1145/3345312.3345497' : {'all' :  20, 'core' :      17}}

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
    rec = {'tc' : 'P', 'artlink' : 'https://dl.acm.org/doi/' + doi, 'doi' : doi,
           'note' : []}


    time.sleep(10)
    driver.get(rec['artlink'])
    artpage = BeautifulSoup(driver.page_source, features="lxml")

    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #keywords
            if meta['name'] == 'dc.Subject':
                rec['keyw'] = re.split(' *; *', meta['content'])
            #date
            elif meta['name'] == 'dc.Date':
                rec['date'] = re.sub('.*?(\d\d\d\\d\-\d+\-\d+)$', r'\1', meta['content'])
            #type
            elif meta['name'] == 'dc.Type':
                rec['note'].append(meta['content'])
            #article no
            elif meta['name'] == 'dc.Identifier':
                if meta.has_attr('scheme') and meta['scheme'] == 'article-no':
                    rec['p1'] = meta['content']
            #journal
            elif meta['name'] == 'citation_journal_title':
                jnl = meta['content']
                if jnl == 'Communications of the ACM':
                    rec['jnl'] = 'Commun.ACM'
                elif jnl == 'ACM SIGACT News':
                    rec['jnl'] = 'Sigact News'
                elif jnl == 'Journal of the ACM (JACM)':
                    rec['jnl'] = 'J.Assoc.Comput.Machinery'
                elif jnl == 'ACM Transactions on Mathematical Software (TOMS)':
                    rec['jnl'] = 'ACM Trans.Math.Software'
                elif jnl == 'ACM Computing Surveys (CSUR)':
                    rec['jnl'] = 'ACM Comput.Surveys'
                elif jnl == 'Proceedings of the ACM on Programming Languages':
                    rec['jnl'] = 'BOOK'
                    rec['tc'] = 'C'
                elif jnl == 'ACM Journal on Emerging Technologies in Computing Systems (JETC)':
                    rec['jnl'] = 'ACM Journal on Emerging Technologies in Computing Systems (JETC)'
                elif jnl == 'ACM Transactions on Quantum Computing':
                    rec['jnl'] = 'ACM Trans.Quant.Comput.'
                elif jnl == 'ACM SIGCOMM Computer Communication Review':
                    rec['jnl'] = 'ACM SIGCOMM Computer Communication Review'
                elif jnl == 'Journal of Experimental Algorithmics (JEA)':
                    rec['jnl'] = 'Journal of Experimental Algorithmics (JEA)'
                elif jnl == 'ACM SIGPLAN Notices':
                    rec['jnl'] = 'SIGPLAN Not.'
                elif jnl == '':
                    rec['jnl'] = ''
                else:
                    missingjournals.append('"%s" %s' % (jnl, doi))                    
    if not 'jnl' in rec:
        for nav in artpage.find_all('nav', attrs = {'aria-label' : 'Breadcrumbs'}):
            lis = nav.find_all('li')
            if len(lis) > 2:
                if lis[1].text.strip() == 'Conferences':
                    rec['jnl'] = 'BOOK'
                    rec['tc'] = 'C'
            for li in lis[2:]:
                rec['note'].append(li.text.strip())

    #date
    if not 'date' in rec:
        for span in artpage.find_all('span', attrs = {'class' : 'CitationCoverDate'}):
            rec['date'] = span.text.strip()
    #tile
    for h1 in artpage.find_all('h1', attrs = {'class' : 'citation__title'}):
        rec['tit'] = h1.text.strip()
    #authors
    for ul in artpage.find_all('ul', attrs = {'ariaa-label' : 'authors'}):
        rec['autaff'] = []
        for li in ul.find_all('li'):
            for span in li.find_all('span', attrs = {'class' : 'loa__author-name'}):
                rec['autaff'].append([span.text.strip()])
            for span in li.find_all('span', attrs = {'class' : 'loa_author_inst'}):
                rec['autaff'][-1].append(span.text.strip())
    #abstract
    for div in artpage.find_all('div', attrs = {'class' : 'abstractInFull'}):
        for sup in div.find_all('sup'):
            supt = sup.text.strip()
            sup.replace_with('$^{%s}$' % (supt))
        for sub in div.find_all('sub'):
            subt = sub.text.strip()
            sub.replace_with('$_{%s}$' % (subt))
        rec['abs'] = div.text.strip()
    #references
    for ol in artpage.find_all('ol', attrs = {'class' : 'references__list'}):
        if not 'refs' in rec:
            rec['refs'] = []
            lis = ol.find_all('li')
        for li in lis:
            refno = ''
            if li.has_attr('id'):
                refno = '[%s] ' % (re.sub('^0*', '', re.sub('\D', '', li['id'])))
            for a in li.find_all('a'):
                if a.has_attr('href') and re.search('doi=10.*key=10', a['href']):
                    rdoi = re.sub('.*key=', '', a['href'])
                    rdoi = re.sub('%28', '(', rdoi)
                    rdoi = re.sub('%29', ')', rdoi)
                    rdoi = re.sub('%2F', '/', rdoi)
                    rdoi = re.sub('%3A', ':', rdoi)
                    a.replace_with(', DOI: %s' % (rdoi))
                else:
                    a.decompose()
            rec['refs'].append([('x', refno + li.text.strip())])
    #FFT
    for li in artpage.find_all('li', attrs = {'class' : 'pdf-file'}):
        for a in li.find_all('a', attrs = {'title' : 'PDF'}):
            rec['hidden'] = 'https://dl.acm.org' + a['href']
    #pages
    for div in artpage.find_all('div', attrs = {'class' : 'pageRange'}):
        rec['p1'] = re.sub('\D.*?(\d+).*', r'\1', div.text.strip())
        rec['p2'] = re.sub('.*\D(\d+).*', r'\1', div.text.strip())
    if not 'p1' in rec:
        for span in artpage.find_all('span', attrs = {'class' : 'epub-section__pagerange'}):
            div2t = span.text.strip()
            if re.search(' pp +\d+\D\d+', ' '+div2t):
                pages = re.split('\D', re.sub('.*pp +(\d+\D\d+).*', r'\1', div2t))
                rec['p1'] = pages[0]
                rec['p2'] = pages[1]


    if not 'jnl' in rec:
        continue










    
    #sample note
    rec['note'] = ['reharvest_based_on_refanalysis',
                   '%i citations from INSPIRE papers' % (sample[doi]['all']),
                   '%i citations from CORE INSPIRE papers' % (sample[doi]['core'])]
    ejlmod3.printrecsummary(rec)
    recs.append(rec)
    ejlmod3.writenewXML(recs[((len(recs)-1) // bunchsize)*bunchsize:], publisher, jnlfilename + '--%04i' % (1 + (len(recs)-1) // bunchsize), retfilename='retfiles_special')

