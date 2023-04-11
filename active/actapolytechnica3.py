# -*- coding: UTF-8 -*-
#program to harvest Acta Polytechnica (Prague)
# FS 2015-10-13
# FS 2023-04-04

import os
import ejlmod3
import re
import sys
#import unicodedata
#import string
import urllib.request, urllib.error, urllib.parse
import time
from bs4 import BeautifulSoup

ejldir = '/afs/desy.de/user/l/library/dok/ejl'

issuesstodo = 3

publisher = 'Czech Technical University in Prague'

#all issues page
url = 'https://ojs.cvut.cz/ojs/index.php/ap/issue/archive'
page = BeautifulSoup(urllib.request.urlopen(url), features="lxml")

issues = []
#for div in page.find_all('div', attrs = {'id' : 'issues'}):
for div in page.find_all('ul', attrs = {'class' : 'issues_archive'}):
    for h2 in div.find_all('h2')[:issuesstodo]:
        at = re.sub('[\n\t\r]', ' ', h2.text.strip())
        vol = re.sub('.*Vol\.? (\d+).*', r'\1', at)
        iss = re.sub('.*No\.? (\d+).*', r'\1', at)
        yr = re.sub('.*\((\d+)\).*', r'\1', at)
        for a in h2.find_all('a'):
            nr = re.sub('.*\/', '', a['href'])
            jnlfilename = re.sub(' ', '_', 'actapoly%s.%s_%s' % (vol, iss, nr))
            #check whether file already exists
            goahead = True
            for ordner in ['/', '/zu_punkten/', '/zu_punkten/enriched/', '/backup/', '/onhold/']:
                if os.path.isfile(ejldir + ordner + jnlfilename + '.doki'):
                    print('    Datei %s exisitiert bereit in %s' % (jnlfilename, ordner))
                    goahead = False
            if goahead:
                print('Will process Acta Polytechnica (Prague), Volume %s, Issue %s' % (vol, iss))
                issues.append((vol, iss, yr, a['href'], jnlfilename))
        
#issues = [('50', '3', '2010', 'https://ojs.cvut.cz/ojs/index.php/ap/issue/view/345', 'maybe_C09-05-05.1')]

#individual issues
for issue in issues:
    print(issue)
    page = BeautifulSoup(urllib.request.urlopen(issue[3]), features="lxml")
    jnlfilename = issue[4]
    recs = []    
#    for table in page.find_all('table', attrs = {'class' : 'tocArticle'}):
    for div in page.find_all('div', attrs = {'class' : 'obj_article_summary'}):
        rec = {'jnl' : 'Acta Polytech.', 'vol' : issue[0], 'year' : issue[2], 'issue' : issue[1], 'tc' : 'P',
               'keyw' : [], 'autaff' : []}
        for h3 in div.find_all('h3', attrs = {'class' : 'title'}):            
            for a in h3.find_all('a'):
                link = a['href']
                rec['tit'] = a.text
                artpage = BeautifulSoup(urllib.request.urlopen(link), features="lxml")
                ejlmod3.metatagcheck(rec, artpage, ['citation_keywords', 'citation_author', 'citation_author_institution',
                                                    'citation_date', 'citation_firstpage', 'citation_lastpage',
                                                    'citation_doi', 'DC.Description', 'citation_pdf_url'])
                ejlmod3.globallicensesearch(rec, artpage)
            recs.append(rec)
            ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
