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

rpp = 20
years = 2
pages = 1
skipalreadyharvested = True
boring = ['B.S.', 'M.S', 'M.A.', 'Master of Science']

hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
departments = ['Mathematics', 'Physics+and+Astronomy', #'Physics', 
               'Computer+Science+%26+Engineering', #'Computing+Science', 
               'Computer+Science+and+Engineering']

dokidir = '/afs/desy.de/user/l/library/dok/ejl/backup'
alreadyharvested = []
def tfstrip(x): return x.strip()
if skipalreadyharvested:
    filenametrunc = re.sub('\d.*', '*doki', jnlfilename)
    alreadyharvested = list(map(tfstrip, os.popen("cat %s/*%s %s/%i/*%s  %s/%i/*%s | grep URLDOC | sed 's/.*=//' | sed 's/;//' " % (dokidir, filenametrunc, dokidir, ejlmod3.year(backwards=1), filenametrunc, dokidir, ejlmod3.year(backwards=2), filenametrunc))))
    print('%i records in backup' % (len(alreadyharvested)))

for (i, department) in enumerate(departments):
    for page in range(pages):
        tocurl = 'https://oaktrust.library.tamu.edu/handle/1969.1/2/browse?type=department&value=' + department + '&rpp=' + str(rpp) + '&etal=-1&sort_by=2&order=DESC'
        tocurl = 'https://oaktrust.library.tamu.edu/handle/1969.1/2/browse?rpp=' + str(rpp) + '&offset=' + str(rpp*page) + '&etal=-1&sort_by=2&type=department&value=' + department + '&order=DESC'
        ejlmod3.printprogress('=', [[i+1, len(departments)], [department], [page+1, pages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        for rec in ejlmod3.getdspacerecs(tocpage, 'https://oaktrust.library.tamu.edu'):
            if department == 'Mathematics':
                rec['fc'] = 'm'
            elif department[:4] in ['Comp']:
                rec['fc'] = 'c'
            elif 'degrees' in rec:
                if 'Astronomy' in rec['degrees']:
                    rec['fc'] = 'a'
            if 'year' in rec and int(rec['year']) <= ejlmod3.year(backwards=years):
                print('      %s too old (%s)' % (rec['hdl'], rec['year']))
            elif rec['hdl'] in alreadyharvested:
                print('      %s in backup' % (rec['hdl']))
            else:
                prerecs.append(rec)
        print('  %4i records so far' % (len(prerecs)))
        time.sleep(10)

recs = []
for (i, rec) in enumerate(prerecs):
    keepit = True
    ejlmod3.printprogress('-', [[i+1, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link'] + '?show=full'), features="lxml")
        time.sleep(4)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link'] + '?show=full'), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'DC.title', 'citation_date',
                                        'DC.subject', 'DCTERMS.abstract', 'citation_pdf_url'])
    rec['autaff'][-1].append(publisher)
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
    #degree
    for tr in artpage.find_all('tr'):
        for td in tr.find_all('td', attrs = {'class' : 'label-cell'}):
            label = td.text.strip()
            for td2 in tr.find_all('td', attrs = {'class' : 'word-break'}):
                if label == 'thesis.degree.name':
                    degree = td2.text.strip()
                    if degree in boring:
                        keepit = False
                    elif not degree in ['PhD', 'Doctor of Philosophy']:
                        rec['note'].append('DEGREE=' + degree)
    if keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['hdl'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
