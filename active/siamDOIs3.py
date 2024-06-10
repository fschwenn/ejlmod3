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


sample = {'10.1137/1.9781611975482.107' : {'all' : 13 , 'core' : 13},
          '10.1137/1.9781611975482.87' : {'all' : 14 , 'core' : 14},
          '10.1137/1.9780898719598' : {'all' : 21 , 'core' : 21},
          '10.1137/141000671' : {'all' : 204 , 'core' : 204},
          '10.1137/080739379' : {'all' : 14 , 'core' : 14},
          '10.1137/090760155' : {'all' : 28 , 'core' : 28},
          '10.1137/S0097539704412910' : {'all' : 13 , 'core' : 13},
          '10.1137/S0895479896305696' : {'all' : 22 , 'core' : 22},
          '10.1137/1116025' : {'all' : 16 , 'core' : 16},
          '10.1137/s0097539796300921' : {'all' : 166 , 'core' : 166},
          '10.1137/S0097539796300921' : {'all' : 166 , 'core' : 166},
          '10.1137/S00361445024180' : {'all' : 29 , 'core' : 29},
          '10.1137/S1052623400366802' : {'all' : 22 , 'core' : 22},
          '10.1137/0218053' : {'all' : 14 , 'core' : 14},
          '10.1137/040605072' : {'all' : 15 , 'core' : 15},
          '10.1137/050644719' : {'all' : 17 , 'core' : 17},
          '10.1137/18M1174726' : {'all' : 26 , 'core' : 26},
          '10.1137/S0097539703436345' : {'all' : 20 , 'core' : 20},
          '10.1137/0907058' : {'all' : 36 , 'core' : 36},
          '10.1137/S0097539705447372' : {'all' : 20 , 'core' : 20},
          '10.1137/050643684' : {'all' : 30 , 'core' : 30},
          '10.1137/0217014' : {'all' : 29 , 'core' : 29},
          '10.1137/S0097539796302452' : {'all' : 25 , 'core' : 25},
          '10.1137/090752286' : {'all' : 53 , 'core' : 53},
          '10.1137/s0036144598347011' : {'all' : 315 , 'core' : 315},
          '10.1137/S0036144598347011' : {'all' : 315 , 'core' : 315},
          '10.1137/18M1231511' : {'all' : 36 , 'core' : 36},
          '10.1137/090745854' : {'all' : 41 , 'core' : 41},
          '10.1137/S0097539705447323' : {'all' : 42 , 'core' : 42},
          '10.1137/S0097539700377025' : {'all' : 40 , 'core' : 40},
          '10.1137/050632981' : {'all' : 39 , 'core' : 39},
          '10.1137/1025002' : {'all' : 129 , 'core' : 129},
          '10.1137/0111030' : {'all' : 96 , 'core' : 96},
          '10.1137/080734479' : {'all' : 49 , 'core' : 49},
          '10.1137/1038003' : {'all' : 70 , 'core' : 70},
          '10.1137/S0097539705447311' : {'all' : 75 , 'core' : 75},
          '10.1137/S0097539704445226' : {'all' : 70 , 'core' : 70},
          '10.1137/0916069' : {'all' : 103 , 'core' : 103},
          '10.1137/050644756' : {'all' : 86 , 'core' : 86},
          '10.1137/S0097539796298637' : {'all' : 105 , 'core' : 105},
          '10.1137/S0097539799359385' : {'all' : 105 , 'core' : 105}}
sample = {'10.1137/090752286' : {'all' : 72, 'core' : 31},
          '10.1137/07070111X' : {'all' : 43, 'core' : 17},
          '10.1137/18M1174726' : {'all' : 33, 'core' : 23},
          '10.1137/0218053' : {'all' : 25, 'core' : 24},
          '10.1137/S0097539704412910' : {'all' : 24, 'core' : 19},
          '10.1137/050644719' : {'all' : 22, 'core' : 19},
          '10.1137/040605072' : {'all' : 20, 'core' : 19},
          '10.1137/1116025' : {'all' : 20, 'core' : 16},
          '10.1137/1.9781611975482.87' : {'all' : 19, 'core' : 19},
          '10.1137/S0097539799355053' : {'all' : 18, 'core' : 18},
          '10.1137/080739379' : {'all' : 17, 'core' : 13},
          '10.1137/1.9781611975482.107' : {'all' : 14, 'core' : 14}}




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




