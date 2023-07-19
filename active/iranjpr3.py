# -*- coding: utf-8 -*-
#harvest Iran.J.Phys.Res.
#FS: 2023-07-17

import sys
import os
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Physics Society of Iran and the Isfahan University of Technology'
issuestocheck = 5 + 60
ejldir = '/afs/desy.de/user/l/library/dok/ejl'

options = uc.ChromeOptions()
options.binary_location='/usr/bin/google-chrome'
options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)
    

#check what is already done
reg = re.compile('.*iranjpr(\d+)\.(\d+).*')
issues = []
for directory in [ejldir+'/backup', ejldir+'/backup/' + str(ejlmod3.year(backwards=1))]:
    for datei in os.listdir(directory):
        if reg.search(datei):
            regs = reg.search(datei)
            vol = regs.group(1)
            issue = regs.group(2)
            if not (vol, issue) in issues:
                issues.append((vol, issue))
issues.sort()
print('done', issues)

#chec what is there
issuesurl = 'https://ijpr.iut.ac.ir/browse?_action=issue&lang=en'
todo = []
driver.get(issuesurl)
issuespage = BeautifulSoup(driver.page_source, features="lxml")
vol = '0'
i = 0
for div in issuespage.body.find_all('div'):
    if div.has_attr('class'):
        if 'title' in div['class']:
            for h3 in div.find_all('h3'):
                vol = re.sub('.*lume (\d+).*', r'\1', h3.text.strip())
                year = re.sub('.*([12]\d\d\d).*', r'\1', h3.text.strip())
                #print('vol', vol)
        if 'issueDetail' in div['class']:
            for a in div.find_all('a'):
                iss = re.sub('.*ssue (\d+).*', r'\1', a.text.strip())
                #print(' iss', iss)
                #print('    ', 'https://ijpr.iut.ac.ir/'+a['href'])
                if i < issuestocheck:
                    if not (vol, iss) in issues:
                        length = len(todo)+1
                        todo.append((length, vol, iss, year, 'https://ijpr.iut.ac.ir/'+a['href']))
                i += 1
print('todo', todo)

for (i, vol, iss, year, toclink) in todo:
    jnlfilename = 'iranjpr%s.%s' % (vol, iss)
    recs = []
    ejlmod3.printprogress('=', [[i, len(todo)], [toclink]])
    time.sleep(10)
    driver.get(toclink)
    tocpage = BeautifulSoup(driver.page_source, features="lxml")
    #get links to articles
    for article in tocpage.find_all('article', attrs = {'class' : 'article-summary'}):
        for h5 in article.find_all('h5'):
            for a in h5.find_all('a'):
                recs.append({'jnl' : 'Iran.J.Phys.Res.', 'vol' : vol, 'issue' : iss,
                             'artlink' : 'https://ijpr.iut.ac.ir/'+a['href'],
                             'tc' : 'P', 'year' : year,
                             'license' : {'statement' : 'CC-BY-NC'}})
    #check article pages
    for (j, rec) in enumerate(recs):
        ejlmod3.printprogress('-', [[i, len(todo)], [j+1, len(recs)], [rec['artlink']]])
        time.sleep(5)
        driver.get(rec['artlink'])
        artpage = BeautifulSoup(driver.page_source, features="lxml")
        ejlmod3.metatagcheck(rec, artpage, ['keywords', 'description', 'citation_title',
                                            'citation_author', 'citation_author_institution',
                                            'citation_publication_date',
                                            'citation_firstpage', 'citation_lastpage',
                                            'citation_doi', 'citation_pdf_url'])
        if  not 'doi' in rec:
            print('try again in 120s')
            time.sleep(120)            
            driver.get(rec['artlink'])
            artpage = BeautifulSoup(driver.page_source, features="lxml")
            ejlmod3.metatagcheck(rec, artpage, ['keywords', 'description', 'citation_title',
                                                'citation_author', 'citation_author_institution',
                                                'citation_publication_date',
                                                'citation_firstpage', 'citation_lastpage',
                                                'citation_doi', 'citation_pdf_url'])
        if 'keyw' in rec and len(rec['keyw']) == 1:
            rec['keyw'] = re.split(',', rec['keyw'][0])
        #references are sometimes not properly formatted
        ejlmod3.printrecsummary(rec)
    ejlmod3.writenewXML(recs, publisher, jnlfilename, retfilename='retfiles_special')
            
        

