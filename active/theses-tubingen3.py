# -*- coding: utf-8 -*-
#harvest theses from Tubingen
#FS: 2020-04-27
#FS: 2023-03-15

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'U. Tubingen'
jnlfilename = 'THESES-TUBINGEN-%s' % (ejlmod3.stampoftoday())

startyear = str(ejlmod3.year(backwards=1))
rpp = 50
skipalreadyharvested = True

hdr = {'User-Agent' : 'Magic Browser'}

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []
    
recs = []
for fac in ['Physik', 'Sonstige+-+Mathematik+und+Physik', 'Mathematik', 'Informatik']:
    tocurl = 'https://publikationen.uni-tuebingen.de/xmlui/handle/10900/42126/discover?rpp=' + str(rpp) + '&filtertype_0=dateIssued&filtertype_1=fachbereich&filter_0=[' + startyear + '+TO+' + str(ejlmod3.year()+1) + ']&filter_relational_operator_1=equals&filter_1=' + fac + '&filter_relational_operator_0=equals&filtertype=type&filter_relational_operator=equals&filter=Dissertation'
    tocurl = 'https://publikationen.uni-tuebingen.de/xmlui/handle/10900/42126/discover?rpp=' + str(rpp) + '&filtertype_0=dateIssued&filtertype_1=fachbereich&filter_0=[' + startyear + '+TO+' + str(ejlmod3.year()+1) + ']&filter_relational_operator_1=equals&filter_1=' + fac + '&filter_relational_operator_0=equals&filtertype=type&filter_relational_operator=equals&filter=PhDThesis'
    
    ejlmod3.printprogress('=', [[fac], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features='lxml')
    for rec in ejlmod3.getdspacerecs(tocpage, 'https://publikationen.uni-tuebingen.de', alreadyharvested=alreadyharvested):
        if fac == 'Mathematik':
            rec['fc'] = 'm'
        if fac == 'Informatik':
            rec['fc'] = 'c'
        recs.append(rec)
    print('  %4i records so far' % (len(recs)))

for (i, rec) in enumerate(recs):
    ejlmod3.printprogress("-", [[i+1, len(recs)], [rec['link']]])
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
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'DC.contributor', 'DC.language', 'DC.identifier',
                                        'DC.title', 'DCTERMS.issued', 'DC.subject', 'DCTERMS.abstract',
                                        'citation_pdf_url'])
    rec['autaff'][-1].append(publisher)
    ejlmod3.printrecsummary(rec)
    

ejlmod3.writenewXML(recs, publisher, jnlfilename)
