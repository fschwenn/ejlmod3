# -*- coding: utf-8 -*-
#harvest theses from Harvard
#FS: 2020-01-14
#FS: 2023-03-14

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import undetected_chromedriver as uc

publisher = 'Harvard U. (main)'
jnlfilename = 'THESES-HARVARD-%s' % (ejlmod3.stampoftoday())

rpp = 20
numofpages = 1
skipalreadyharvested = True
departments = [('m', 'Mathematics'), ('', 'Physics'), ('a', 'Astronomy'), ('c', 'Computer+Science')]

options = uc.ChromeOptions()
options.binary_location='/opt/google/chrome/google-chrome'
options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
#driver = uc.Chrome(version_main=chromeversion, options=options)
driver = uc.Chrome( options=options)

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
for (fc, dep) in departments:
    for i in range(numofpages):
        tocurl = 'https://dash.harvard.edu/handle/1/4927603/browse?type=department&value=%s&rpp=%i&sort_by=2&type=dateissued&offset=%i&etal=-1&order=DESC' % (dep, rpp, i*rpp)
        ejlmod3.printprogress("-", [[dep], [i+1, numofpages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        time.sleep(10)
        for rec in ejlmod3.getdspacerecs(tocpage, 'https://dash.harvard.edu', fakehdl=True):
            if fc: rec['fc'] = fc
            prerecs.append(rec)
        print('  %4i records so far' % (len(prerecs)))
            
j = 0
recs = []
for rec in prerecs:
    j += 1
    ejlmod3.printprogress("-", [[j, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        driver.get(rec['link'])
        artpage = BeautifulSoup(driver.page_source, features="lxml")
    except:
        time.sleep(60)
        print('wait a minute')
        driver.get(rec['link'])
        artpage = BeautifulSoup(driver.page_source, features="lxml")
    time.sleep(5)
    #author
    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'DC.date', 'DCTERMS.abstract',
                                        'citation_pdf_url', 'citation_keywords'])
    for info in rec['infos']:
        if re.search('rft.author=.*%40', info):
            rec['autaff'][-1].append(re.sub('.*=(.*)%40(.*)', r'EMAIL:\1@\2', info))
        elif re.search('rft_id=\d\d\d\d\-\d\d\d\d\-', info):
            rec['autaff'][-1].append(re.sub('.*=', 'ORCID:', info))        
    rec['autaff'][-1].append(publisher)
    #URN
    keepit = True
    for meta in artpage.find_all('meta', attrs = {'name' : 'DC.identifier'}):
        if meta.has_attr('scheme'):
            if re.search('URI', meta['scheme']):
                rec['urn'] = re.sub('.*harvard.edu\/', '', meta['content'])
                if skipalreadyharvested and rec['urn'] in alreadyharvested:
                    keepit = False
                    print('  %s already in backup' % (rec['urn']))
                else:
                    rec['link'] = meta['content']
            else:
                rec['note'].append(meta['content'])
    if not 'urn' in list(rec.keys()):
        rec['doi'] = '20.2000/Harvard' + re.sub('.*\/', '', rec['link'])
    if keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
