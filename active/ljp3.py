# -*- coding: UTF-8 -*-
#program to harvest Lithuanian Journal of Physics
# FS 2020-12-05
# FS 2023-04-23

import os
import ejlmod3
import re
import sys
import urllib.request, urllib.error, urllib.parse
import time
from bs4 import BeautifulSoup

ejldir = '/afs/desy.de/user/l/library/dok/ejl'

issuesstocheck = 3

publisher = 'Lithuanian Academy of Sciences'

#all issues page
url = 'https://www.lmaleidykla.lt/ojs/index.php/physics/issue/archive'
page = BeautifulSoup(urllib.request.urlopen(url))

issues = []
#for div in page.find_all('div', attrs = {'id' : 'issues'}):
for div in page.find_all('ul', attrs = {'class' : 'issues_archive'}):
    for a in div.find_all('a')[:issuesstocheck]:
        at = a.text.strip()
        vol = re.sub('.*Vol\.? (\d+).*', r'\1', at)
        iss = re.sub('.*No\.? (\d+).*', r'\1', at)
        yr = re.sub('.*\((\d+)\).*', r'\1', at)
        nr = re.sub('.*\/', '', a['href'])
        jnlfilename = 'lithpj%s.%s_%s' % (vol, iss, nr)
        #check whether file already exists
        goahead = True
        for ordner in ['/', '/backup/', '/backup/%i/' % (ejlmod3.year(backwards=1))]:
            if os.path.isfile(ejldir + ordner + 'LABS_' + jnlfilename + '.doki') or os.path.isfile(ejldir + ordner + 'JSONL_' + jnlfilename + '.doki'):
                print('    Datei %s exisitiert bereit in %s' % (jnlfilename, ordner))
                goahead = False
        if goahead:
            print('Will process Lithuanian Journal of Physics, Volume %s, Issue %s' % (vol, iss))
            issues.append((vol, iss, yr, a['href'], jnlfilename))
        

#individual issues
for (j, issue) in enumerate(issues):
    ejlmod3.printprogress('=', [[j, len(issues)], issue])
    time.sleep(2)
    page = BeautifulSoup(urllib.request.urlopen(issue[3]), features="lxml")    
    jnlfilename = issue[4]
    recs = []    
#    for table in artpage.find_all('table', attrs = {'class' : 'tocArticle'}):
    divs = page.find_all('div', attrs = {'class' : 'obj_article_summary'})
    for (i, div) in enumerate(divs):
        rec = {'jnl' : 'Lith.J.Phys.', 'vol' : issue[0], 'year' : issue[2], 'issue' : issue[1], 'tc' : 'P',
               'keyw' : [], 'autaff' : []}
        for h3 in div.find_all('div', attrs = {'class' : 'title'}):            
            for a in h3.find_all('a'):
                link = a['href']
                ejlmod3.printprogress('-', [[j, len(issues)], [i+1, len(divs)], [link]])
                rec['tit'] = a.text
                artpage = BeautifulSoup(urllib.request.urlopen(link), features="lxml")
                time.sleep(2)
                ejlmod3.globallicensesearch(rec, artpage)
                ejlmod3.metatagcheck(rec, artpage, ['citation_keywords',  'citation_author',
                                                    'citation_author_institution', 'citation_date',
                                                    'citation_firstpage', 'citation_lastpage',
                                                    'citation_doi', 'DC.Description',
                                                    'citation_pdf_url'])
            recs.append(rec)
            ejlmod3.printrecsummary(rec)

    ejlmod3.writenewXML(recs, publisher, jnlfilename)
