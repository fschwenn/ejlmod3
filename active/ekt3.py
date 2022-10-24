# -*- coding: utf-8 -*-
#program to harvest Adv.Nucl.Phys.
# FS 2022-10-24

import sys
import os
import ejlmod3
import re
import codecs
from bs4 import BeautifulSoup
import time
import undetected_chromedriver as uc

publisher = 'National Documentation Centre'
typecode = 'C'
issueid = sys.argv[1]
cnum = False
if len(sys.argv) > 2: 
    cnum = sys.argv[2]

options = uc.ChromeOptions()
options.headless=True
options.binary_location='/usr/bin/chromium-browser'
options.add_argument('--headless')
driver = uc.Chrome(version_main=103, options=options)



urltrunk = 'https://eproceedings.epublishing.ekt.gr/index.php/hnps/issue/view/' + issueid
print(urltrunk)

driver.get(urltrunk)
tocpage = BeautifulSoup(driver.page_source, features="lxml")

note = ''
for  div in tocpage.body.find_all('div', attrs = {'class' : 'description'}):
    for p in div.find_all('p'):
        note += p.text.strip()

recs = []
for section in tocpage.body.find_all('section'):
    for h5 in section.find_all('h5'):
        sectiontitle = h5.text.strip()
        print(' -', sectiontitle)
        if not sectiontitle in ['Frontmatter', 'Backmatter']:
            for div in section.find_all('div', attrs = {'class' : 'card'}):
                for h6 in div.find_all('h6'):
                    for a in h6.find_all('a'):
                        rec = {'jnl' : 'Adv.Nucl.Phys.', 'tc' : typecode, 'note' : note}
                        rec['note'] = [note, sectiontitle]
                        rec['artlink'] = a['href']
                        if cnum: rec['cnum'] = cnum
                        recs.append(rec)

for (i, rec) in enumerate(recs):
    driver.get(rec['artlink'])
    artpage = BeautifulSoup(driver.page_source, features="lxml")
    ejlmod3.printprogress('-', [[i+1, len(recs)], [rec['artlink']]])
    ejlmod3.metatagcheck(rec, artpage, ["DC.Description", "DC.Identifier.DOI", "DC.Rights", "DC.Title",
                                        "citation_author", "citation_author_institution", "DC.Date.issued",
                                        "citation_volume", "citation_firstpage", "citation_lastpage",
                                        "citation_doi", "citation_keywords", "citation_pdf_url",
                                        "citation_reference", "citation_language"])
    #ORCIDs are not in metatags :-(
    for div in artpage.body.find_all('div', attrs = {'class' : 'authors'}):
        rec['autaff'] = []
        for author in div.find_all('div', attrs = {'class' : 'author'}):
            #name
            for strong in author.find_all('strong'):
                name = rec['autaff'].append([strong.text])
            #ORCID
            for orcid in author.find_all('div', attrs = {'class' : 'orcid'}):
                for a in orcid.find_all('a'):
                    rec['autaff'][-1].append('ORCID:' + re.sub('.*\/', '', a['href']))
            #affiliation
            for aff in author.find_all('div', attrs = {'class' : 'article-author-affilitation'}):
                rec['autaff'][-1].append(aff.text)
    ejlmod3.printrecsummary(rec)
    time.sleep(5)
                

if cnum:
    jnlfilename = 'advnuclphys%s_%s_%s' % (issueid, rec['vol'], cnum)
else:
    jnlfilename = 'advnuclphys%s_%s' % (issueid, rec['vol'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
driver.quit()
