# -*- coding: utf-8 -*-
#harvest theses from College of William and Mary
#FS: 2019-10-29

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

numofpages = 2

publisher = 'Coll. William and Mary'
boring = ['Education', 'American Studies', 'Anthropology', 'Chemistry', 'History',
          'Virginia Institute of Marine Science', 'Biology', 'Psychology']
hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
jnlfilename = 'THESES-WM-%s' % (ejlmod3.stampoftoday())
for i in range(numofpages):
    if i == 0:
        tocurl = 'https://scholarworks.wm.edu/etd/index.html'
    else:
        tocurl = 'https://scholarworks.wm.edu/etd/index.%i.html' % (i+1)
    ejlmod3.printprogress('=', [[i+1, numofpages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    time.sleep(3)
    for p in tocpage.body.find_all('p', attrs = {'class' : 'article-listing'}):
        for a in p.find_all('a'):
            rec = {'tc' : 'T', 'jnl' : 'BOOK', 'note' : [], 'supervisor' : []}
            rec['artlink'] = a['href']
            if ejlmod3.ckeckinterestingDOI(rec['artlink']):
                prerecs.append(rec)

i = 0
recs = []
for rec in prerecs:
    keepit = True
    i += 1
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        time.sleep(10-3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['artlink']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        except:
            print("no access to %s" % (rec['artlink']))
            continue
    #license
    ejlmod3.metatagcheck(rec, artpage, ['bepress_citation_title', 'bepress_citation_date', 'description', 'bepress_citation_pdf_url'])
    for link in artpage.head.find_all('link', attrs = {'rel' : 'license'}):
        rec['license'] = {'url' : link['href']}
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #author
            if meta['name'] == 'bepress_citation_author':
                author = re.sub(' *\[.*', '', meta['content'])
                rec['autaff'] = [[ author ]]
                for div in artpage.body.find_all('div', attrs = {'id' : 'orcid'}):
                    for p in div.find_all('p'):
                        rec['autaff'][-1].append('ORCID:%s' % (re.sub('.*orcid.org\/', '', p.text.strip())))
                for meta2 in artpage.head.find_all('meta', attrs = {'name' : 'bepress_citation_author_institution'}):
                    rec['autaff'][-1].append(meta2['content']+', USA')

            #DOI
            elif meta['name'] == 'bepress_citation_doi':
                rec['doi'] = re.sub('.*org\/(10.*)', r'\1', meta['content'])
                rec['doi'] = re.sub('.*org\/doi:(10.*)', r'\1', rec['doi'])
            #typ of dissertation
            elif meta['name'] == 'bepress_citation_dissertation_name':
                disstyp = meta['content']
                if not re.search('octor', disstyp):
                    keepit = False
                    print('skip %s' % (disstyp))
    #department
    for div in artpage.body.find_all('div', attrs = {'id' : 'department'}):
        for p in div.find_all('p'):
            department = p.text
            if department in boring:
                keepit = False
            else:
                rec['note'].append(department)
    #supervisor
    for j in range(6):
        for div in artpage.body.find_all('div', attrs = {'id' : 'advisor%i' % (j+1)}):
            for h4 in div.find_all('h4'):
                if h4.text == 'Advisor':
                    for p in div.find_all('p'):
                        rec['supervisor'].append([p.text])
                elif h4.text != 'Committee Member':
                    print(h4.text)
    if keepit:
        recs.append(rec)
        ejlmod3.printrecsummary(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['artlink'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
