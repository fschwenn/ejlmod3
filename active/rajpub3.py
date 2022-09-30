# -*- coding: utf-8 -*-
#!/usr/bin/python
#program to harvest Khalsa Publications
# FS 2022-09-29

import sys
import os
import ejlmod3
import re
import urllib.parse
from bs4 import BeautifulSoup
import time

publisher = 'Khalsa Publications'

jnl = sys.argv[1]
issuenumber = sys.argv[2]

if jnl == 'jap':
    jnlname = 'J.Adv.Phys.'

tocurl = 'https://rajpub.com/index.php/%s/issue/view/%s' % (jnl, issuenumber)
print(tocurl)
try:
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
    time.sleep(3)
except:
    print("retry %s in 180 seconds" % (tocurl))
    time.sleep(180)
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")

recs = []
for div in tocpage.find_all('h3', attrs = {'class' : 'title'}):
    for a in div.find_all('a'):
        rec = {'jnl': jnlname, 'tc' : 'P', 'autaff' : [], 'keyw' : []}
        rec['tit'] = a.text.strip()
        rec['artlink'] = a['href']
        recs.append(rec)

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress('-', [[i, len(recs)], [rec['artlink']]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        time.sleep(3)
    except:
        print("retry %s in 180 seconds" % (rec['artlink']))
        time.sleep(180)
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'citation_author_institution', 'citation_date', 'citation_volume',
                                        'citation_issue', 'citation_doi', 'citation_keywords', 'citation_pdf_url',
                                        'DC.Description', 'DC.Rights', 'citation_firstpage', 'citation_lastpage'])
    #references
    for div in artpage.body.find_all('section', attrs = {'class' : 'item references'}):
        rec['refs'] = []
        for div2 in div.find_all('p'):
            for br in div2.find_all('br'):
                br.replace_with('_TRENNER_')
            div2t = re.sub('\. *\[(\d+)\] ', r'._TRENNER_[\1] ', div2.text)
            for ref in re.split('_TRENNER_', div2t):
                rec['refs'].append([('x', ref)])    
    ejlmod3.printrecsummary(rec)

if 'issue' in rec:
    jnlfilename = '%s%s.%s_%s' % (jnl, rec['vol'], rec['issue'], ejlmod3.stampoftoday())
else:
    jnlfilename = '%s%s_%s' % (jnl, rec['vol'], ejlmod3.stampoftoday())
                    
ejlmod3.writenewXML(recs, publisher, jnlfilename)
