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

sample = {'10.1145/237814.237866' : {'all' : 652, 'core' : 569},
          '10.1145/359340.359342' : {'all' : 203, 'core' : 156},
          '10.1145/1008908.1008920' : {'all' : 169, 'core' : 128},
          '10.1145/227683.227684' : {'all' : 106, 'core' : 83},
          '10.1145/3065386' : {'all' : 101, 'core' : 59},
          '10.1145/359168.359176' : {'all' : 99, 'core' : 71},
          '10.1145/382780.382781' : {'all' : 96, 'core' : 84},
          '10.1145/279232.279236' : {'all' : 77, 'core' : 43},
          '10.1145/2331130.2331138' : {'all' : 63, 'core' : 18},
          '10.1145/3183895.3183901' : {'all' : 62, 'core' : 59},
          '10.1145/1568318.1568324' : {'all' : 56, 'core' : 39},
          '10.1145/3168822' : {'all' : 52, 'core' : 52},
          '10.1145/581771.581773' : {'all' : 52, 'core' : 33},
          '10.1145/3402192' : {'all' : 49, 'core' : 41},
          '10.1145/502090.502097' : {'all' : 48, 'core' : 37},
          '10.1145/3341302.3342070' : {'all' : 45, 'core' : 38},
          '10.1145/1968.1972' : {'all' : 42, 'core' : 29},
          '10.1145/800157.805047' : {'all' : 41, 'core' : 31},
          '10.1145/502090.502098' : {'all' : 39, 'core' : 30},
          '10.1145/1089014.1089019' : {'all' : 39, 'core' : 13},
          '10.1145/2491956.2462177' : {'all' : 38, 'core' : 37},
          '10.1145/3106700.3106710' : {'all' : 38, 'core' : 34},
          '10.1145/167088.167097' : {'all' : 38, 'core' : 34},
          '10.1145/285861.285868' : {'all' : 37, 'core' : 17},
          '10.1145/380752.380758' : {'all' : 36, 'core' : 19},
          '10.1145/3385412.3386007' : {'all' : 34, 'core' : 34},
          '10.1145/3434318' : {'all' : 34, 'core' : 33},
          '10.1145/3233188.3233224' : {'all' : 34, 'core' : 32},
          '10.1145/3428218' : {'all' : 33, 'core' : 33},
          '10.1145/3009837.3009894' : {'all' : 33, 'core' : 32},
          '10.1145/2885493' : {'all' : 33, 'core' : 23},
          '10.1145/3422622' : {'all' : 32, 'core' : 19},
          '10.1145/3386162' : {'all' : 31, 'core' : 31},
          '10.1145/278298.278306' : {'all' : 30, 'core' : 15},
          '10.1145/3387514.3405853' : {'all' : 29, 'core' : 24},
          '10.1145/2597917.2597939' : {'all' : 28, 'core' : 26},
          '10.1145/3386367.3431293' : {'all' : 27, 'core' : 23},
          '10.1145/258533.258579' : {'all' : 27, 'core' : 23},
          '10.1145/1008731.1008735' : {'all' : 27, 'core' : 17},
          '10.1145/2431211.2431220' : {'all' : 26, 'core' : 24},
          '10.1145/276698.276708' : {'all' : 26, 'core' : 21},
          '10.1145/380752.380757' : {'all' : 26, 'core' : 13},
          '10.1145/3485628' : {'all' : 26, 'core' : 12},
          '10.1145/3406306' : {'all' : 25, 'core' : 22},
          '10.1145/992287.992296' : {'all' : 24, 'core' : 15},
          '10.1145/1268776.1268777' : {'all' : 24, 'core' : 12},
          '10.1145/1008731.1008738' : {'all' : 24, 'core' : 12},
          '10.1145/2499370.2462177' : {'all' : 23, 'core' : 22},
          '10.1145/1219092.1219096' : {'all' : 23, 'core' : 22},
          '10.1145/3550488' : {'all' : 21, 'core' : 21},
          '10.1145/130385.130401' : {'all' : 21, 'core' : 16},
          '10.1145/1039111.1039118' : {'all' : 21, 'core' : 16},
          '10.1145/1052796.1052804' : {'all' : 21, 'core' : 14},
          '10.1145/273865.273901' : {'all' : 21, 'core' : 11},
          '10.1145/3325111' : {'all' : 20, 'core' : 8},
          '10.1145/3387940.3391459' : {'all' : 20, 'core' : 20},
          '10.1145/3464420' : {'all' : 20, 'core' : 17},
          '10.1145/3345312.3345497' : {'all' : 20, 'core' : 17},
          '10.1145/2491533.2491549' : {'all' : 20, 'core' : 17},
          '10.1145/1206035.1206039' : {'all' : 20, 'core' : 16},
          '10.1145/3292548' : {'all' : 20, 'core' : 12},
          '10.1145/3310974' : {'all' : 20, 'core' : 10},
          '10.1145/3287624.3287704' : {'all' : 19, 'core' : 19},
          '10.1145/301250.301347' : {'all' : 19, 'core' : 14},
          '10.1145/1374376.1374407' : {'all' : 18, 'core' : 7},
          '10.1145/237814.237838' : {'all' : 18, 'core' : 11},
          '10.1145/2699464' : {'all' : 17, 'core' : 8},
          '10.1145/3519939.3523433' : {'all' : 17, 'core' : 17},
          '10.1145/3441309' : {'all' : 17, 'core' : 15},
          '10.1145/2213977.2213983' : {'all' : 17, 'core' : 15},
          '10.1145/2432622.2432625' : {'all' : 17, 'core' : 12},
          '10.1145/3319535.3363229' : {'all' : 17, 'core' : 11},
          '10.1145/1008908.1008911' : {'all' : 16, 'core' : 9},
          '10.1145/1236457.1236459' : {'all' : 16, 'core' : 7},
          '10.1145/3377816.3381731' : {'all' : 16, 'core' : 16},
          '10.1145/1536414.1536440' : {'all' : 16, 'core' : 12},
          '10.1145/2817206' : {'all' : 15, 'core' : 7},
          '10.1145/3360546' : {'all' : 15, 'core' : 15}}


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

