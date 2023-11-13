# -*- coding: utf-8 -*-
#harvest journals from Royal Society of Chemistry
# FS: 2023-10-16

import sys
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import os
import undetected_chromedriver as uc

journal = sys.argv[1]
vol = sys.argv[2]
iss = sys.argv[3]
issuid = '%03i%03i' % (int(vol), int(iss))


publisher = 'Royal Society of Chemistry'

tc = 'P'
if journal == 'cp':
    jnl = 'Phys.Chem.Chem.Phys.'
    issn = '1463-9076'

jnlfilename = 'rsc_%s%s.%s' % (journal, vol, iss)

tocurl = 'https://pubs.rsc.org/en/journals/journalissues/' + journal + '#!issueid=' + journal + issuid + '&type=current&issnprint=' + issn
print(tocurl)

options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

try:
    driver.get(tocurl)
    time.sleep(5)
    tocpage = BeautifulSoup(driver.page_source, features="lxml")
except:
    time.sleep(120)
    driver.get(tocurl)
    time.sleep(5)
    tocpage = BeautifulSoup(driver.page_source, features="lxml")

recs = []
for div in tocpage.find_all('div', attrs = {'class' : 'capsule--article'}):
    rec = {'tc' : tc, 'jnl' : jnl, 'note' : [], 'vol' : vol, 'issue' : iss}
    keepit = True
    for span in div.find_all('span'):
        for a in span.find_all('a'):
            if a.has_attr('href') and re.search('doi.org\/10', a['href']):
                rec['doi'] = re.sub('.*doi.org\/', '', a['href'])
    for a in div.find_all('a', attrs = {'class' : 'capsule__action'}):
        if a.has_attr('href') and re.search('articlelanding', a['href']):
            rec['artlink'] = 'https://pubs.rsc.org' + a['href']
    #themed collection
    for div2 in div.find_all('div', attrs = {'class' : 'fixpadb--m'}):
        for a in div2.find_all('a'):
            rec['note'].append(a.text.strip())
    #article type
    for span in div.find_all('span', attrs = {'class' : 'capsule__context"'}):
        rec['note'].append(span.text.strip())    
    for h3 in div.find_all('h3', attrs = {'class' : 'capsule__title'}):
        title = h3.text.strip()
        if title in ['Front cover', 'Back cover', 'Editorial', 'Contents list',
                     'Inside back cover', 'Inside front cover']:
            keepit = False
        #print(keepit, title)
    if keepit:
        recs.append(rec)

for (i, rec) in enumerate(recs):
    ejlmod3.printprogress('-', [[i+1, len(recs)], [rec['artlink']]])
    time.sleep(10)
    try:
        driver.get(rec['artlink'])
        artpage = BeautifulSoup(driver.page_source, features="lxml")
    except:
        time.sleep(120)
        driver.get(rec['artlink'])
        artpage = BeautifulSoup(driver.page_source, features="lxml")
    ejlmod3. metatagcheck(rec, artpage, ['citation_title', 'citation_author', 'citation_author_institution',
                                         'citation_online_date', 'citation_volume', 'citation_issue',
                                         'citation_firstpage', 'citation_lastpage', 'citation_doi',
                                         'citation_reference', 'citation_abstract'])
    ejlmod3.globallicensesearch(rec, artpage)
    if 'license' in rec:
        ejlmod3. metatagcheck(rec, artpage, ['citation_pdf_url'])
#        print(artpage)
#        sys.exit(0)
    #year
    for meta in artpage.find_all('meta', attrs = {'name' : 'citation_publication_date'}):
        rec['year'] = re.sub('.*([12]\d\d\d).*', r'\1', meta['content'])
    #affiliations
    affs = {}
    for p in artpage.find_all('p', attrs = {'class' : 'article__author-affiliation'}):
        for sup in p.find_all('sup'):
            affkey = sup.text.strip()
            sup.decompose()
            affs[affkey] = re.sub(' *E.mail:.*', '',  re.sub('[\n\t\r]', ' ', p.text.strip()))
    #ORCIDs
    for div in artpage.find_all('div', attrs = {'class' : 'article__authors'}):
        autaff = []
        for span in div.find_all('span', attrs = {'class' : 'article__author-link'}):
            #name
            for a in span.find_all('a'):
                if a.has_attr('href') and re.search('searchtext=Author', a['href']):
                    autaff.append([re.sub('\n', ' ', a.text.strip())])
            #ORCID
            for a in span.find_all('a'):
                if a.has_attr('href') and re.search('orcid.org', a['href']):
                    autaff[-1].append(re.sub('.*orcid.org\/', 'ORCID:', a['href']))
            #affiliation
            for sup in span.find_all('sup'):
                for aff in sup.text.strip():
                    if aff in affs:
                        autaff[-1].append(affs[aff])
                    else:
                        print('   no affiliation with key "%s"' % (aff))
        if not rec['autaff'] or len(autaff) == len(rec['autaff']):
            rec['autaff'] = autaff
    #references
    for div in artpage.find_all('div', attrs = {'class' : 'ref-list'}):
        rec['refs'] = []
        for li in div.find_all('li'):            
            rdoi = False
            for a in li.find_all('a'):
                atext = a.text.strip()
                if atext == 'CrossRef':
                    rdoi = re.sub('.*doi.org\/', '', a['href'])
                    a.replace_with(', DOI: %s' % (rdoi))
                elif atext == 'RSC':
                    rdoi = re.sub('.*doi=(.*?)&.*', r'10.1039/\1', a['href'])
                    a.replace_with(', DOI: %s' % (rdoi))
                elif atext in ['CAS', 'Search PubMed', 'PubMed', 'Search PubMed', '??']:
                    a.decompose()
                elif re.search('^10\.\d+\/', atext):
                    rdoi = atext
                    a.decompose()
                else:
                    print('    reflink to %s??' % (atext))
            ref = [('x', re.sub('[\n\t\r]', ' ', li.text.strip()).strip())]
            if rdoi:
                ref.append(('a', 'doi:' + rdoi))
            rec['refs'].append(ref)

                    

    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename, retfilename='retfiles_special')


                   
