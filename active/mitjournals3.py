# -*- coding: UTF-8 -*-
#!/usr/bin/python
#program to harvest De Gruyter journals
# FS 2016-01-04
# FS 2022-09-16

import os
import ejlmod3
import re
import sys
import urllib.request, urllib.error, urllib.parse
import time
from bs4 import BeautifulSoup
import undetected_chromedriver as uc


urltrunc = 'https://direct.mit.edu'
publisher = 'MIT Press'
skipalreadyharvested = True


journal = sys.argv[1]
vol = sys.argv[2]
iss = sys.argv[3]

options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium'
options.headless=True
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

jnlfilename = 'mit%s.%s.%s_%s' %  (journal, vol, iss, ejlmod3.stampoftoday())
if journal == 'neco':
    jnl = 'Neural Comput.'
tc = 'P'

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

    
tocurl = '%s/%s/issue/%s/%s' % (urltrunc, journal, vol, iss)
print(tocurl)

#tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
driver.get(tocurl)
tocpage = BeautifulSoup(driver.page_source, features="lxml")
recs = []
for div in tocpage.find_all('div', attrs = {'class' : 'section-container'}):
    for section in div.find_all('section'):
        h4note = False
        for h4 in section.find_all('h4'):
            h4note = h4.text.strip()
            ejlmod3.printprogress('=', [[h4note]])
        for div2 in section.find_all('div', attrs = {'class' : 'al-article-item-wrap'}):
            rec = {'tc' : tc, 'jnl' : jnl, 'vol' : vol, 'issue' : iss, 'note' : []}
            if h4note:
                rec['note'].append(h4note)
            for a in div2.find_all('a', attrs = {'class' : 'article-pdfLink'}):
                if a.has_attr('data-doi'):
                    rec['doi'] = a['data-doi']
            for h5 in div2.find_all('h5'):
                for a in h5.find_all('a'):
                    rec['artlink'] = urltrunc + a['href']
            if skipalreadyharvested and 'doi' in rec and rec['doi'] in alreadyharvested:
                print('  %s already in backup' % (rec['doi']))
            else:
                recs.append(rec)

for (i, rec) in enumerate(recs):
    ejlmod3.printprogress('-', [[i+1, len(recs)], [rec['artlink']]])
    time.sleep(10)
    #artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
    driver.get(rec['artlink'])
    artpage = BeautifulSoup(driver.page_source, features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'citation_author_email', 'citation_author_institution',
                                        'citation_author_orcid', 'citation_title', 'citation_firstpage',
                                        'citation_lastpage', 'citation_doi', 'citation_publication_date',
                                        'citation_reference', 'og:description'])
    ejlmod3.globallicensesearch(rec, artpage)
    if 'license' in rec:
        ejlmod3.metatagcheck(rec, artpage, ['citation_pdf_url'])
        #references in html are better
        for div in artpage.find_all('div', attrs = {'class' : 'ref-list'}):
            rec['refs'] = []
            print('    take references from html-code')
            for reference in div.find_all('div', attrs = {'class' : 'ref-content'}):
                for a in reference.find_all('a'):
                    ate = a.text.strip()
                    if ate in ['Google Scholar', 'PubMed', 'Crossref', 'Search ADS']:
                        a.decompose()
                rec['refs'].append([('x', reference.text.strip())]) 
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename, retfilename='retfiles_special')
