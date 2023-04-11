# -*- coding: utf-8 -*-
#harvest theses from St. Andrews U.
#FS: 2022-10-27

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import ssl

publisher = 'St. Andrews U.'
jnlfilename = 'THESES-StAndrewsU-%s' % (ejlmod3.stampoftoday())

rpp = 20
pages = 1
skipalreadyharvested = True

#bad certificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
hdr = {'User-Agent' : 'Magic Browser'}

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

deps = [('28', 'm'), ('129', ''), ('60', 'c')]
recs = []
i = 0
for (dep, fc) in deps:
    for page in range(pages):
        tocurl = 'https://research-repository.st-andrews.ac.uk/handle/10023/' + dep + '/browse?rpp=' + str(rpp) + '&offset=' + str(page*rpp) + '&etal=-1&sort_by=2&type=type&value=Thesis&order=DESC'
        ejlmod3.printprogress('=', [[i*pages+page+1, len(deps)*pages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        for rec in ejlmod3.getdspacerecs(tocpage, 'https://research-repository.st-andrews.ac.uk/', alreadyharvested=alreadyharvested):
            if fc: rec['fc'] = fc
            recs.append(rec)
        print('  %4i records do far' % (len(recs)))
        time.sleep(10)
    i += 1

for (i, rec) in enumerate(recs):
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
    ejlmod3.metatagcheck(rec, artpage, ['citation_title', 'citation_author', 'citation_date',
                                        'DCTERMS.abstract', 'citation_pdf_url', 'DC.identifier'])
    rec['autaff'][-1].append(publisher)
    for tr in artpage.body.find_all('tr'):
        for td in tr.find_all('td', attrs = {'class' : 'label-cell'}):
            tdt = td.text.strip()
            td.decompose()
        for td in tr.find_all('td'):
            if td.text.strip() == 'en_US':
                continue
            #supervisor
            if tdt in ['dc.contributor.supervisor', 'dc.contributor.advisor']:
                sv = td.text.strip()
                if sv:
                    rec['supervisor'].append( [sv] )
            #pages
            elif tdt == 'dc.coverage.spatial':
                if re.search('\d\d', td.text):
                    rec['pages'] = re.sub('.*?(\d\d+).*', r'\1', td.text.strip())
            #keywords
            elif tdt == 'dc.subject.lcsh':
                if 'keyw' in rec:
                    rec['keyw'].append(td.text.strip())
                else:
                    rec['keyw'] = [td.text.strip()]
            #degree type
            elif tdt == 'dc.type.qualificationlevel':
                if td.text != 'Doctoral':
                    rec['note'].append(td.text.strip())
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
