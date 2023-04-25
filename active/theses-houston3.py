# -*- coding: utf-8 -*-
#harvest theses from Houston U.
#FS: 2019-12-09
#FS: 2023-04-18

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Houston U.'
jnlfilename = 'THESES-HOUSTON-%s' % (ejlmod3.stampoftoday())

rpp = 10
skipalreadyharvested = True

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []
    
hdr = {'User-Agent' : 'Magic Browser'}
recs = []
for department in ['Physics%2C+Department+of', 'Physics', 'Mathematics%2C+Department+of', 'Computer+Science%2C+Department+of']:
    tocurl = 'https://uh-ir.tdl.org/handle/10657/1/browse?type=department&value=' + department + '&sort_by=2&order=DESC&rpp=' + str(rpp)
    ejlmod3.printprogress('=', [[tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features='lxml')
    divs = tocpage.body.find_all('div', attrs = {'class' : 'artifact-description'})
    for rec in ejlmod3.getdspacerecs(tocpage, 'https://uh-ir.tdl.org', alreadyharvested=alreadyharvested):
        if department == 'Mathematics%2C+Department+of':
            rec['fc'] = 'm'
        elif department == 'Computer+Science%2C+Department+of':
            rec['fc'] = 'c'
        recs.append(rec)
    print('   %4i records so far' % (len(recs)))
    time.sleep(30)

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['link']]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features='lxml')
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features='lxml')
        except:
            print("no access to %s" % (rec['link']))
            continue    
    ejlmod3.metatagcheck(rec, artpage, ['DC.title', 'DCTERMS.issued', 'DC.subject',
                                        'DCTERMS.abstract', 'citation_pdf_url'])
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'DC.creator'}):
        if re.search('\d\d\d\d\-\d\d\d\d',  meta['content']):
            rec['autaff'][-1].append('ORCID:' + meta['content'])
        else:
            author = re.sub(' \d.*', '', re.sub(' *\[.*', '', meta['content']))
            rec['autaff'] = [[ author ]]
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
                                rec['FFT'] = 'https://uh-ir.tdl.org' + re.sub('\?.*', '', a['href'])

    for tr in artpage.find_all('tr', attrs = {'class' : 'ds-table-row'}):
        for td in tr.find_all('td', attrs = {'class' : 'label-cell'}):
            tht = td.text.strip()
        for td in tr.find_all('td', attrs = {'class' : 'word-break'}):
            #supervisor
            if tht == 'dc.contributor.advisor':
                rec['supervisor'].append([td.text.strip()])
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
