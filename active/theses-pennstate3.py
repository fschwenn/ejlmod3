# -*- coding: utf-8 -*-
#harvest PennSate University theses
#FS: 2018-02-12
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

publisher = 'Penn State University'
rpp = 100

jnlfilename = 'THESES-PENNSTATE-%s' % (ejlmod3.stampoftoday())

recs = []
for (topic, fc) in [('Physics', ''), ('Computer+Science+and+Engineering', 'c'),
                    ('Mathematics', 'm'), ('Astronomy+and+Astrophysics', 'a')]:
    for year in [ejlmod3.year(), ejlmod3.year(backwards=1)]:
        tocurl = 'https://etda.libraries.psu.edu/?f%5Bdegree_name_ssi%5D%5B%5D=PHD&f%5Bprogram_name_ssi%5D%5B%5D=' + topic + '&f%5Byear_isi%5D%5B%5D=' + str(year) + '&per_page=' + str(rpp) + '&sort=year-desc'
        ejlmod3.printprogress('=', [[topic, year], [tocurl]])
        try:
            tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
            time.sleep(3)
        except:
            print("retry %s in 180 seconds" % (tocurl))
            time.sleep(180)
            tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
        for h3 in tocpage.body.find_all('h3', attrs = {'class' : 'document-title-heading'}):
            for a in h3.find_all('a'):
                rec = {'jnl' : 'BOOK', 'tc' : 'T', 'supervisor' : [], 'keyw' : [], 'note' : [topic], 'year' : str(year)}
                rec['link'] = 'https://etda.libraries.psu.edu' + a['href']
                rec['doi'] = '20.2000/PENNSTATE/%s' % (re.sub('\W', '', a['href']))
                rec['tit'] = a.text.strip()
                if fc:
                    rec['fc'] = fc
                recs.append(rec)
        print('  %4i records so far' % (len(recs)))

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress('-', [[i, len(recs)], [rec['link']]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(3)
    except:
        print("retry %s in 180 seconds" % (rec['link']))
        time.sleep(180)
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
    #fulltext
    for li in artpage.body.find_all('li', attrs = {'class' : 'download'}):
        for a in li.find_all('a'):
            if not a['href'] == '/login' and not re.search('feedback', a['href']):
                rec['FFT'] = 'https://etda.libraries.psu.edu' + a['href']
    if not 'FFT' in rec:
        for a in artpage.find_all('a', attrs = {'class' : 'file-link'}):
            rec['FFT'] = 'https://etda.libraries.psu.edu' + a['href']
    #author
    for dd in artpage.body.find_all('dd', attrs = {'class' : 'blacklight-author_name_tesi'}):
        rec['auts'] = [ dd.text.strip() ]
        rec['aff'] = [ 'Penn State U.' ]
    #supervisor
    for dd in artpage.body.find_all('dd', attrs = {'class' : 'blacklight-committee_member_and_role_tesim'}):
        for li in dd.find_all('li'):
            lit = li.text.strip()
            if re.search(', Dissertation Advisor', lit):
                rec['supervisor'].append([re.sub(', Dissertation Advisor.*', '', lit)])
    #keywords
    for dd in artpage.body.find_all('dd', attrs = {'class' : 'blacklight-keyword_ssim'}):
        for li in dd.find_all('li'):
            rec['keyw'].append(li.text.strip())
        if not rec['keyw']:
            for br in dd.find_all('br'):
                br.replace_with(';;;')
            rec['keyw'] = re.split(';;;', dd.text.strip())
    #abstract
    for dd in artpage.body.find_all('dd', attrs = {'class' : 'blacklight-abstract_tesi'}):
        rec['abs'] = dd.text.strip()
    ejlmod3.printrecsummary(rec)
ejlmod3.writenewXML(recs, publisher, jnlfilename)
