# -*- coding: utf-8 -*-
#harvest theses (with english titles) from Osaka U.
#FS: 2020-08-31
#FS: 2023-01-09

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import json

publisher = 'Osaka U. '

jnlfilename = 'THESES-OSAKA_U-%s' % (ejlmod3.stampoftoday())

rpp = 200
pages = 1
hdr = {'User-Agent' : 'Magic Browser'}

#first get links of year pages
masterurl = 'https://ir.library.osaka-u.ac.jp/repo/ouka/thesis/?lang=1'
req = urllib.request.Request(masterurl, headers=hdr)
masterpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
tocurls = {}
for div in masterpage.body.find_all('div', attrs = {'class' : 'menu_none'}):
    for a in div.find_all('a'):
        parts = re.split(' \/ ', a.text.strip())
        if len(parts) == 3:
            tocurl = 'https://ir.library.osaka-u.ac.jp/repo/ouka/thesis' + a['href'][1:] + '&disp_cnt=' + str(rpp)
            if parts[1] in list(tocurls.keys()):
                if parts[2] in list(tocurls[parts[1]].keys()):
                    if not tocurl in tocurls[parts[1]][parts[2]]:
                        tocurls[parts[1]][parts[2]].append(tocurl)
                else:
                    tocurls[parts[1]][parts[2]] = [tocurl]
            else:
                tocurls[parts[1]] = {parts[2] : [tocurl]}
time.sleep(1)

#check indiviual TOC for each year
recs = []
artlinks = []
for dep in ['Graduate School of Science']:
    for year in [str(ejlmod3.year()), str(ejlmod3.year(backwards=1))]:
        if dep in list(tocurls.keys()):
            if year in list(tocurls[dep].keys()):
                for tocurl in tocurls[dep][year]:
                    ejlmod3.printprogress("=", [[dep], [year], [tocurl]])
                    req = urllib.request.Request(tocurl, headers=hdr)
                    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
                    for div in tocpage.body.find_all('div', attrs = {'class' : 'row'}):
                        for p in div.find_all('p', attrs = {'class' : 'result-book-title'}):
                            for a in p.find_all('a'):
                                artlink = re.sub('.*\/all\/(.*)\/.*', r'https://ir.library.osaka-u.ac.jp/repo/ouka/all/\1/?lang=1', a['href'])
                                if not artlink in artlinks:
                                    artlinks.append(artlink)
                    print('  %4i records so far' % (len(artlinks)))
                    time.sleep(5)
i = 0
for artlink in artlinks:
    rec = {'tc' : 'T', 'jnl' : 'BOOK', 'keyw' : [], 'artlink' : artlink, 'auts' : []}
    i += 1
    ejlmod3.printprogress("-", [[i, len(artlinks)], [rec['artlink']]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['artlink']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']))
        except:
            print("no access to %s" % (rec['artlink']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['DC.language', 'citation_doi', 'DC.identifier', 'citation_date',
                                        'DC.subject', 'citation_pdf_url'])
    #title
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'citation_title'}):
        if not 'tit' in rec:
            rec['tit'] = meta['content']            
    #author
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'citation_author'}):
        if rec['auts']:
            if not re.search('CHINESENAME', rec['auts'][-1]):
                rec['auts'][-1] += ', CHINESENAME: ' + meta['content']
        else:
            rec['auts'] = [meta['content']]
        rec['aff'] = [publisher]
    #FFT
    for table in tocpage.body.find_all('table', attrs = {'class' : 'detailURL'}):
        for tr in table.find_all('tr'):
            for td in tr.find_all('td', attrs = {'class' : 'flintro'}):
                if re.search('Dissertation', td.text):
                    for td2 in tr.find_all('td', attrs = {'class' : 'filenm'}):
                        for a in td2.find_all('a'):
                            rec['hidden'] = re.sub('(.*)\/.*', r'\1', rec['artlink']) + a['href'][2:]    
    ejlmod3.printrecsummary(rec)
    ejlmod3.printrec(rec)
    recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
