# -*- coding: UTF-8 -*-
#!/usr/bin/python
#program to harvest journals from SIAM
# FS 2023-08-29
import os
import ejlmod3
import re
import sys
import undetected_chromedriver as uc
import time
from bs4 import BeautifulSoup

publisher = 'Society for Industrial and Applied Mathematics'
skipalreadyharvested = True

journal = sys.argv[1]
vol = sys.argv[2]
issues = re.split(',', sys.argv[3])

tc = 'P'
if journal == 'sjmaah':
    jnl = 'SIAM J.Math.Anal.'
elif journal == 'sjoce3':
    jnl = 'SIAM J.Sci.Comput.'
elif journal == 'siread':
    jnl = 'SIAM Rev.'
elif journal == 'smjcat':
    jnl = 'SIAM J.Comput.'
elif journal == 'smjmap':
    jnl = 'SIAM J.Appl.Math.'
elif journal == 'sjmael':
    jnl = 'SIAM J.Matrix Anal.Appl.'
elif journal == 'sjnaam':
    jnl = 'SIAM J.Numer.Anal.'
elif journal == 'sjdmec':
    jnl = 'SIAM J.Discrete Math.'
elif journal == 'sjaabq':
    jnl = 'SIAM J.Appl.Alg.Geom.'

if len(issues) == 1:
    jnlfilename = 'siam_%s%s.%s_%s' % (journal, vol, issues[0], ejlmod3.stampoftoday())
else:
    jnlfilename = 'siam_%s%s.%s-%s_%s' % (journal, vol, issues[0], issues[-1],  ejlmod3.stampoftoday())
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)


options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium'
#options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)
driver.implicitly_wait(300)

recs = []
dois = []
for (j, iss) in enumerate(issues):
    tocurl = 'https://epubs.siam.org/toc/%s/%s/%s' % (journal, vol, iss)
    ejlmod3.printprogress('=', [[j+1, len(issues)], [tocurl]])
    driver.get(tocurl)
    time.sleep(20)
    tocpage = BeautifulSoup(driver.page_source, features="lxml")
    banner = []
    #year
    for div in tocpage.body.find_all('div', attrs = {'class' : 'current-issue__meta text-center'}):
        for span in div.find_all('span', attrs = {'class' : 'cover-date'}):
            year = span.text.strip()
    for h2 in tocpage.body.find_all('h2', attrs = {'class' : 'banner-widget__subheading-item'}):
        banner.append(h2.text.strip())
        print(banner[-1])
        if re.search('(Proceedings|Conference|Workshop)', banner[-1]):
            tc = 'C'
            print('identified as proceedings')
    for section in tocpage.body.find_all('section', attrs = {'class' : 'table-of-content__section'}):
        h4t = False
        for h4 in section.find_all('h4', attrs = {'class' : 'toc__heading'}):
            h4t = h4.text.strip()
            print(h4t)
        for h3 in section.find_all('h3', attrs = {'class' : 'issue-item__title'}):
            for a in h3.find_all('a'):
                if a.has_attr('href'):
                    rec = {'tc' : tc, 'jnl' : jnl, 'vol' : vol, 'issue' : iss, 'note' : [], 'year' : year}
                    rec['doi'] = re.sub('.*doi\/', '', a['href'])
                    dois.append(rec['doi'])
                    print('  ', rec['doi'])
                    rec['tit'] = a.text.strip()
                    rec['artlink'] = 'https://epubs.siam.org' + a['href']
                    if banner:
                        rec['note'] += banner
                    if h4t:
                        rec['note'] += h4t
                        if re.search('SPECIAL SECTION STOC 20\d\d', h4t):
                            rec['tc'] = 'C'
                            if re.search('SPECIAL SECTION STOC 2022', h4t):
                                rec['cnum'] = 'C22-06-20.11'
                            elif re.search('SPECIAL SECTION STOC 2023', h4t):
                                rec['cnum'] = 'C23-06-20.2'
                    if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
                        if not rec['tit'] in ['Survey and Review', 'Research Spotlights',
                                              'Book Reviews', 'Education', 'SIGEST']:
                            recs.append(rec)
        
    for h3 in tocpage.body.find_all('h3', attrs = {'class' : 'issue-item__title'}):
        for a in h3.find_all('a'):
            if a.has_attr('href'):
                rec = {'tc' : tc, 'jnl' : jnl, 'vol' : vol, 'issue' : iss, 'note' : [], 'year' : year}
                rec['doi'] = re.sub('.*doi\/', '', a['href'])
                if not rec['doi'] in dois:
                    print(rec['doi'])
                    rec['tit'] = a.text.strip()
                    rec['artlink'] = 'https://epubs.siam.org' + a['href']
                    if banner:
                        rec['note'] += banner
                    if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
                        if not rec['tit'] in ['Survey and Review', 'Research Spotlights',
                                              'Book Reviews', 'Education', 'SIGEST']:
                            recs.append(rec)
    print('  %4i records so far' % (len(recs)))

for (i, rec) in enumerate(recs):
    oa = False
    ejlmod3.printprogress('-', [[i+1, len(recs)], [rec['artlink']]])    
    time.sleep(25)
    driver.get(rec['artlink'])
    artpage = BeautifulSoup(driver.page_source, features="lxml")
    #abstract
    ejlmod3.metatagcheck(rec, artpage, ['og:description'])
    #license
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            if meta['name'] == 'DC.Rights':
                if re.search('under the terms of the Creative Commons 4.0 license', meta['content']):
                    rec['license'] = {'statement' : 'CC-BY-4.0'}
                    oa = 'FFT'
                else:
                    rec['note'].append('DC.Rights:::' + meta['content'])
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
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)#, retfilename='retfiles_special')
