# -*- coding: utf-8 -*-
#harvest theses from Victoria U., Wellington
#FS: 2019-11-25
#FS: 2023-04-08

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import ssl

rpp = 20
numofpages = 5
skipalreadyharvested = True

publisher = 'Victoria U., Wellington'
jnlfilename = 'THESES-VICTORIA-%s' % (ejlmod3.stampoftoday())

boring = ['rft.contributor=School+of+Government', 'rft.contributor=Victoria+Management+School',
          'rft.contributor=School+of+Languages+and+Cultures',
          'rft.contributor=School+of+Biological+Sciences',
          'rft.contributor=New+Zealand+School+of+Music',
          'rft.contributor=School+of+Geography%2C+Environment+and+Earth+Sciences',
          'rft.contributor=School+of+Linguistics+and+Applied+Language+Studies',
          'rft.contributor=Centre+of+Building+Performance+Research',
          'rft.contributor=School+of+Social+and+Cultural+Studies',
          'rft.contributor=School+of+History%2C+Philosophy%2C+Political+Science+and+International+Relations',
          'rft.contributor=School+of+Architecture',
          'rft.contributor=Antarctic+Research+Centre',
          'rft.contributor=Centre+for+Accounting%2C+Governance+and+Taxation+Research',
          'rft.contributor=Centre+for+Applied+Cross-Cultural+Research',
          'rft.contributor=Engineering+at+Victoria',
          'rft.contributor=Graduate+School+of+Nursing%2C+Midwifery+and+Health',
          'rft.contributor=Institute+of+Policy+Studies',
          'rft.contributor=International+Institute+of+Modern+Letters',
          'rft.contributor=Macdiarmid+Institute+for+Advanced+Materials+and+Nanotechnology',
          'rft.contributor=Museum+and+Heritage+Studies',
          'rft.contributor=School+of+Accounting+and+Commercial+Law',
          'rft.contributor=School+of+Art+History%2C+Classics+and+Religious+Studies',
          'rft.contributor=School+of+Chemical+and+Physical+Sciences',
          'rft.contributor=School+of+Economics+and+Finance',
          'rft.contributor=School+of+Education+Policy+and+Implementation',
          'rft.contributor=School+of+Education',
          'rft.contributor=School+of+English%2C+Film%2C+Theatre+and+Media+Studies',
          'rft.contributor=School+of+Information+Management',
          'rft.contributor=School+of+Law',
          'rft.contributor=School+of+Management+%3A+Te+Kura+Whakahaere',
          'rft.contributor=School+of+Maori+Studies+%3A+Te+Kawa+a+M%C4%81ui',
          'rft.contributor=School+of+Marketing+and+International+Business',
          'rft.contributor=School+of+M%C4%81ori+Studies+%3A+Te+Kawa+a+M%C4%81ui',
          'rft.contributor=School+of+Psychology',
          'rft.contributor=Te+Kura+Maori',
          'rft.contributor=Wellington+School+of+Architecture']

#bad certificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

hdr = {'User-Agent' : 'Magic Browser'}
recs = []
for i in range(numofpages):
    tocurl = 'https://researcharchive.vuw.ac.nz/handle/10063/32/browse?rpp=%i&sort_by=2&type=dateissued&offset=%i&etal=-1&order=DESC' % (rpp, i*rpp)
    ejlmod3.printprogress("=", [[i+1, numofpages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
    time.sleep(2)
    for rec in ejlmod3.getdspacerecs(tocpage, 'https://researcharchive.vuw.ac.nz', alreadyharvested=alreadyharvested):
        keepit = True
        for inf in rec['infos']:
            if re.search('rft.contributor', inf):
                if inf in boring:
                    keepit = False
                else:
                    rec['note'].append(inf)
        if keepit:
            recs.append(rec)
    print('  %4i records so far' % (len(recs)))
            
j = 0
for rec in recs:
    j += 1
    ejlmod3.printprogress("-", [[j, len(recs)], [rec['link']]])
    req = urllib.request.Request(rec['link'])
    artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
    time.sleep(5)
    #author
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'DC.date', 'citation_date',
                                        'DCTERMS.abstract', 'DC.subject',
                                        'citation_pdf_url'])
    rec['autaff'][-1].append(publisher)
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
