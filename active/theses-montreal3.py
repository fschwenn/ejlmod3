# -*- coding: utf-8 -*-
#harvest theses from Montreal
#FS: 2020-01-24
#FS: 2023-03-24

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import ssl

publisher = 'U. Montreal (main)'
jnlfilename = 'THESES-MONTREAL-%s' % (ejlmod3.stampoftoday())

startyear = ejlmod3.year(backwards=1)
skipalreadyharvested = True
rpp = 200

#bad certificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
hdr = {'User-Agent' : 'Magic Browser'}

hdr = {'User-Agent' : 'Magic Browser'}
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = 0

prerecs = []
for (fac, fc) in [('2949', 'm'), ('2990', ''), ('2958', 'c')]:
    tocurl = 'https://papyrus.bib.umontreal.ca/xmlui/handle/1866/' + fac + '/discover?filtertype=dateIssued&filter_relational_operator=equals&filter=[' + str(startyear) + '+TO+' + str(ejlmod3.year()) + ']&rpp=' + str(rpp)
  #  tocurl = 'https://papyrus.bib.umontreal.ca/xmlui/handle/1866/' + fac + '/discover?rpp=10&etal=0&group_by=none&page=2&sort_by=dc.date.issued_dt&order=desc&filtertype_0=dateIssued&filter_relational_operator_0=equals&filter_0=&rpp=' + str(rpp)
    ejlmod3.printprogress('=', [[fac], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features='lxml')
    for rec in ejlmod3.getdspacerecs(tocpage, 'https://papyrus.bib.umontreal.ca', alreadyharvested=alreadyharvested):
        if fc: rec['fc'] = fc
        prerecs.append(rec)
    print('  %4i records so far' % (len(prerecs)))

i = 0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        #artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features='lxml')
        req = urllib.request.Request(rec['link'], headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features='lxml')
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            #artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features='lxml')
            req = urllib.request.Request(rec['link'], headers=hdr)
            artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features='lxml')
        except:
            print("no access to %s" % (rec['link']))
            continue    
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'DC.contributor', 'DC.title',
                                        'DCTERMS.issued', 'DC.subject',
                                        'citation_pdf_url'])
    rec['autaff'][-1].append(publisher)
    #abstract
    for div in artpage.body.find_all('div', attrs = {'class' : 'simple-item-view-description'}):
        for h5 in div.find_all('h5'):
            if re.search('R.s.', h5.text) or re.search('Abstra', h5.text):
                h5.replace_with('')
                for div2 in  div.find_all('div', attrs = {'class' : 'spacer'}):
                    div2.replace_with('XXXSPACERXXX')
                abstract = re.split('XXXSPACERXXX', div.text.strip())
                #print len(abstract)                    
                rec['abs'] = ''.join(abstract[len(abstract)//2:])
    #degree
    for div in artpage.body.find_all('div', attrs = {'class' : 'simple-item-view-degreelevel'}):
        for h5 in div.find_all('h5'):
            h5.replace_with('')
            if div.text.strip() == "Doctoral":
                recs.append(rec)
                ejlmod3.printrecsummary(rec)
            else:
                print('skip', div.text.strip())
                ejlmod3.adduninterestingDOI(rec['hdl'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
