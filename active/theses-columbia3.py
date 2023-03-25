# -*- coding: utf-8 -*-
#harvest theses from Columbia U. 
#FS: 2020-03-23


import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
import urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Columbia U.'
jnlfilename = 'THESES-COLUMBIA-%s' % (ejlmod3.stampoftoday())

rpp = 20
deps = ['Applied+Physics+and+Applied+Mathematics', 'Mathematics', 'Physics', 'Computer+Science']
skipalreadyharvested = True

hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
for dep in deps:
    tocurl = 'https://academiccommons.columbia.edu/search?f%5Bdegree_grantor_ssim%5D%5B%5D=%28%22Columbia+University%22+OR+%22Teachers+College%2C+Columbia+University%22+OR+%22Union+Theological+Seminary%22+OR+%22Mailman+School+of+Public+Health%2C+Columbia+University%22%29&f%5Bdegree_level_name_ssim%5D%5B%5D=Doctoral&f%5Bdepartment_ssim%5D%5B%5D=' + dep + '&f%5Bgenre_ssim%5D%5B%5D=Theses&per_page=' + str(rpp) + '&sort=Published+Latest'
    ejlmod3.printprogress('=', [[tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    time.sleep(2)
    for h3 in tocpage.body.find_all('h3', attrs = {'class' : 'index_title'}):
        for a in h3.find_all('a'):
            rec = {'tc' : 'T', 'jnl' : 'BOOK', 'note' : [], 'keyw' : [], 'supervisor' : []}
            rec['link'] = 'https://academiccommons.columbia.edu' + a['href']
            rec['note'].append(re.sub('\W', ' ', dep))
            if dep == 'Mathematics':
                rec['fc'] = 'm'
            elif dep == 'Computer+Science':
                rec['fc'] = 'c'
            prerecs.append(rec)

#check individual thesis pages
i = 0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    ejlmod3.globallicensesearch(rec, artpage)
    ejlmod3.metatagcheck(rec, artpage, ['citation_title', 'citation_author', 'citation_publication_date', 'citation_doi', 'citation_keywords', 'description', 'citation_pdf_url'])
    rec['autaff'][-1].append(publisher)
    #supervisor
    for dl in artpage.body.find_all('dl'):
        for child in dl.children:
            try:
                child.name
            except:
                continue
            if child.name == 'dt':
                dtt = child.text.strip()
            elif child.name == 'dd' and dtt == 'Thesis Advisors':
                rec['supervisor'].append([child.text.strip()])
    if not skipalreadyharvested or not 'doi' in rec or not rec['doi'] in alreadyharvested:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    
ejlmod3.writenewXML(recs, publisher, jnlfilename)
