# -*- coding: UTF-8 -*-
# crawls iop web page to get metadata of individual IOP articles
#
# FS 2023-12-06

import os
import sys
import ejlmod3
import re
import time
from bs4 import BeautifulSoup
import urllib.request, urllib.error, urllib.parse
import undetected_chromedriver as uc

publisher = 'IOP'
regexpiopurl = re.compile('http...iopscience.iop.org.')
regexpdxdoi = re.compile('http...dx.doi.org.')

skipalreadyharvested = False
bunchsize = 10
corethreshold = 15

jnlfilename = 'IOP_QIS_retro.' + ejlmod3.stampoftoday() + 'C'
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)


#driver
host = os.uname()[1]
if host == 'l00schwenn':
    options = uc.ChromeOptions()
    options.binary_location='/usr/bin/chromium'
    chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
    driver = uc.Chrome(version_main=chromeversion, options=options)
else:
    options = uc.ChromeOptions()
    options.binary_location='/usr/bin/chromium-browser'
    options.add_argument('--headless')
    chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
    driver = uc.Chrome(version_main=chromeversion, options=options)
    driver.implicitly_wait(30)

sample = {'10.1088/1367-2630/7/1/215' : {'all' : 21, 'core' : 19},
          '10.1088/1367-2630/18/4/043021' : {'all' : 21, 'core' : 19},
          '10.1088/1367-2630/18/12/123007' : {'all' : 21, 'core' : 18},
          '10.1088/2058-9565/aa5f8d' : {'all' : 21, 'core' : 17},
          '10.1088/1367-2630/ab193d' : {'all' : 21, 'core' : 17},
          '10.1088/1367-2630/ab1800' : {'all' : 21, 'core' : 17},
          '10.1088/1751-8113/40/28/S16' : {'all' : 21, 'core' : 16},
          '10.1088/1751-8113/49/11/115302' : {'all' : 21, 'core' : 14},
          '10.1088/1751-8113/41/35/352001' : {'all' : 21, 'core' : 14},
          '10.1088/1367-2630/ab783d' : {'all' : 21, 'core' : 14},
          '10.1088/1367-2630/aa8fe3' : {'all' : 21, 'core' : 14},
          '10.1209/0295-5075/130/50001' : {'all' : 21, 'core' : 13},
          '10.1088/2040-8986/ab05a8' : {'all' : 21, 'core' : 11},
          '10.1088/1367-2630/aaec34' : {'all' : 20, 'core' : 19},
          '10.1088/1751-8121/aaf54d' : {'all' : 20, 'core' : 18},
          '10.1088/1742-6596/698/1/012003' : {'all' : 20, 'core' : 18},
          '10.1088/1367-2630/aa573a' : {'all' : 20, 'core' : 18},
          '10.1088/1367-2630/ab34e7' : {'all' : 20, 'core' : 17},
          '10.1088/1367-2630/11/4/045007' : {'all' : 20, 'core' : 17},
          '10.1088/0953-4075/43/21/215508' : {'all' : 20, 'core' : 17},
          '10.1209/epl/i2004-10203-9' : {'all' : 20, 'core' : 16},
          '10.1088/1751-8113/45/43/435301' : {'all' : 20, 'core' : 16},
          '10.1088/0953-4075/44/15/154013' : {'all' : 20, 'core' : 14},
          '10.1088/1367-2630/aba919' : {'all' : 20, 'core' : 13},
          '10.1088/1367-2630/18/9/093053' : {'all' : 20, 'core' : 13},
          '10.1088/1367-2630/11/4/045013' : {'all' : 19, 'core' : 18},
          '10.1088/1367-2630/11/2/023002' : {'all' : 19, 'core' : 17},
          '10.1088/2058-9565/abbc74' : {'all' : 19, 'core' : 16},
          '10.1088/1367-2630/17/11/113060' : {'all' : 19, 'core' : 16},
          '10.1088/1009-1963/14/5/006' : {'all' : 19, 'core' : 15},
          '10.1088/1367-2630/aab8e7' : {'all' : 19, 'core' : 14},
          '10.1088/1367-2630/11/1/013006' : {'all' : 19, 'core' : 14},
          '10.1088/0268-1242/12/12/001' : {'all' : 19, 'core' : 12},
          '10.1088/1367-2630/ab6f1f' : {'all' : 19, 'core' : 11},
          '10.1088/1367-2630/13/1/013043' : {'all' : 18, 'core' : 17},
          '10.1088/1367-2630/ab6cdd' : {'all' : 18, 'core' : 16},
          '10.1088/1367-2630/13/11/113042' : {'all' : 18, 'core' : 16},
          '10.1088/1367-2630/11/7/075006' : {'all' : 18, 'core' : 14},
          '10.1088/0953-4075/40/18/011' : {'all' : 18, 'core' : 13},
          '10.1088/1367-2630/18/10/103028' : {'all' : 17, 'core' : 17},
          '10.1088/1367-2630/ab2e26' : {'all' : 17, 'core' : 16},
          '10.1088/1367-2630/18/1/013020' : {'all' : 17, 'core' : 16},
          '10.1088/2632-2153/aba220' : {'all' : 17, 'core' : 15},
          '10.1088/2058-9565/ac22f6' : {'all' : 17, 'core' : 14},
          '10.1088/1367-2630/ab60f6' : {'all' : 17, 'core' : 14},
          '10.1088/0305-4470/34/47/329' : {'all' : 17, 'core' : 14},
          '10.1088/1367-2630/aa5fdb' : {'all' : 17, 'core' : 13},
          '10.1088/1751-8121/ab9d46' : {'all' : 17, 'core' : 11},
          '10.1088/1367-2630/abfc6a' : {'all' : 17, 'core' : 11},
          '10.1088/0953-4075/44/18/184016' : {'all' : 16, 'core' : 16},
          '10.1088/2058-9565/ac1e00' : {'all' : 16, 'core' : 15},
          '10.1088/1367-2630/aa5709' : {'all' : 16, 'core' : 15},
          '10.1088/1367-2630/aac9e7' : {'all' : 16, 'core' : 14},
          '10.1088/1367-2630/ab5ca2' : {'all' : 16, 'core' : 13},
          '10.1088/1367-2630/aac11a' : {'all' : 16, 'core' : 13}}

    
jnls = {'1538-3881': 'Astron.J.',
        '0004-637X': 'Astrophys.J.',
        '1538-4357': 'Astrophys.J.',
        '2041-8205': 'Astrophys.J.Lett.',
        '0067-0049': 'Astrophys.J.Supp.',
        '1538-4365': 'Astrophys.J.Supp.',
        '0264-9381': 'Class.Quant.Grav.',
        '1009-9271': 'Chin.J.Astron.Astrophys.',
        '0256-307X': 'Chin.Phys.Lett.',
        '0253-6102': 'Commun.Theor.Phys.',
        '0143-0807': 'Eur.J.Phys.',
        '0295-5075': 'EPL',
        '0266-5611': 'Inv.Problems',
        '1757-899X': 'IOP Conf.Ser.Mater.Sci.Eng.',
        '1742-6596': 'J.Phys.Conf.Ser.',
        '1475-7516': 'JCAP ',
        '1126-6708': 'JHEP ',
        '1748-0221': 'JINST ',
        '1742-5468': 'JSTAT ',
        '0957-0233': 'Measur.Sci.Tech.',
        '1367-2630': 'New J.Phys.',
        '0031-9120': 'Phys.Educ.',
        '1063-7869': 'Phys.Usp.',
        '0034-4885': 'Rept.Prog.Phys.',
        '1674-4527': 'Res.Astron.Astrophys.',
        '1402-4896': 'Phys.Scripta',
        '0953-2048': 'Supercond.Sci.Technol.',
        '2399-6528': 'J.Phys.Comm.',
        '1757-899X': 'IOP Conf.Ser.Mater.Sci.Eng.',
        '0036-0279': 'Russ.Math.Surveys',
        '0951-7715': 'Nonlinearity',
        '0953-4075': 'J.Phys.',
        '0953-8984': 'J.Phys.Condens.Matter',
        '0031-9155': 'Phys.Med.Biol.',
        '1538-3873': 'Publ.Astron.Soc.Pac.',
        '2399-6528': 'J.Phys.Comm.',
        '0741-3335': 'Plasma Phys.Control.Fusion',
        '2515-5172': 'Res.Notes AAS',
        '0026-1394': 'Metrologia'}
jnls['2516-1067'] = 'Plasma Res.Express'
jnls['2633-4356'] = 'Mat.Quant.Tech.'
jnls['1347-4065'] = 'Jap.J.Appl.Phys.'
jnls['2515-7647'] = 'JPhys Photon.'
jnls['2058-9565'] = 'Quantum Sci.Technol.'


jnls['1361-6633'] = 'Rept.Prog.Phys.' 
jnls['0305-4470'] = 'J.Phys.A'
jnls['1751-8113'] = 'J.Phys.A'
jnls['1742-5468'] = 'J.Phys.A'
jnls['1674-1056'] = 'Chin.Phys.B'
jnls['1674-1137'] = 'Chin.Phys.C'
jnls['1361-6455'] = 'J.Phys.B'
jnls['1464-4266'] = 'J.Opt.B'
jnls['1882-0786'] = 'Appl.Phys.Expr.'
jnls['1361-6668'] = 'Supercond.Sci.Technol.'
jnls['0022-3719'] = 'J.Phys.C'
jnls['0305-4608'] = 'J.Phys.F'
jnls['1751-8121'] = 'J.Phys.A'
jnls['0031-8949'] = 'Phys.Scripta'
jnls['0370-1298'] = 'Proc.Roy.Soc.Lond.A'
jnls['1355-5111'] = 'Quant.Opt.'
jnls['2632-2153'] = 'Mach.Learn.Sci.Tech.'
jnls['2633-1357'] = 'IOP SciNotes'
#jnls[''] = ''

driver.get('https://iopscience.iop.org/')
time.sleep(30)

i = 0
recs = []
missingjournals = []
print(sample)
for doi in list(sample.keys()):
    artlink = 'https://iopscience.iop.org/article/' + doi
    rec = {'doi' : doi, 'tc' : 'P'}
    i += 1
    ejlmod3.printprogress('-', [[i, len(sample)], [doi, sample[doi]['all'], sample[doi]['core']], [len(recs)]])
    if sample[doi]['core'] < corethreshold:
        print('   too, few citations')
        continue
    if skipalreadyharvested and doi in alreadyharvested:
        print('   already in backup')
        continue
    try:
        driver.get(artlink)
        artpage = BeautifulSoup(driver.page_source, features="lxml")
    except:
        print('try "%s" again after 1 minutes' % (artlink))
        time.sleep(60)
        driver.get(artlink)
        artpage = BeautifulSoup(driver.page_source, features="lxml")
    time.sleep(44)
    #jnl
    if re.search('^10.....\/\d\d\d\d\-\d\d\d.\/', doi):
        issn = doi[8:17]
        #print(issn)
        if issn in jnls:
            rec['jnl'] = jnls[issn]
        else:
            mi = doi
            for meta in artpage.find_all('meta', attrs = {'name' : 'citation_journal_title'}):
                mi += ' (%s)' % (meta['content'])
            missingjournals.append(mi)
            continue
    elif re.search('^10.1209\/epl\/', doi):
        rec['jnl'] = 'EPL'
    elif re.search('^10.1238\/Physica.Topical', doi):
        rec['jnl'] = 'Phys.Scripta'
    elif doi in ['10.1070/SM1967v001n04ABEH001994']:
        rec['jnl'] = 'Math.USSR Sb.'
    elif doi in ['10.1088/2632-2153/ab9a21']:
        rec['jnl'] = 'Mach.Learn.Sci.Tech.'
    else:
        mi = doi
        for meta in artpage.find_all('meta', attrs = {'name' : 'citation_journal_title'}):
            mi += ' (%s)' % (meta['content'])
        missingjournals.append(mi)
        continue
    #roboter check
    doimeta = artpage.find_all('meta', attrs = {'name' : 'citation_doi'})
    if not doimeta:
        print('\n !!! ROBO CHECK !!!\n')
        print('try "%s" again after 5 minutes' % (artlink))
        time.sleep(300)
        driver.get(artlink)
        artpage = BeautifulSoup(driver.page_source, features="lxml")
    autaff = False
    #licence
    for divl in artpage.body.find_all('div', attrs = {'class' : 'col-no-break wd-jnl-art-license media'}):
        for a in divl.find_all('a'):
            if a.has_attr('href'):
                if re.search('creativecommons.org', a['href']):
                    rec['licence'] = {'url' : a['href']}
    #metadata
    ejlmod3.metatagcheck(rec, artpage, ['citation_online_date', 'citation_issue', 'citation_doi',
                                        'citation_author', 'citation_author_institution', 'citation_author_orcid',
                                        'citation_author_email', 'citation_abstract', 'citation_reference',
                                        'citation_issue', 'citation_volume'])
    orcidsfound = False
    for meta in artpage.find_all('meta', attrs = {'name' : 'citation_author_orcid'}):
        orcidsfound = True
    if not 'date' in rec:
        ejlmod3.metatagcheck(rec, artpage, ['citation_publication_date'])
    for meta in artpage.find_all('meta'):
        if meta.has_attr('name'):
            if meta['name'] == 'citation_title':
                rec['tit'] = meta['content']
            elif meta['name'] == 'citation_volume':
                if issn in ['1674-1056', '0953-4075']:
                    rec['vol'] = 'B' + meta['content']
                elif issn == '1674-1137':
                    rec['vol'] = 'C' + meta['content']
                elif issn == '1751-8121':
                    rec['vol'] = 'A' + meta['content']
                elif issn == '0954-3899':
                    rec['vol'] = 'G' + meta['content']
                elif issn == '1361-6463':
                    rec['vol'] = 'D' + meta['content']
                else:
                    rec['vol'] = meta['content']
            elif meta['name'] == 'citation_firstpage':
                rec['p1'] = meta['content']
                if issn == '1748-0221' and rec['p1'][0] == 'C':
                    rec['tc'] = 'C'
    #JCAP
    if issn == '1475-7516':
        rec['vol'] = '%s%02i' % (rec['date'][2:4], int(rec['issue']))
        del rec['issue']
    if autaff:
        rec['autaff'].append(autaff)
    #authors if no ORCIDs in meta-section
    if not orcidsfound or not rec['autaff']:
        (auts, aff) = ([], [])
        for authorsection in artpage.body.find_all('span'):
            if authorsection.has_attr('data-authors'):
                break
        for span in authorsection.find_all('span', attrs = {'itemprop' : 'author'}):
            orcid = False
            affis = []
            for sup in span.find_all('sup'):
                affis = re.split(' *, *', sup.text)
                sup.replace_with('')
            author = re.sub('(.*) (.*)', r'\2, \1', span.text.strip())
            for a in span.find_all('a'):
                if a.has_attr('href') and re.search('orcid.org', a['href']):
                    orcid = re.sub('.*orcid.org\/(\d.*[\dX])', r'\1', a['href'])
            if orcid:
                auts.append('%s, ORCID:%s' % (author, orcid))
                orcidsfound = True
            else:
                auts.append(author)
            for affi in affis:
                auts.append('=Aff%s' % (affi))
        for diva in artpage.body.find_all('div', attrs = {'class' : 'wd-jnl-art-author-affiliations'}):
            for p in diva.find_all('p'):
                for sup in p.find_all('sup'):
                    affi = sup.text
                    sup.replace_with('Aff%s= ' % (affi))
                aff.append(p.text)
        if len(auts) >= len(rec['autaff']):
            del rec['autaff']
            rec['auts'] = auts
            rec['aff'] = aff
    #abstract
    for abstr in artpage.body.find_all('div', attrs = {'class' : 'article-text wd-jnl-art-abstract cf'}):
        rec['abs'] = abstr.text.strip()
    #keywords:
    for divk in artpage.body.find_all('div', attrs = {'class' : 'wd-jnl-aas-keywords'}):
        rec['keyw'] = []
        for a in divk.find_all('a'):
            rec['keyw'].append(a.text)
    #get rid of footnotes
    for ul in artpage.body.find_all('ul', attrs = {'class' : 'clear-list wd-content-footnotes'}):
        ul.replace_with('')

    #sample note
    rec['note'] = ['reharvest_based_on_refanalysis',
                   '%i citations from INSPIRE papers' % (sample[doi]['all']),
                   '%i citations from CORE INSPIRE papers' % (sample[doi]['core'])]
    ejlmod3.printrecsummary(rec)
    recs.append(rec)
    ejlmod3.writenewXML(recs[((len(recs)-1) // bunchsize)*bunchsize:], publisher, jnlfilename + '--%04i' % (1 + (len(recs)-1) // bunchsize), retfilename='retfiles_special')
    if missingjournals:
        print('\nmissing journals:', missingjournals, '\n')
    
