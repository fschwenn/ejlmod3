# -*- coding: utf-8 -*-
#harvest theses from Digital Commons Network
#FS: 2018-02-12
#FS: 2023-04-28

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Digital Commons Network'
jnlfilename = 'THESES-DCN-%s' % (ejlmod3.stampoftoday())

skipalreadyharvested = True
years = 2

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

recs = []
for (dep, fc) in [('elementary-particles-and-fields-and-string-theory', 'pt'),
                  ('quantum-physics', 'k'),
                  ('nuclear', 'n'),
                  ('plasma-and-beam-physics', 'b')]:
    tocurl = 'http://network.bepress.com/explore/physical-sciences-and-mathematics/physics/' + dep + '/?facet=publication_type%3A%22Theses%2FDissertations%22&facet=publication_facet%3A%22Doctoral+Dissertations%22'
    ejlmod3.printprogress('=', [[tocurl], [len(recs)]])

    try:
        tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
        time.sleep(3)
    except:
        print("retry %s in 180 seconds" % (tocurl))
        time.sleep(180)
        tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")


    for div in tocpage.body.find_all('div', attrs = {'class' : 'hide floatbox'}):
        for h4 in div.find_all('h4'):
            for small in h4.find_all('small'):
                 rec = {'jnl' : 'BOOK', 'tc' : 'T'}
                 if fc:
                     rec['fc'] = fc
                 rec['auts'] = [ re.sub('^ *, *', '', small.text.strip()) ]
                 small.replace_with('')
                 rec['tit'] = h4.text.strip()
        for p in div.find_all('p'):
            pt = p.text.strip()
            if len(pt) > 2:
                rec['abs'] = pt
        for a in div.find_all('a', attrs = {'title' : 'Opens in new window'}):
            rec['link'] = a['href']
            print(' . ', rec['link'])
            rec['doi'] = '20.2000/DCN/' + re.sub('\W', '', a['href'][4:])
        #date
        for small in div.previous_sibling.previous_sibling.previous_sibling.previous_sibling.find_all('small', attrs = {'class' : 'pull-right'}):
            rec['date'] = re.sub('.*([12]\d\d\d).*', r'\1', small.text.strip())
            if int(rec['date']) > ejlmod3.year(backwards=years):
                if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
                    recs.append(rec)
                    ejlmod3.printrecsummary(rec)
                
    
ejlmod3.writenewXML(recs, publisher, jnlfilename)
