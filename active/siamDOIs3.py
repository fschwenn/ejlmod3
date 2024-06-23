# -*- coding: UTF-8 -*-
#!/usr/bin/python
#program to harvest individual DOIs from journals from SIAM
# FS 2023-12-28
import os
import ejlmod3
import re
import sys
import undetected_chromedriver as uc
import time
from bs4 import BeautifulSoup

publisher = 'Society for Industrial and Applied Mathematics'

skipalreadyharvested = False
bunchsize = 10
corethreshold = 15

jnlfilename = 'SIAM_QIS_retro.' + ejlmod3.stampoftoday()
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)


tc = 'P'

options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)
driver.implicitly_wait(300)


sample = {'10.1137/090752286' : {'all' :  73, 'core' :      32},
          '10.1137/090771806' : {'all' :  35, 'core' :      12},
          '10.1137/18M1174726' : {'all' :  34, 'core' :      24},
          '10.1137/1.9781611975482.87' : {'all' :  21, 'core' :      21},
          '10.1103/PhysRevA.104.013703' : {'all' :  13, 'core' :      10}}




i = 0
recs = []
missingjournals = []
for doi in sample:
    rec = {'tc' : tc, 'note' : [], 'doi' : doi}
    i += 1
    ejlmod3.printprogress('-', [[i, len(sample)], [doi, sample[doi]['all'], sample[doi]['core']], [len(recs)]])
    if sample[doi]['core'] < corethreshold:
        print('   too, few citations')
        continue
    if skipalreadyharvested and doi in alreadyharvested:
        print('   already in backup')
        continue
    artlink = 'https://doi.org/' + doi
    oa = False
    time.sleep(25)
    driver.get(artlink)
    artpage = BeautifulSoup(driver.page_source, features="lxml")
    #abstract
    ejlmod3.metatagcheck(rec, artpage, ['og:description', 'dc.Title'])
    #license
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            if meta['name'] == 'DC.Rights':
                if re.search('under the terms of the Creative Commons 4.0 license', meta['content']):
                    rec['license'] = {'statement' : 'CC-BY-4.0'}
                    oa = 'FFT'
                else:
                    rec['note'].append('DC.Rights:::' + meta['content'])
            elif meta['name'] == 'citation_journal_title':
                if meta['content'] in ['SIAM Journal on Computing']:
                    rec['jnl'] = 'SIAM J.Comput.'
                elif meta['content'] in ['SIAM Review']:
                    rec['jnl'] = 'SIAM Rev.'
                elif meta['content'] in ['SIAM Journal on Optimization']:
                    rec['jnl'] = 'SIAM J.Optim.'
                elif meta['content'] in ['SIAM Journal on Matrix Analysis and Applications']:
                    rec['jnl'] = 'SIAM J.Matrix Anal.Appl.'
                elif meta['content'] in ['SIAM Journal on Scientific and Statistical Computing']:
                    rec['jnl'] = 'SIAM J.Sci.Statist.Comput.'
                elif meta['content'] in ['SIAM Journal on Scientific Computing']:
                    rec['jnl'] = 'SIAM J.Sci.Comput.'
                elif meta['content'] in ['SIAM Journal on Applied Dynamical Systems']:
                    rec['jnl'] = 'SIAM J.Appl.Dynam.Syst.'
                elif meta['content'] in ['Journal of the Society for Industrial and Applied Mathematics']:
                    rec['jnl'] = 'J.Soc.Indust.Appl.Math.'
                else:
                    missingjournals.append( meta['content'] )
    for inp in artpage.body.find_all('input', attrs = {'name' : 'SeriesKey'}):
        coden = inp['value']
        if coden == 'sjmaah':
            jnl = 'SIAM J.Math.Anal.'
        elif coden == 'sjoce3':
            jnl = 'SIAM J.Sci.Comput.'
        elif coden == 'siread':
            jnl = 'SIAM Rev.'
        elif coden == 'smjcat':
            jnl = 'SIAM J.Comput.'
        elif coden == 'smjmap':
            jnl = 'SIAM J.Appl.Math.'
        elif coden == 'sjmael':
            jnl = 'SIAM J.Matrix Anal.Appl.'
        elif coden == 'sjnaam':
            jnl = 'SIAM J.Numer.Anal.'
        elif coden == 'sjdmec':
            jnl = 'SIAM J.Discrete Math.'
        elif coden == 'sjaabq':
            jnl = 'SIAM J.Appl.Alg.Geom.'

    if not 'jnl' in rec:
        continue
    #volume
    for span in artpage.body.find_all('span', attrs = {'property' : 'volumeNumber'}):
        rec['vol'] = span.text.strip()
    for span in artpage.body.find_all('span', attrs = {'property' : 'issueNumber'}):
        rec['issue'] = span.text.strip()
    #authors+affs
    for section in artpage.body.find_all('section', attrs = {'class' : 'core-authors'}):
        rec['autaff'] = []
        for div in section.find_all('div', attrs = {'property' : 'author'}):
            if div.has_attr('typeof') and 'Person' in div['typeof']:
                for div2 in div.find_all('div', attrs = {'class' : 'heading'}):
                    #name
                    author = ''
                    for span in div2.find_all('span', attrs = {'property' : 'givenName'}):
                        author = span.text.strip()
                    for span in div2.find_all('span', attrs = {'property' : 'familyName'}):
                        author += ', ' + span.text.strip()
                    if author:
                        rec['autaff'].append([author])
                    else:
                        print(div)
                        sys.exit(0)
                    #ORCID
                    for a in div2.find_all('a', attrs = {'class' : 'orcid-id'}):
                        if a.has_attr('href'):
                            rec['autaff'][-1].append(re.sub('.*org\/', 'ORCID:', a['href']))
                #affiliation
                for div2 in div.find_all('div', attrs = {'property' : 'affiliation'}):
                    rec['autaff'][-1].append(div2.text.strip())
    #pages
    for div in artpage.body.find_all('div', attrs = {'class' : 'core-pagination'}):
        for span in div.find_all('span', attrs = {'property' : 'pageStart'}):
            rec['p1'] = span.text.strip()
        for span in div.find_all('span', attrs = {'property' : 'pageEnd'}):
            rec['p2'] = span.text.strip()
    #date
    for section in artpage.body.find_all('section', attrs = {'class' : 'core-history'}):
        for div in section.find_all('div'):
            for b in div.find_all('b'):
                if b.text.strip() == 'Published online':
                    b.decompose()
            rec['date'] = re.sub('^ *:', '', div.text.strip())
    #keywords    
    for section in artpage.body.find_all('section', attrs = {'property' : 'keywords'}):
        for h4 in section.find_all('h4'):
            h4t = h4.text.strip()
            if h4t == 'Keywords':
                rec['keyw'] = []
                for a in section.find_all('a'):
                    rec['keyw'].append(a.text.strip())                    
            else:
                for a in section.find_all('a'):
                    rec['note'].append(h4t + ':::' + a.text.strip())
    #references
    for section in artpage.body.find_all('section', attrs = {'id' : 'bibliography'}):
        rec['refs'] = []
        for div in section.find_all('div', attrs = {'role' : 'listitem'}):
            ref = []            
            for a in div.find_all('a'):
                ats = a.text.strip()
                if ats in ['Google Scholar', 'ISI']:
                    a.decompose()
                elif ats == 'Crossref':
                    if a.has_attr('href'):
                        rdoi = re.sub('.*doi.org\/', '', a['href'])
                        ref.append(('a', 'doi:'+rdoi))
                        a.replace_with(', DOI: ' + rdoi)
                        for div2 in div.find_all('div', attrs = {'class' : 'label'}):
                            ref.append(('o', re.sub('\.$', '', div2.text.strip())))
                    else:
                        a.decompose()
            ref.append(('x', div.text.strip()))
            rec['refs'].append(ref)
    #pdf
    for div in artpage.body.find_all('div', attrs = {'class' : 'meta-panel__access'}):
        divt = div.text.strip()
        print('   OA : ' + divt)
        if divt == 'Open access':
            oa = 'FFT'
        elif divt == 'Free access':
            oa = 'hidden'

        if oa:
            rec[oa] = 'https://epubs.siam.org/doi/pdf/%s?download=true' % (rec['doi'])            



    #sample note
    rec['note'] = ['reharvest_based_on_refanalysis',
                   '%i citations from INSPIRE papers' % (sample[doi]['all']),
                   '%i citations from CORE INSPIRE papers' % (sample[doi]['core'])]
    ejlmod3.printrecsummary(rec)
    recs.append(rec)
    ejlmod3.writenewXML(recs[((len(recs)-1) // bunchsize)*bunchsize:], publisher, jnlfilename + '--%04i' % (1 + (len(recs)-1) // bunchsize), retfilename='retfiles_special')
    if missingjournals:
        print('\nmissing journals:', missingjournals, '\n')




