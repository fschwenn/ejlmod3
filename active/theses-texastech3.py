# -*- coding: utf-8 -*-
#harvest theses from Texas Tech.
#FS: 2021-04-14
#FS: 2023-02-24

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Texas Tech.'
jnlfilename = 'THESES-TexasTech-%s' % (ejlmod3.stampoftoday())
departments = [('Applied+Physics', ''), ('Mathematical+Physics', 'm'), ('Mathematics', ''),
               ('Mathematics+and+Statistics', 'm'), ('Physics', ''), ('Science', ''),
               ('Computer+Science', 'c')]
rpp = 10
skipalreadyharvested = True
years = 2

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

hdr = {'User-Agent' : 'Magic Browser'}
recs = []
j = 0
for (department, fc) in departments:
    j += 1
    tocurl = 'https://ttu-ir.tdl.org/handle/2346/521/browse?type=department&value=' + department + '&sort_by=2&order=DESC&rpp=' + str(rpp)
    ejlmod3.printprogress("=", [[j, len(departments)], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    for rec in ejlmod3.getdspacerecs(tocpage, 'https://ttu-ir.tdl.org'):
        if skipalreadyharvested and rec['hdl'] in alreadyharvested:
            print('   %s already in backup' % (rec['hdl']))
        elif 'year' in rec and int(rec['year']) <= ejlmod3.year(backwards=years):
            print('   %s too old' % (rec['year']))
        else:
            rec['note'] = [ re.sub('\W', ' ', department) ]
            if fc: rec['fc'] = fc
            recs.append(rec)
    print('  %4i records so far' % (len(recs)))
    time.sleep(10)

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['link']]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link'] + '?show=full'), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link'] + '?show=full'))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link'] + '?show=full'), features="lxml")
        except:
            print("no access to %s" % (rec['link'] + '?show=full'))
            continue    
    ejlmod3.metatagcheck(rec, artpage, ['DC.title', 'DCTERMS.issued', 'DC.subject',
                                        'DCTERMS.abstract', 'citation_pdf_url'])
    #author
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
            if tht in ['dc.contributor.advisor', 'dc.contributor.committeeChair']:
                rec['supervisor'].append([td.text.strip()])
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
