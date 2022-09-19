# -*- coding: utf-8 -*-
#harvest theses from Hawaii
#FS: 2021-02-24
#FSL 2022-09-10

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import codecs
import time

publisher = 'Hawaii U.'
jnlfilename = 'THESES-HAWAII-%s' % (ejlmod3.stampoftoday())

rpp = 10

hdr = {'User-Agent' : 'Magic Browser'}
recs = []
for (dep, depnr, dephash, fc) in [('Astronomy', '772', '67c8d51f-97a4-4d45-8a69-8baeaacaeaf6', 'a'),
                                  ('Physics', '2136', '87248401-a4ae-4708-ad85-5240acfa10f4', ''),
                                  ('Mathematics', '2094', '6d94e5d9-ce7f-4e9a-9748-d8471bb2deba', 'm')]:
    tocurl = 'https://scholarspace.manoa.hawaii.edu/handle/10125/' + depnr + '/browse?type=dateissued&year=-1&month=-1&sort_by=2&order=DESC&rpp=' + str(rpp) + '&etal=0&submit_browse=Update'
    tocurl = ' https://scholarspace.manoa.hawaii.edu/browse/dateissued?scope=' + dephash + '&bbm.rpp=' + str(rpp) + '&bbm.sd=DESC'
    ejlmod3.printprogress('=', [[dep], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    for tr in tocpage.body.find_all('ds-item-search-result-list-element'):
        rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'autaff' : [], 'note' : [dep]}
        for a in tr.find_all('a', attrs = {'class' : 'item-list-title'}):
            rec['artlink'] = 'https://scholarspace.manoa.hawaii.edu' + a['href'] #+ '?show=full'
            if fc:
                rec['fc'] = fc
            recs.append(rec)
    time.sleep(7)

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress('-', [[i, len(recs)], [rec['artlink']]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['artlink']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        except:
            print("no access to %s" % (rec['artlink']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['citation_title', 'citation_author', 'citation_publication_date', 'citation_pdf_url', 'citation_keywords'])
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #author
            if meta['name'] == 'citation_abstract_html_url':
                if re.search('handle.net',  meta['content']):
                    rec['hdl'] = re.sub('.*net\/', '', meta['content'])
            #description
            elif meta['name'] == 'DC.description':
                rec['note'].append(meta['content'])
    if len(rec['autaff']) == 1:
        rec['autaff'][-1].append(publisher)
    #license
    ejlmod3.globallicensesearch(rec, artpage)
    for tr in artpage.find_all('tr'):
        for td in tr.find_all('td', attrs = {'class' : 'metadataFieldLabel'}):
            tdt = td.text.strip()
        for td in tr.find_all('td', attrs = {'class' : 'metadataFieldValue'}):
            #abstract
            if tdt == 'Abstract:':
                rec['abs'] = td.text.strip()
            #pages
            elif tdt == 'Pages/Duration:':
                if re.search('\d\d p', td.text):
                    rec['pages'] = re.sub('.*?(\d\d+) p.*', r'\1', td.text.strip())
   
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
