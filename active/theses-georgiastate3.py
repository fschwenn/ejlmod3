# -*- coding: utf-8 -*-
#harvest theses from Georgia State U.
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

publisher = 'Georgia State U.'
jnlfilename = 'THESES-GeorgiaStateU-%s' % (ejlmod3.stampoftoday())
years = 2

#bad certificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
hdr = {'User-Agent' : 'Magic Browser'}
deps = [('math', 'm'), ('phy_astr', ''), ('cs', 'c')]
recs = []
i = 0
for (dep, fc) in deps:
    i += 1
    tocurl = 'https://scholarworks.gsu.edu/' + dep + '_diss/'
    ejlmod3.printprogress('=', [[i, len(deps)], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
    year = '9999'
    for div in tocpage.body.find_all('div', attrs = {'id' : 'series-home'}):
        for child in div.children:
            try:
                child.name
            except:
                continue
            if child.name:
                if child.name == 'h4':
                    for span in child.find_all('span'):
                        year = int(re.sub('.*([12]\d\d\d).*', r'\1', span.text.strip()))
                        print(year)
                    if year <= ejlmod3.year(backwards=years):
                        break
                elif child.name == 'p':
                    if child.has_attr('class') and 'article-listing' in child['class']:
                        for a in child.find_all('a'):
                            rec = {'tc' : 'T', 'jnl' : 'BOOK', 'year' : str(year), 'supervisor' : []}
                            rec['artlink'] = a['href']
                            if fc: rec['fc'] = fc
                            recs.append(rec)

for (i, rec) in enumerate(recs):
    ejlmod3.printprogress('-', [[i+1, len(recs)], [rec['artlink']]])
    try:
        req = urllib.request.Request(rec['artlink']+'?show=full', headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        time.sleep(3)
    except:
        try:
            print("   retry %s in 15 seconds" % (rec['artlink']))
            time.sleep(15)
            req = urllib.request.Request(rec['artlink']+'?show=full', headers=hdr)
            artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        except:
            print("   no access to %s" % (rec['artlink']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['bepress_citation_title', 'bepress_citation_pdf_url',
                                        'keywords', 'description', 'bepress_citation_author',
                                        'bepress_citation_doi'])
    #ORCID
    for div in artpage.find_all('div', attrs = {'id' : 'orcid'}):
        if re.search('Author ORCID ', div.text):
            for strong in div.find_all('strong'):
                rec['autaff'][-1].append('ORCID:' + strong.text.strip())
    rec['autaff'][-1].append(publisher)
    #supervisor
    for div in artpage.find_all('div', attrs = {'id' : ['advisor1', 'advisor2']}):
        for p in div.find_all('p'):
            rec['supervisor'].append([p.text.strip()])
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
