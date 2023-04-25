# -*- coding: utf-8 -*-
#program to harvest East Eur.J.Phys.
# FS 2022-10-25

import sys
import os
import ejlmod3
import re
import codecs
from bs4 import BeautifulSoup
import time
import undetected_chromedriver as uc

publisher = 'Karazim Univeristy'
issueid = sys.argv[1]

options = uc.ChromeOptions()
options.binary_location='/usr/bin/google-chrome'
options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

urltrunk = 'https://periodicals.karazin.ua/eejp/issue/view/' + issueid
print(urltrunk)

driver.get(urltrunk)
tocpage = BeautifulSoup(driver.page_source, features="lxml")

recs = []
for div in tocpage.body.find_all('div', attrs = {'class' : 'title'}):
    for a in div.find_all('a'):
        rec = {'jnl' : 'East Eur.J.Phys.', 'tc' : 'P', 'note' : []}
        rec['artlink'] = a['href']
        recs.append(rec)

for (i, rec) in enumerate(recs):
    driver.get(rec['artlink'])
    artpage = BeautifulSoup(driver.page_source, features="lxml")
    ejlmod3.printprogress('-', [[i+1, len(recs)], [rec['artlink']]])
    ejlmod3.metatagcheck(rec, artpage, ["DC.Description", "DC.Identifier.DOI", "DC.Rights", "DC.Title",
                                        "citation_author", "DC.Date.issued", "DC.Language",
                                        "citation_firstpage", "citation_lastpage",
                                        "citation_doi", "citation_keywords", "citation_pdf_url",
                                        "DC.Language", "DC.Title.Alternative", "citation_issue"])
    rec['vol'] = re.sub('.*(20\d\d).*', r'\1', rec['date'])    
    #in the beginning they had proper volumes
    rec['alternatejnl'] = rec['jnl']
    rec['alternateissue'] = rec['issue']
    rec['alternatep1'] = rec['p1']
    rec['alternatep2'] = rec['p2']
    rec['alternatevol'] = str(int(rec['vol'])-2013)
                              
    #ORCIDs are not in metatags :-(
    for ul in artpage.body.find_all('ul', attrs = {'class' : 'authors'}):
        rec['autaff'] = []
        for author in ul.find_all('li'):
            #name
            for span in author.find_all('span', attrs = {'class' : 'name'}):
                name = rec['autaff'].append([span.text.strip()])
            #ORCID
            for span in author.find_all('span', attrs = {'class' : 'orcid'}):
                for a in span.find_all('a'):
                    rec['autaff'][-1].append('ORCID:' + re.sub('.*\/', '', a['href']))
            #affiliation
            for span in author.find_all('span', attrs = {'class' : 'affiliation'}):
                rec['autaff'][-1].append(span.text.strip())
    #references
    for div in artpage.body.find_all('div', attrs = {'class' : 'item references'}):
        rec['refs'] = []
        for p in div.find_all('p'):
            rec['refs'].append([('x', p.text)])
    ejlmod3.printrecsummary(rec)
    time.sleep(5)
                
jnlfilename = 'eejp%s_%s.%s' % (issueid, rec['vol'], rec['issue'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
driver.quit()
