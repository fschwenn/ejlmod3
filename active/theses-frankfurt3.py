# -*- coding: utf-8 -*-
#harvest theses from Frankfurt
#FS: 2019-09-15
#FS: 2022-09-24

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import codecs
import datetime
import time
import json

publisher = 'Goethe U., Frankfurt (main)'

jnlfilename = 'THESES-FRANKFURT-%s' % (ejlmod3.stampoftoday())
hdr = {'User-Agent' : 'Magic Browser'}
pages = 3
years = 2
rpp = 10
skipalreadyharvested = True
skipoldones = True

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

prerecs = []
for (institute, fc) in [('Physik', ''), ('Informatik', 'c'), ('Mathematik', 'm'),
                        ('Frankfurt+Institute+for+Advanced+Studies+(FIAS)', ''),
                        ('Informatik+und+Mathematik', 'cm'),
                        ('keine+Angabe+Institut', ''),
                        ('Helmholtz+International+Center+for+FAIR', '')]:
    for page in range(pages):
        tocurl = 'http://publikationen.ub.uni-frankfurt.de/solrsearch/index/search/searchtype/simple/query/%2A%3A%2A/browsing/true/doctypefq/doctoralthesis/start/' + str(page*rpp) + '/rows/10/institutefq/' + institute + '/sortfield/year/sortorder/desc'
        ejlmod3.printprogress('=', [[institute, page+1, pages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        time.sleep(3)
        for dt in tocpage.body.find_all('div', attrs = {'class' : 'results_title'}):
            for a in dt.find_all('a'):
                rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK'}
                rec['artlink'] = 'http://publikationen.ub.uni-frankfurt.de' + a['href']
                rec['tit'] = a.text.strip()
                if fc:
                    rec['fc'] = fc
                if skipoldones and ejlmod3.checknewenoughDOI(rec['artlink']):
                    prerecs.append(rec)
        print('   %4i records so far' % (len(prerecs)))


i = 0
recs = []
for rec in prerecs:
    i += 1
    time.sleep(3)
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    req = urllib.request.Request(rec['artlink'], headers=hdr)
    artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'DC.description', 'citation_pdf_url',
                                        'citation_language', 'DC.rights', 'citation_doi',
                                        'citation_keywords'])
    rec['autaff'][-1].append('Goethe U., Frankfurt (main)')
    #link
    if not 'doi' in rec:
        for meta in artpage.head.find_all('meta', attrs = {'name' : 'DC.Identifier'}):
            if re.search('http.*docId', meta['content']):
                rec['link'] = meta['content']
    for tr in artpage.body.find_all('tr'):
        for td in tr.find_all('td'):
            tdt = td.text.strip()
        for th in tr.find_all('th'):
            tht = th.text.strip()
            #supervisor
            if tht == 'Advisor:':
                rec['supervisor'] = [[ tdt, 'Goethe U., Frankfurt (main)' ]]
            #language
            elif tht == 'Language:':
                rec['language'] = tdt
            #date
            elif tht == 'Release Date:':
                rec['date'] = tdt
                if re.search('[12]\d\d\d', rec['date']):
                    rec['year'] = re.sub('.*([12]\d\d\d).*', r'\1', rec['date'])
            #number of pages
            elif tht in ['Pagenumber:', 'Page Number:']:
                rec['pages'] = re.sub('\D*(\d+).*', r'\1', tdt)
    if not skipalreadyharvested or not 'doi' in rec or not rec['doi'] in alreadyharvested:
        if skipoldones and 'year' in rec and int(rec['year']) <= ejlmod3.year(backwards=years):
            print('     skip "%s"' % (rec['year']))
            ejlmod3.addtoooldDOI(rec['artlink'])
        else:
            ejlmod3.printrecsummary(rec)
            recs.append(rec)
ejlmod3.writenewXML(recs, publisher, jnlfilename)

