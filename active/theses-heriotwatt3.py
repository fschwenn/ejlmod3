# -*- coding: utf-8 -*-
#harvest theses from Heriot-Watt U.
#FS: 2022-10-31

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import ssl

publisher = 'Heriot-Watt U.'
jnlfilename = 'THESES-HERIOTWATT-%s' % (ejlmod3.stampoftoday())

rpp = 50
pages = 2

#bad certificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
hdr = {'User-Agent' : 'Magic Browser'}
deps = ['31','37']
i = 0
recs = []
for dep in deps:
    for page in range(pages):
        tocurl = 'https://www.ros.hw.ac.uk/handle/10399/' + dep + '/browse?rpp=' + str(rpp) + '&offset=' + str(page*rpp) + '&etal=-1&sort_by=2&type=dateissued&starts_with=null&order=DESC'
        ejlmod3.printprogress('=', [[i*pages+page+1, len(deps)*pages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        recs += ejlmod3.getdspacerecs(tocpage, 'https://www.ros.hw.ac.uk')
        print('  %4i records do far' % (len(recs)))
        time.sleep(5)
    i += 1
    
for (i, rec) in enumerate(recs):
    if not ejlmod3.ckeckinterestingDOI(rec['link']):
        continue
    ejlmod3.printprogress('-', [[i+1, len(recs)], [rec['link']]])
    try:
        req = urllib.request.Request(rec['link']+'?show=full', headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        time.sleep(3)
    except:
        try:
            print("   retry %s in 15 seconds" % (rec['link']))
            time.sleep(15)            
            req = urllib.request.Request(rec['link']+'?show=full', headers=hdr)
            artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        except:
            print("   no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['citation_language', 'citation_author', 'citation_pdf_url',
                                        'citation_date', 'DCTERMS.abstract',
                                        'citation_title', 'DC.rights'])
    if 'abs' in rec:
        if re.search('Abstract.*(unavailable|not available)', rec['abs']):
            print('  del "%s"' % (rec['abs']))
            del(rec['abs'])
    rec['autaff'][-1].append(publisher)
    for tr in artpage.body.find_all('tr'):
        for td in tr.find_all('td', attrs = {'class' : 'label-cell'}):
            tdt = td.text.strip()
            td.decompose()
        for td in tr.find_all('td'):
            #supervisor
            if tdt in ['dc.contributor.supervisor', 'dc.contributor.advisor']:
                sv = td.text.strip()
                if sv:
                    rec['supervisor'].append( [sv] )
    ejlmod3.printrecsummary(rec)
        
ejlmod3.writenewXML(recs, publisher, jnlfilename)
