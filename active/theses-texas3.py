# -*- coding: utf-8 -*-
#harvest theses from Texas U.
#FS: 2019-12-09
#FS: 2022-09-10

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

publisher = 'Texas U.'

rpp = 50

hdr = {'User-Agent' : 'Magic Browser'}
for department in ['Physics', 'Mathematics']:
    tocurl = 'https://repositories.lib.utexas.edu/handle/2152/4/browse?type=department&value=' + department + '&sort_by=2&order=DESC&rpp=' + str(rpp)
    ejlmod3.printprogress('=', [[department], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    recs = []    
    recs = ejlmod3.getdspacerecs(tocpage, 'https://repositories.lib.utexas.edu/')
    time.sleep(30)

    i = 0
    for rec in recs:
        i += 1
        ejlmod3.printprogress('-', [[department], [i, len(recs)], [rec['link']]])
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
        ejlmod3.metatagcheck(rec, artpage, ['DC.title', 'DCTERMS.issued', 'DC.subject', 'DCTERMS.abstract', 'citation_pdf_url', 'DC.identifier'])
        if department == 'Mathematics':
            rec['fc'] = 'm'
        for meta in artpage.head.find_all('meta'):
            if meta.has_attr('name'):
                #author
                if meta['name'] == 'DC.creator':
                    if re.search('\d\d\d\d\-\d\d\d\d',  meta['content']):
                        rec['autaff'][-1].append('ORCID:' + meta['content'])
                    else:
                        author = re.sub(' *\[.*', '', meta['content'])
                        rec['autaff'] = [[ author ]]
        rec['autaff'][-1].append(publisher)
        ejlmod3.globallicensesearch(rec, artpage)
        ejlmod3.printrecsummary(rec)
    jnlfilename = 'THESES-TEXAS_U-%s_%s' % (ejlmod3.stampoftoday(), re.sub('\W', '', department))

    ejlmod3.writenewXML(recs, publisher, jnlfilename)
