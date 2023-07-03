# -*- coding: utf-8 -*-
#harvest theses from Kansas State U.
#FS: 2020-02-10
#FS: 2023-02-20

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Kansas State U.'
pages = 40+60
skipalreadyharvested = True

rejectwords = []
for rejectword in ['Department of Adult Learning', 'Department of Agricultural', 'Department of Agronomy',
                   'Department of Anatomy', 'Department of Animal', 'Department of Apparel', 'Department of Bio',
                   'Department of Chemi', 'Department of Civil Engineering', 'Department of Communications Studies',
                   'Department of Curriculum and Instruction', 'Department of Diagnostic',
                   'Department of Diagnostic Medicine and Pathobiology', 'Department of Economics',
                   'Department of Educational', 'Department of Entomology', 'Department of Environmental Design',
                   'Department of Family', 'Department of Food', 'Department of Geography',
                   'Department of Grain Science', 'Department of History', 'Department of Horticulture',
                   'Department of Hospitality Managemen', 'Department of Human', 'Department of Industrial',
                   'Department of Kinesiology', 'Department of Landscape', 'Department of Mechanical',
                   'Department of Modern Languages', 'Department of Music', 'Department of Plant',
                   'Department of Plant Pathology', 'Department of Psycho', 'Department of Psychological',
                   'Department of Soci', 'Department of Sociology', 'Department of Special Education',
                   'Department of Statistics', 'Kansas Department of Transportation', 'Master of ']:
    rejectwords.append(re.compile(rejectword))

jnlfilename = 'THESES-KANSASSTATE-%s' % (ejlmod3.stampoftoday())

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

prerecs = []
hdr = {'User-Agent' : 'Magic Browser'}
for page in range(pages):
    tocurl = 'https://krex.k-state.edu/dspace/handle/2097/4/recent-submissions?offset=' + str(page*5)
    ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    time.sleep(5)
    for rec in ejlmod3.getdspacerecs(tocpage, 'https://krex.k-state.edu'):
        if skipalreadyharvested and rec['hdl'] in alreadyharvested:
            pass
        else:
            prerecs.append(rec)
    print('  %4i records so far' % (len(prerecs)))

i = 0
recs = []
for rec in prerecs:
    interesting = True
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(5)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    keepit = True
    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'citation_pdf_url', 'DCTERMS.abstract',
                                        'citation_title', 'citation_date', 'citation_keywords'])
    #thesis type
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'DC.description'}):
        rec['note'].append(meta['content'])
        if keepit:
            for rejectword in rejectwords:
                if rejectword.search(meta['content']):
                    keepit = False
                    break
    if keepit:
        rec['autaff'][-1].append(publisher)
        recs.append(rec)
        ejlmod3.printrecsummary(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['hdl'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
