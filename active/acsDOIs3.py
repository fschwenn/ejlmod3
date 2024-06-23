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

skipalreadyharvested = False
bunchsize = 10
corethreshold = 15
pdfpath = '/afs/desy.de/group/library/publisherdata/pdf'
downloadpath = '/tmp'
jnlfilename = 'ACS_QIS_retro.' + ejlmod3.stampoftoday()
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

sample = {'10.1021/acs.nanolett.7b03103' : {'all' :  48, 'core' :      12},
          '10.1021/cr2001417' : {'all' :  29, 'core' :      19},
          '10.1021/acs.nanolett.7b05075' : {'all' :  27, 'core' :      11},
          '10.1021/acs.nanolett.9b00900' : {'all' :  26, 'core' :      11},
          '10.1021/acs.nanolett.9b01316' : {'all' :  24, 'core' :      14},
          '10.1021/acs.nanolett.7b03220' : {'all' :  23, 'core' :      11},
          '10.1021/acs.nanolett.5b01306' : {'all' :  19, 'core' :      10},
          '10.1021/acs.nanolett.8b03217' : {'all' :  18, 'core' :      15},
          '10.1021/acsnano.0c03167' : {'all' :  18, 'core' :      13},
          '10.1021/acs.nanolett.0c04771' : {'all' :  18, 'core' :      11}}
    

host = os.uname()[1]
options = uc.ChromeOptions()
options.add_experimental_option("prefs", {"download.prompt_for_download": False, "plugins.always_open_pdf_externally": True, "download.default_directory": downloadpath})
if host == 'l00schwenn':
    options.binary_location='/usr/bin/chromium'
    tmpdir = '/home/schwenn/tmp'
else:
    options.binary_location='/usr/bin/google-chrome'
    options.add_argument('--headless')
    tmpdir = '/tmp'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)


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
    elif jnl == 'ijacsa':
        rec['jnl'] = 'International Journal of Advanced Computer Science and Applications'
        letter = ''
    else:
        missingjournals.append(doi)
        continue
        

    if sample[doi]['core'] < corethreshold:
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
#        for a in artpage.find_all('a', attrs = {'class' : 'pdf-button'}):
#            rec['FFT'] = 'https://pubs.acs.org' + a['href']
        targetfilename = '%s/%s/%s.pdf' % (pdfpath, re.sub('\/.*', '', rec['doi']), re.sub('[\(\)\/]', '_', rec['doi']))
        if os.path.isfile(targetfilename):
            print('     %s already exists' % (targetfilename))
            rec['FFT'] = '%s.pdf' % (re.sub('[\(\)\/]', '_', rec['doi']))
        else:
            for a in artpage.find_all('a', attrs = {'class' : 'pdf-button'}):
                pdfurl = 'https://pubs.acs.org' + a['href'] + '?download=true'
                savedfilereg = re.compile('%s\-.*\d\d\d\d\-%s.*.pdf$' % (re.sub('.* ', '', rec['autaff'][0][0].lower()), re.sub('\W*$', '', re.sub(' .*', '', rec['tit'].lower()))))
            print('     get PDF from %s' % (re.sub('epdf', 'pdf', pdfurl)))
            time.sleep(20)
            #driver.get(pdfurl)
            driver.get(re.sub('epdf', 'pdf', pdfurl))
            #print('        looking for %s\-.*\d\d\d\d\-%s.*.pdf\n\n  --> please click download button <--\n' % (re.sub('.* ', '', rec['autaff'][0][0].lower()), re.sub('\W*$', '', re.sub(' .*', '', rec['tit'].lower()))))
            print('        looking for %s\-.*\d\d\d\d\-%s.*.pdf\n' % (re.sub('.* ', '', rec['autaff'][0][0].lower()), re.sub('\W*$', '', re.sub(' .*', '', rec['tit'].lower()))))
            time.sleep(120)
            found = False
            for j in range(18):
                if not found:
                    for datei in os.listdir(downloadpath):
                        if savedfilereg.search(datei):
                            savedfilename = '%s/%s' % (downloadpath, datei)
                            print('     mv %s to %s' % (savedfilename, targetfilename))
                            os.system('mv "%s" %s' % (savedfilename, targetfilename))
                            rec['FFT'] = '%s.pdf' % (re.sub('[\(\)\/]', '_', rec['doi']))
                            found = True
                if found:
                    break
                else:
                    time.sleep(10)
        
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

