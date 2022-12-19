# -*- coding: utf-8 -*-
#harvest theses from Texas A&M
#FS: 2019-12-09
#FS: 2022-12-16


import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Texas A-M'
jnlfilename = 'THESES-TEXAS_AM-%s' % (ejlmod3.stampoftoday())

rpp = 100
years = 2

hdr = {'User-Agent' : 'Magic Browser'}
recs = []
departments = ['Physics', 'Physics+and+Astronomy', 'Mathematics', 'Computer+Science',
               'Computer+Science+%26+Engineering', 'Computer+Science+and+Engineering',
               'Computing+Science', 'Physics+and+Astronomy']
for (i, department) in enumerate(departments):
    tocurl = 'https://oaktrust.library.tamu.edu/handle/1969.1/2/browse?type=department&value=' + department + '&rpp=' + str(rpp) + '&etal=-1&sort_by=2&order=DESC'
    tocurl = 'https://oaktrust.library.tamu.edu/browse?rpp=' + str(rpp) + '40&offset=40&etal=-1&sort_by=2&type=department&value=' + department + '&order=DESC'
    ejlmod3.printprogress('=', [[i+1, len(departments)], [department], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    for rec in ejlmod3.getdspacerecs(tocpage, 'https://oaktrust.library.tamu.edu'):
        if department == 'Mathematics':
            rec['fc'] = 'm'
        elif department[:4] in ['Comp']:
            rec['fc'] = 'c'
        if 'year' in rec and int(rec['year']) <= ejlmod3.year(backwards=years):
            pass
        else:
            recs.append(rec)
    print('  %4i records so far' % (len(recs)))
    time.sleep(10)

i = 0
for (i, rec) in enumerate(recs):
    print('---{ %i/%i }---{ %s }------' % (i+1, len(recs), rec['link']))
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(4)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'DC.title', 'DCTERMS.issued',
                                        'DC.subject', 'DCTERMS.abstract', 'citation_pdf_url'])
    #license
    for a in artpage.find_all('a'):
        if a.has_attr('href') and re.search('creativecommons.org', a['href']):
            rec['license'] = {'url' : a['href']}
            if 'pdf_url' in list(rec.keys()):
                rec['FFT'] = rec['pdf_url']
            else:
                for div in artpage.find_all('div'):
                    for a2 in div.find_all('a'):
                        if a2.has_attr('href') and re.search('bistream.*\.pdf', a['href']):
                            divt = div.text.strip()
                            if re.search('Restricted', divt):
                                print(divt)
                            else:
                                rec['FFT'] = 'https://oaktrust.library.tamu.edu' + re.sub('\?.*', '', a['href'])
    ejlmod3.printrecsummary(rec)
                                    
ejlmod3.writenewXML(recs, publisher, jnlfilename)
