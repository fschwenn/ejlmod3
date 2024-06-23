# -*- coding: UTF-8 -*-
#program to harvest individual DOIs from journals from SciPost
# FS 2023-12-28

import os
import ejlmod3
import re
import sys
import urllib.request, urllib.error, urllib.parse
import time
from bs4 import BeautifulSoup

regexpsubm1 = re.compile('[sS]ubmissions')
regexpsubm2 = re.compile('.*\/(\d\d\d\d\.\d\d\d\d\d).*')
skipalreadyharvested = True

publisher = 'SciPost Fundation'


skipalreadyharvested = False
bunchsize = 10
corethreshold = 15

jnlfilename = 'SCIPOST_QIS_retro.' + ejlmod3.stampoftoday()
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)


sample = {'10.21468/SciPostPhys.3.6.039' : {'all' : 77, 'core' : 16},
          '10.21468/SciPostPhys.7.5.069' : {'all' : 53, 'core' : 11},
          '10.21468/SciPostPhys.9.4.044' : {'all' : 49, 'core' : 10},
          '10.21468/SciPostPhys.4.6.043' : {'all' : 44, 'core' : 14},
          '10.21468/SciPostPhys.12.6.201' : {'all' : 43, 'core' : 10},
          '10.21468/SciPostPhys.8.6.083' : {'all' : 41, 'core' : 24},
          '10.21468/SciPostPhysCore.2.2.006' : {'all' : 36, 'core' : 16},
          '10.21468/SciPostPhys.10.6.147' : {'all' : 34, 'core' : 13},
          '10.21468/SciPostPhys.10.2.040' : {'all' : 29, 'core' : 19},
          '10.21468/SciPostPhysLectNotes.31' : {'all' : 27, 'core' : 23},
          '10.21468/SciPostPhys.3.5.033' : {'all' : 26, 'core' : 13}}



i = 0
recs = []
missingjournals = []
for doi in sample:
    rec = {'tc' : 'P', 'note' : [], 'doi' : doi}
    if re.search('SciPostPhysLectNote', doi):
        rec['jnl'] = 'SciPost Phys.Lect.Notes'
    elif re.search('SciPostPhysCore', doi):
        rec['jnl'] = 'SciPost Phys.Core'
    elif re.search('SciPostPhys\.\d', doi):
        rec['jnl'] = 'SciPost Phys.'
    i += 1
    ejlmod3.printprogress('-', [[i, len(sample)], [doi, sample[doi]['all'], sample[doi]['core']], [len(recs)]])
    if sample[doi]['core'] < corethreshold:
        print('   too, few citations')
        continue
    if skipalreadyharvested and doi in alreadyharvested:
        print('   already in backup')
        continue
    artlink = 'https://doi.org/' + doi

    time.sleep(3)
    artpage = BeautifulSoup(urllib.request.urlopen(artlink), features="lxml")
    ejlmod3.globallicensesearch(rec, artpage)
    ejlmod3.metatagcheck(rec, artpage, ['citation_doi', 'citation_pdf_url', 'citation_publication_date', 'citation_title', 'citation_volume', 'citation_issue'])
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #article ID
            if meta['name'] == 'citation_firstpage':
                if rec['jnl'] in ['SciPost Phys.Lect.Notes']:
                    rec['vol'] = re.sub('^0*', '', meta['content'])
                    rec['p1'] = '1'
                else:
                    rec['p1'] = meta['content']
    #abstract
    if not 'abs' in rec:
        for div in artpage.body.find_all('div', attrs = {'class' : 'col-12'}):
            for h3 in div.find_all('h3'):
                if h3.text.strip() == 'Abstract':
                    h3.decompose()
                    rec['abs'] = div.text.strip()
    #arXiv-number
    for a in artpage.body.find_all('a'):
        if a.has_attr('href'):
            if regexpsubm1.search(a.text) and regexpsubm2.search(a['href']):
                rec['arxiv'] = regexpsubm2.sub(r'\1', a['href'])
    #author
    for ul in artpage.body.find_all('ul', attrs = {'class' : 'list-inline'}):
        if ul['class'] != ['list-inline', 'my-2']:
            continue
        rec['auts'] = []
        for li in ul.find_all('li', attrs = {'class' : ['list-inline-item', 'mr-1']}):
            sups = []
            for sup in li.find_all('sup'):
                sups.append('=Aff' + sup.text.strip())
                sup.replace_with('')
            lit = li.text.strip()
            lit = re.sub(', *$', '', lit)
            rec['auts'].append(lit)
            rec['auts'] += sups
    #affiliation
    for ul in artpage.body.find_all('ul', attrs = {'class' : 'list'}):
        if ul['class'] != ['list', 'list-unstyled', 'my-2', 'mx-3']:
            continue
        rec['aff'] = []
        for li in ul.find_all('li'):
            for sup in li.find_all('sup'):
                supnr = sup.text.strip()
                sup.replace_with('')
            rec['aff'].append('Aff%s= %s' % (supnr, li.text.strip()))
    #collaboration
    for p in artpage.body.find_all('p', attrs = {'class' : 'mb-1'}):
        pt = p.text.strip()
        if re.search('[Cc]ollaboration', pt):
            rec['col'] = pt


    #sample note
    rec['note'] = ['reharvest_based_on_refanalysis',
                   '%i citations from INSPIRE papers' % (sample[doi]['all']),
                   '%i citations from CORE INSPIRE papers' % (sample[doi]['core'])]
    ejlmod3.printrecsummary(rec)
    recs.append(rec)
    ejlmod3.writenewXML(recs[((len(recs)-1) // bunchsize)*bunchsize:], publisher, jnlfilename + '--%04i' % (1 + (len(recs)-1) // bunchsize), retfilename='retfiles_special')
    if missingjournals:
        print('\nmissing journals:', missingjournals, '\n')




