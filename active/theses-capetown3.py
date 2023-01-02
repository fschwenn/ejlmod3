# -*- coding: utf-8 -*-
#harvest theses from University of Cape Town
#FS: 2019-09-25
#FS: 2022-12-20

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Cape Town U.'
skipalreadyharvested = True
dokidir = '/afs/desy.de/user/l/library/dok/ejl/backup'

jnlfilename = 'THESES-CAPETOWN-%s' % (ejlmod3.stampoftoday())

hdr = {'User-Agent' : 'Magic Browser'}

alreadyharvested = []
def tfstrip(x): return x.strip()
if skipalreadyharvested:
    filenametrunc = re.sub('\d.*', '*doki', jnlfilename)
    alreadyharvested = list(map(tfstrip, os.popen("cat %s/*%s %s/%i/*%s | grep URLDOC | sed 's/.*=//' | sed 's/;//' " % (dokidir, filenametrunc, dokidir, ejlmod3.year(backwards=1), filenametrunc))))
    print('%i records in backup' % (len(alreadyharvested)))

recs = []
for dep in ['Department+of+Physics', 'Department+of+Mathematics+and+Applied+Mathematics', 'Department+of+Astronomy', 'Department+of+Maths+and+Applied+Maths', 'Department+of+Computer+Science']:
    tocurl = 'https://open.uct.ac.za/handle/11427/29121/discover?sort_by=dc.date.issued_dt&order=desc&rpp=10&filtertype=department&filter_relational_operator=equals&filter=' + dep
    print(tocurl)
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    for rec in ejlmod3.getdspacerecs(tocpage, 'https://open.uct.ac.za'):
        if dep == 'Department+of+Astronomy':
            rec['fc'] = 'a'
        elif dep in ['Department+of+Mathematics+and+Applied+Mathematics', 'Department+of+Maths+and+Applied+Maths']:
            rec['fc'] = 'm'
        elif dep in ['Department+of+Computer+Science']:
            rec['fc'] = 'c'
        if not rec['hdl'] in alreadyharvested:
            recs.append(rec)

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress('-', [[i, len(recs)], [rec['link']]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']+'?show=full'), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']+'?show=full'), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue    
    ejlmod3.metatagcheck(rec, artpage, ['DC.title', 'DCTERMS.issued', 'DCTERMS.abstract',
                                        'citation_pdf_url'])
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #author
            if meta['name'] == 'DC.creator':
                author = re.sub(' *\[.*', '', meta['content'])
                rec['autaff'] = [[ author ]]
                rec['autaff'][-1].append(publisher)
    if rec['hdl'] == '11427/32379':
        rec['date'] = '2020'
    #supervisor
    for tr in artpage.body.find_all('tr', attrs = {'class' : 'ds-table-row'}):
        for td in tr.find_all('td', attrs = {'class' : 'label-cell'}):
            if td.text.strip() == 'dc.contributor.advisor':
                td.decompose()
                for td2 in tr.find_all('td'):
                    tdt = td2.text.strip()
                    if tdt and tdt != 'en_ZA':
                        rec['supervisor'].append([tdt])
    ejlmod3.printrecsummary(rec)
ejlmod3.writenewXML(recs, publisher, jnlfilename)
