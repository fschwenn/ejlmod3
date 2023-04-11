# -*- coding: utf-8 -*-
#harvest theses Regina U.
#FS: 2021-12-21
#FS: 2023-03-29

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import ssl

publisher = 'Regina U.'
jnlfilename = 'THESES-REGINA-%s' % (ejlmod3.stampoftoday())

rpp = 50
skipalreadyharvested = True
pages = 2

boringdeps = ['Biochemistry', 'Biology', 'Clinical Psychology', 'Education',
              'Engineering - Electronic Systems', 'Engineering - Environmental Systems',
              'Engineering - Petroleum Systems', 'Experimental and Applied Psychology',
              'Geology', 'History', 'Interdisciplinary Studies', 'Public Policy',
              'Chemistry', 'Engineering - Industrial Systems', 'Engineering - Process Systems',
              'Geography', 'Kinesiology and Health Studies', 'Canadian Plains Studies',
              'Engineering - Software Systems', 'Psychology', 'Kinesiology', 'Media Studies',
              'Police Studies', 'olitical Science', 'Social Work']

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

#bad certificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
hdr = {'User-Agent' : 'Magic Browser'}

prerecs = []
for page in range(pages):
    tocurl = 'https://ourspace.uregina.ca/handle/10294/2900/discover?sort_by=dc.date.issued_dt&order=desc&rpp=' + str(rpp) + '&page=' + str(page+1)
    ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
    try:
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
    except:
        print(' try again in 20s...')
        time.sleep(20)
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
    prerecs += ejlmod3.getdspacerecs(tocpage,  'https://ourspace.uregina.ca', alreadyharvested=alreadyharvested)
    time.sleep(5)

i = 0
recs = []
for rec in prerecs:
    keepit = True
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        req = urllib.request.Request(rec['link'] + '?show=full', headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        time.sleep(4)
    except:
        try:
            print("   retry %s in 15 seconds" % (rec['link']))
            time.sleep(15)
            req = urllib.request.Request(rec['link'] + '?show=full', headers=hdr)
            artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        except:
            print("   no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'DC.title', 'citation_date' ,
                                        'DC.subject', 'DCTERMS.abstract', 'citation_pdf_url'])
    for tr in artpage.body.find_all('tr', attrs = {'class' : 'ds-table-row'}):
        (label, word) = ('', '')
        for td in tr.find_all('td', attrs = {'class' : 'label-cell'}): 
            label = td.text.strip()
        for td in tr.find_all('td', attrs = {'class' : 'word-break'}):
            word = td.text.strip()
        #supervisor
        if re.search('dc.contributor.advisor', label):
                rec['supervisor'].append([ word ])
        #department
        elif re.search('thesis.degree.discipline', label):
            if word in boringdeps:
                keepit = False
            else:
                rec['note'].append(word)

    #license
    ejlmod3.globallicensesearch(rec, artpage)
    if keepit:
        recs.append(rec)
        ejlmod3.printrecsummary(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['hdl'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
